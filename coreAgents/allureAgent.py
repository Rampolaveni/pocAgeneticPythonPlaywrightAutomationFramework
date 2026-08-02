# coreAgents/allureAgent.py

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import allure
from playwright.sync_api import Page

from coreAgents.loggerAgent import LoggerAgent
from coreAgents.pathAgent import PathAgent


class AllureAgent:
    """
    Handles Allure reporting.

    Responsibilities:
    - prepare one consolidated allure-results folder
    - write environment details
    - write executor details
    - attach screenshots directly to Allure report
    - generate one consolidated HTML report after execution
    - keep only latest 10 HTML reports
    """

    MAX_REPORTS_TO_KEEP = 5

    log = LoggerAgent.get_logger("AllureAgent")

    @classmethod
    def prepare_allure_results(cls) -> None:
        """
        Cleans and recreates allure-results before test execution.

        This is called only when --report=true.
        """

        if PathAgent.ALLURE_RESULTS_DIR.exists():
            shutil.rmtree(PathAgent.ALLURE_RESULTS_DIR)

        PathAgent.ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        cls.log.info(f"Allure results folder prepared: {PathAgent.ALLURE_RESULTS_DIR}")

    @classmethod
    def write_environment_file(cls, config_agent) -> None:
        """
        Writes environment.properties file inside allure-results.
        """

        environment_file = PathAgent.ALLURE_RESULTS_DIR / "environment.properties"

        environment_data = {
            "Environment": config_agent.get_value("env"),
            "Base URL": config_agent.get_value("base_url"),
            "Browser": config_agent.get_value("browser"),
            "Headed": config_agent.get_value("headed"),
            "Test Type": config_agent.get_value("test_type"),
        }

        with open(environment_file, "w", encoding="utf-8") as file:
            for key, value in environment_data.items():
                file.write(f"{key}={value}\n")

        cls.log.info(f"Allure environment file created: {environment_file}")

    @classmethod
    def write_executor_file(cls) -> None:
        """
        Writes executor.json file inside allure-results.
        """

        executor_file = PathAgent.ALLURE_RESULTS_DIR / "executor.json"

        executor_data = {
            "name": "Local Pytest Execution",
            "type": "pytest",
            "buildName": "OpenCart Automation Framework",
            "reportName": "OpenCart Automation Report",
        }

        with open(executor_file, "w", encoding="utf-8") as file:
            json.dump(executor_data, file, indent=4)

        cls.log.info(f"Allure executor file created: {executor_file}")

    @classmethod
    def attach_screenshot(
        cls,
        page: Page,
        screenshot_name: str = "Screenshot",
        full_page: bool = True,
    ) -> bool:
        """
        Captures screenshot and attaches it directly to Allure report.

        No screenshot folder is created.
        No screenshot file is saved locally.
        """

        try:
            clean_name = cls._clean_attachment_name(screenshot_name)

            screenshot_bytes = page.screenshot(
                full_page=full_page,
                type="png",
            )

            allure.attach(
                screenshot_bytes,
                name=clean_name,
                attachment_type=allure.attachment_type.PNG,
            )

            cls.log.info(f"Screenshot attached to Allure: {clean_name}")

            return True

        except Exception as error:
            cls.log.error(f"Failed to attach screenshot to Allure: {error}")
            return False

    @classmethod
    def attach_failure_screenshot(
        cls,
        page: Page,
        test_name: str,
    ) -> bool:
        """
        Attaches failure screenshot directly to Allure report.
        """

        return cls.attach_screenshot(
            page=page,
            screenshot_name=f"Failure Screenshot - {test_name}",
            full_page=True,
        )

    @classmethod
    def generate_html_report(cls) -> Optional[Path]:
        """
        Generates one consolidated Allure HTML report after all tests finish.
        Works reliably on Windows by resolving allure.cmd.
        """

        if not PathAgent.ALLURE_RESULTS_DIR.exists():
            cls.log.warning("Allure results folder does not exist. Report not generated.")
            return None

        allure_command = cls._get_allure_command()

        if not allure_command:
            cls.log.error("Allure commandline is not installed or not added to PATH.")
            cls.log.error("Run this in terminal to verify: allure --version")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_folder = PathAgent.ALLURE_REPORTS_DIR / f"allure_report_{timestamp}"

        command = [
            allure_command,
            "generate",
            str(PathAgent.ALLURE_RESULTS_DIR),
            "-o",
            str(report_folder),
        ]

        try:
            cls.log.info("Generating consolidated Allure HTML report")
            cls.log.info(f"Resolved Allure command: {allure_command}")
            cls.log.info(f"Command: {' '.join(command)}")

            subprocess.run(
                command,
                cwd=str(PathAgent.ROOT_DIR),
                check=True,
                capture_output=True,
                text=True,
            )

            cls.log.info(f"Consolidated Allure HTML report generated: {report_folder}")

            cls.cleanup_old_reports()

            return report_folder

        except subprocess.CalledProcessError as error:
            cls.log.error("Allure HTML report generation failed")
            cls.log.error(f"STDOUT: {error.stdout}")
            cls.log.error(f"STDERR: {error.stderr}")
            return None

        except Exception as error:
            cls.log.error(f"Unexpected error while generating Allure report: {error}")
            return None

    @classmethod
    def _get_allure_command(cls) -> Optional[str]:
        """
        Resolves Allure commandline executable.

        On Windows, npm/scoop usually exposes allure as allure.cmd.
        Python subprocess may not resolve it the same way PowerShell does.
        """

        possible_commands = [
            "allure.cmd",
            "allure.bat",
            "allure.exe",
            "allure",
        ]

        for command in possible_commands:
            resolved_command = shutil.which(command)

            if resolved_command:
                return resolved_command

        return None

    @classmethod
    def cleanup_old_reports(cls) -> None:
        """
        Keeps only latest 10 Allure HTML report folders.
        Deletes older reports.
        """

        if not PathAgent.ALLURE_REPORTS_DIR.exists():
            return

        report_folders = [
            folder
            for folder in PathAgent.ALLURE_REPORTS_DIR.iterdir()
            if folder.is_dir() and folder.name.startswith("allure_report_")
        ]

        report_folders.sort(
            key=lambda folder: folder.stat().st_mtime,
            reverse=True,
        )

        old_reports = report_folders[cls.MAX_REPORTS_TO_KEEP:]

        for report_folder in old_reports:
            try:
                shutil.rmtree(report_folder)
                cls.log.info(f"Old Allure report deleted: {report_folder}")

            except Exception as error:
                cls.log.error(f"Failed to delete old Allure report: {report_folder}")
                cls.log.error(f"Reason: {error}")

    @staticmethod
    def _clean_attachment_name(name: str) -> str:
        """
        Cleans attachment name for Allure.
        """

        clean_name = re.sub(r"[^A-Za-z0-9_ .:-]+", "_", name)
        return clean_name.strip()