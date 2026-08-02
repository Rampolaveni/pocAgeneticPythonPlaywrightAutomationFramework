# conftest.py

import pytest

from coreAgents.allureAgent import AllureAgent
from coreAgents.configAgent import ConfigAgent
from coreAgents.loggerAgent import LoggerAgent
from coreAgents.pathAgent import PathAgent
from coreAgents.runtimeAgent import RuntimeAgent
from coreAgents.testrailAgent import TestRailAgent

log = LoggerAgent.get_logger("conftest")


def to_bool(value: str) -> bool:
    """
    Converts command-line string value to boolean.

    Examples:
        "true"  -> True
        "false" -> False
    """

    return str(value).lower().strip() in ["true", "1", "yes", "y", "on"]


def pytest_addoption(parser):
    """
    Custom Pytest command-line options.

    Note:
    --browser and --headed are already provided by pytest-playwright.
    So we should not register them again.
    """

    parser.addoption(
        "--env",
        action="store",
        default="qa",
        choices=["qa", "uat", "prod"],
        help="Environment to run tests against: qa, uat, or prod",
    )

    parser.addoption(
        "--testrail",
        action="store",
        default="false",
        choices=["true", "false"],
        help="Publish results to TestRail: true or false",
    )

    parser.addoption(
        "--report",
        action="store",
        default="false",
        choices=["true", "false"],
        help="Generate automation report: true or false",
    )

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Sets Allure raw result path early.

    This is needed before Allure starts writing test result files.
    """

    report_enabled = str(
        config.getoption("report", default="false")
    ).lower() == "true"

    if not report_enabled:
        return

    config.option.allure_report_dir = str(PathAgent.ALLURE_RESULTS_DIR)

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """
    Starts Allure reporting session only when --report=true.

    This prepares allure-results before tests execute.
    """

    report_enabled = str(
        session.config.getoption("report", default="false")
    ).lower() == "true"

    if not report_enabled:
        return

    AllureAgent.prepare_allure_results()

    session.config.option.allure_report_dir = str(PathAgent.ALLURE_RESULTS_DIR)

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Final session teardown.

    Responsibilities:
    - generate consolidated Allure report when --report=true
    - publish TestRail results when --testrail=true
    """

    allure_report_link = None

    report_enabled = str(
        session.config.getoption("report", default="false")
    ).lower() == "true"

    if report_enabled:
        report_folder = AllureAgent.generate_html_report()

        if report_folder:
            allure_report_link = str(report_folder)
            log.info(f"Consolidated Allure report available at: {report_folder}")

    if TestRailAgent.is_enabled(session.config):
        TestRailAgent.publish_results(
            session=session,
            allure_report_link=allure_report_link,
        )

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Captures pytest result.

    Responsibilities:
    - stores test result for fixtures
    - attaches failure screenshot to Allure when --report=true
    - captures TestRail result when --testrail=true
    """

    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)

    report_enabled = str(
        item.config.getoption("report", default="false")
    ).lower() == "true"

    if report_enabled and report.failed and report.when in ["setup", "call"]:
        page = getattr(item, "runtime_page", None)

        screenshot_already_attached = getattr(
            item,
            "failure_screenshot_attached",
            False,
        )

        if page and not screenshot_already_attached:
            AllureAgent.attach_failure_screenshot(
                page=page,
                test_name=item.name,
            )

            setattr(item, "failure_screenshot_attached", True)

    if TestRailAgent.is_enabled(item.config):
        TestRailAgent.capture_result(
            item=item,
            report=report,
        )


@pytest.fixture(scope="session")
def configAgent(request):
    """
    Creates ConfigAgent for the current test execution.

    This fixture:
    - reads command-line values
    - creates ConfigAgent
    - applies runtime values
    - logs execution parameters
    """

    PathAgent.create_framework_directories()

    env_name = request.config.getoption("env")

    browser = request.config.getoption("browser")

    # pytest-playwright may return browser as list: ["chromium"]
    if isinstance(browser, list):
        browser = browser[0]

    headed = request.config.getoption("headed")
    test_type = request.config.getoption("markexpr") or "all"
    testrail_enabled = request.config.getoption("testrail")
    report_enabled = request.config.getoption("report")

    config_agent = ConfigAgent(env_name)

    config_agent.apply_runtime_values(
        browser=browser,
        headed=headed,
        test_type=test_type,
        testrail_enabled=to_bool(testrail_enabled),
        report_enabled=to_bool(report_enabled),
    )

    if config_agent.get_value("report_enabled"):
        AllureAgent.write_environment_file(config_agent)
        AllureAgent.write_executor_file()

    log.info("")
    log.info("============================== TEST PARAMETERS ===============================================")
    log.info(f"Environment      : {config_agent.get_value('env')}")
    log.info(f"Base URL         : {config_agent.get_value('base_url')}")
    log.info(f"Browser          : {config_agent.get_value('browser')}")
    log.info(f"Headed           : {config_agent.get_value('headed')}")
    log.info(f"Test Type        : {config_agent.get_value('test_type')}")
    log.info(f"TestRail Enabled : {config_agent.get_value('testrail_enabled')}")
    log.info(f"Report Enabled   : {config_agent.get_value('report_enabled')}")
    log.info(f"Log File         : {LoggerAgent.get_log_file_name()}")
    log.info("=============================================================================================")

    return config_agent


@pytest.fixture(scope="session")
def browserInstance(playwright, configAgent):
    """
    Launches browser once for the full test session.
    """

    browser_name = configAgent.get_value("browser")

    launch_options = {
        "headless": not configAgent.get_value("headed"),
        "slow_mo": configAgent.get_value("slow_mo"),
    }

    if browser_name == "chromium":
        browser = playwright.chromium.launch(**launch_options)

    elif browser_name == "firefox":
        browser = playwright.firefox.launch(**launch_options)

    elif browser_name == "webkit":
        browser = playwright.webkit.launch(**launch_options)

    else:
        raise ValueError(f"Invalid browser name: {browser_name}")

    yield browser

    browser.close()

    log.info("Browser closed successfully")




@pytest.fixture(scope="function")
def isolatedBrowserContext(browserInstance, configAgent):
    """
    Creates a fresh isolated Playwright browser context for each test.

    This is an internal framework fixture.
    """


    context = browserInstance.new_context(
        viewport=configAgent.get_value("viewport"),
        locale=configAgent.get_value("locale"),
        timezone_id=configAgent.get_value("timezone_id"),
        ignore_https_errors=configAgent.get_value("ignore_https_errors"),
        accept_downloads=configAgent.get_value("accept_downloads"),
    )

    yield context

    context.close()


@pytest.fixture(scope="function")
def browserPage(request, isolatedBrowserContext, configAgent):
    """
    Creates a new Playwright page for each test and opens application URL.

    This is an internal framework fixture.
    Test cases should use runtimeAgent, not browserPage directly.
    """

    test_name = request.node.name
    base_url = configAgent.get_value("base_url")
    timeout = configAgent.get_value("playwright_timeout")

    log.info(f"============================== TEST START: {test_name} ==============================")

    page = isolatedBrowserContext.new_page()
    request.node.runtime_page = page

    page.set_default_timeout(timeout)
    page.set_default_navigation_timeout(timeout)

    log.info(f"Opening URL: {base_url}")

    page.goto(
        base_url,
        wait_until="domcontentloaded",
        timeout=timeout,
    )

    yield page

    page.close()

    log.info(f"============================== TEST END: {test_name} ================================")
    log.info("")

@pytest.fixture(scope="function")
def runtimeAgent(browserPage, configAgent):
    """
    Creates RuntimeAgent for each test.

    This is the main fixture that test cases should use.
    """

    return RuntimeAgent(
        page=browserPage,
        config_agent=configAgent,
    )