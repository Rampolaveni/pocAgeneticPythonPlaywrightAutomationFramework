# coreAgents/testRailAgent.py

import os
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional

from coreAgents.loggerAgent import LoggerAgent


class TestRailAgent:
    """
    Handles TestRail integration.

    Responsibilities:
    - read TestRail configuration from environment variables
    - capture pytest results
    - create one TestRail run
    - publish all results to TestRail
    """

    BASE_URL = os.getenv("TESTRAIL_BASE_URL", "https://opencart.testrail.io").rstrip("/")
    USERNAME = os.getenv("TESTRAIL_USERNAME", "polaveniiram@gmail.com")
    API_KEY = os.getenv("TESTRAIL_API_KEY", "xwpVJnzd51bCanuVQvX6-5bFnq0sZrITCbdFeans/")

    PROJECT_ID = os.getenv("TESTRAIL_PROJECT_ID", "2")
    SUITE_ID = os.getenv("TESTRAIL_SUITE_ID", "")

    CLOSE_RUN_AFTER_EXECUTION = (
        os.getenv("TESTRAIL_CLOSE_RUN", "false").lower().strip() == "true"
    )

    INCLUDE_ALL_CASES = False

    STATUS_PASSED = 1
    STATUS_BLOCKED = 2
    STATUS_FAILED = 5

    TEST_RESULTS: List[Dict[str, Any]] = []

    log = LoggerAgent.get_logger("TestRailAgent")

    @classmethod
    def is_enabled(cls, config) -> bool:
        """
        Checks whether TestRail publishing is enabled from pytest option.
        """

        return str(
            config.getoption("testrail", default="false")
        ).lower().strip() == "true"

    @classmethod
    def get_build_identifier(cls) -> str:
        """
        Returns Jenkins build number when running from Jenkins.
        Returns Local Run when running locally.
        """

        build_number = os.getenv("BUILD_NUMBER", "").strip()

        if build_number:
            return f"Build #{build_number}"

        return "Local Run"

    @classmethod
    def validate_config(cls) -> bool:
        """
        Validates required TestRail environment variables.
        """

        missing_values = []

        if not cls.BASE_URL:
            missing_values.append("TESTRAIL_BASE_URL")

        if not cls.USERNAME:
            missing_values.append("TESTRAIL_USERNAME")

        if not cls.API_KEY:
            missing_values.append("TESTRAIL_API_KEY")

        if not cls.PROJECT_ID:
            missing_values.append("TESTRAIL_PROJECT_ID")

        if missing_values:
            cls.log.error(f"Missing TestRail configuration: {missing_values}")
            return False

        return True

    @classmethod
    def capture_result(cls, item, report) -> None:
        """
        Captures pytest result for TestRail.

        Captures:
        - passed
        - failed
        - skipped
        """

        if getattr(item, "testrail_result_captured", False):
            return

        if report.when == "setup" and report.failed:
            outcome = "failed"

        elif report.when == "call":
            outcome = report.outcome

        else:
            return

        case_id = cls.get_case_id(item)

        if not case_id:
            cls.log.warning(f"No TestRail case id found for test: {item.nodeid}")
            return

        result = {
            "case_id": case_id,
            "test_name": item.name,
            "nodeid": item.nodeid,
            "outcome": outcome,
            "duration": getattr(report, "duration", 0),
            "longrepr": str(report.longrepr) if report.failed else "",
        }

        cls.TEST_RESULTS.append(result)

        setattr(item, "testrail_result_captured", True)

        cls.log.info(
            f"Captured TestRail result | Case: C{case_id} | "
            f"Test: {item.name} | Outcome: {outcome}"
        )

    @classmethod
    def get_case_id(cls, item) -> Optional[int]:
        """
        Reads TestRail case id from pytest marker.

        Supported:
            @pytest.mark.testrail(case_id=123)
            @pytest.mark.testrail(123)
            @pytest.mark.testrail("C123")
        """

        marker = item.get_closest_marker("testrail")

        if not marker:
            return None

        case_id = marker.kwargs.get("case_id")

        if case_id is None and marker.args:
            case_id = marker.args[0]

        if case_id is None:
            return None

        case_id = str(case_id).upper().replace("C", "").strip()

        if not case_id.isdigit():
            raise ValueError(f"Invalid TestRail case id: {case_id}")

        return int(case_id)

    @classmethod
    def get_status_id(cls, outcome: str) -> int:
        """
        Maps pytest outcome to TestRail status id.
        """

        if outcome == "passed":
            return cls.STATUS_PASSED

        if outcome == "skipped":
            return cls.STATUS_BLOCKED

        return cls.STATUS_FAILED

    @classmethod
    def create_test_run(cls, session, allure_report_link: Optional[str] = None) -> Optional[int]:
        """
        Creates one TestRail run for the full automation execution.
        """

        browser = session.config.getoption("browser")

        if isinstance(browser, list):
            browser = browser[0]

        env_name = session.config.getoption("env")
        marker = session.config.getoption("markexpr") or "all"
        build_identifier = cls.get_build_identifier()

        timestamp = datetime.now().strftime("%Y-%m-%d")

        run_name = (
            f"OpenCart Automation {marker.title()} | "
            f"{env_name.upper()} | "
            f"{browser.title()} | "
            f"{build_identifier} | "
            f"{timestamp}"
        )

        case_ids = sorted(
            list({result["case_id"] for result in cls.TEST_RESULTS})
        )

        payload = {
            "name": run_name,
            "include_all": cls.INCLUDE_ALL_CASES,
            "case_ids": case_ids,
        }

        if cls.SUITE_ID:
            payload["suite_id"] = int(cls.SUITE_ID)

        response = cls.post_request(
            endpoint=f"add_run/{cls.PROJECT_ID}",
            payload=payload,
        )

        if not response:
            return None

        run_id = response.get("id")

        cls.log.info(f"TestRail run created successfully | Run ID: {run_id}")

        return run_id

    @classmethod
    def publish_results(cls, session, allure_report_link: Optional[str] = None) -> None:
        """
        Publishes all captured results to TestRail.
        """

        if not cls.is_enabled(session.config):
            cls.log.info("TestRail publishing skipped because --testrail=false")
            return

        if not cls.TEST_RESULTS:
            cls.log.warning("No TestRail results captured. Nothing to publish.")
            return

        if not cls.validate_config():
            cls.log.error("TestRail publishing skipped due to invalid configuration.")
            return

        run_id = cls.create_test_run(
            session=session,
            allure_report_link=allure_report_link,
        )

        if not run_id:
            cls.log.error("TestRail run creation failed. Results not published.")
            return

        for result in cls.TEST_RESULTS:
            cls.add_result_for_case(
                run_id=run_id,
                result=result,
                allure_report_link=allure_report_link,
            )

        if cls.CLOSE_RUN_AFTER_EXECUTION:
            cls.close_run(run_id)

        cls.log.info("TestRail result publishing completed successfully")

    @classmethod
    def add_result_for_case(
        cls,
        run_id: int,
        result: Dict[str, Any],
        allure_report_link: Optional[str] = None,
    ) -> None:
        """
        Adds result for one TestRail case.
        """

        status_id = cls.get_status_id(result["outcome"])

        comment = cls.build_comment(
            result=result,
            allure_report_link=allure_report_link,
        )

        payload = {
            "status_id": status_id,
            "comment": comment,
            "elapsed": cls.format_elapsed(result.get("duration", 0)),
        }

        cls.post_request(
            endpoint=f"add_result_for_case/{run_id}/{result['case_id']}",
            payload=payload,
        )

        cls.log.info(
            f"Published result to TestRail | Run: {run_id} | "
            f"Case: C{result['case_id']} | Outcome: {result['outcome']}"
        )

    @classmethod
    def build_comment(
        cls,
        result: Dict[str, Any],
        allure_report_link: Optional[str] = None,
    ) -> str:
        """
        Builds TestRail result comment.
        """

        comment = (
            f"Automation Test: {result['test_name']}\n"
            f"Pytest Node ID: {result['nodeid']}\n"
            f"Outcome: {result['outcome']}\n"
        )

        if allure_report_link:
            comment += f"\nAllure Report: {allure_report_link}\n"

        if result.get("longrepr"):
            comment += f"\nFailure/Error:\n{result['longrepr']}\n"

        return comment

    @classmethod
    def close_run(cls, run_id: int) -> None:
        """
        Closes TestRail run.
        """

        cls.post_request(
            endpoint=f"close_run/{run_id}",
            payload={},
        )

        cls.log.info(f"TestRail run closed successfully | Run ID: {run_id}")

    @classmethod
    def post_request(
        cls,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Sends POST request to TestRail API.
        """

        url = f"{cls.BASE_URL}/index.php?/api/v2/{endpoint}"

        try:
            response = requests.post(
                url=url,
                json=payload,
                auth=(cls.USERNAME, cls.API_KEY),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code >= 400:
                cls.log.error(f"TestRail API failed | Status: {response.status_code}")
                cls.log.error(f"Response: {response.text}")
                return None

            return response.json()

        except Exception as error:
            cls.log.error(f"TestRail API request failed | Endpoint: {endpoint}")
            cls.log.error(f"Error: {error}")
            return None

    @staticmethod
    def format_elapsed(duration: float) -> str:
        """
        Converts pytest duration into TestRail elapsed format.
        """

        seconds = int(duration)

        if seconds <= 0:
            return "1s"

        return f"{seconds}s"