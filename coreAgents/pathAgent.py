# coreAgents/pathAgent.py

from pathlib import Path


class PathAgent:
    """
    Central place for all framework paths.

    This avoids hardcoding paths in different files.
    """

    # Project root folder
    ROOT_DIR = Path(__file__).resolve().parents[1]

    # Main folders
    CONFIG_DIR = ROOT_DIR / "config"
    CORE_AGENTS_DIR = ROOT_DIR / "coreAgents"
    TESTS_DIR = ROOT_DIR / "tests"
    REPORTS_DIR = ROOT_DIR / "reports"

    # AI Agents
    AI_OUTPUTS_DIR = ROOT_DIR / "aiOutputs"
    TEST_PLANS_DIR = AI_OUTPUTS_DIR / "testPlans"
    GENERATED_CODE_DIR = AI_OUTPUTS_DIR / "generatedCode"
    HEALING_REPORTS_DIR = AI_OUTPUTS_DIR / "selfHealingReports"

    # Report folders
    LOGS_DIR = REPORTS_DIR / "logs"

    ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"
    ALLURE_REPORTS_DIR = REPORTS_DIR / "allure-reports"

    @classmethod
    def create_framework_directories(cls):
        """
        Creates required framework folders if they are missing.
        """

        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.ALLURE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        cls.AI_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEST_PLANS_DIR.mkdir(parents=True, exist_ok=True)
        cls.GENERATED_CODE_DIR.mkdir(parents=True, exist_ok=True)
        cls.HEALING_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_root_dir(cls) -> Path:
        return cls.ROOT_DIR

    @classmethod
    def get_reports_dir(cls) -> Path:
        return cls.REPORTS_DIR

    @classmethod
    def get_logs_dir(cls) -> Path:
        return cls.LOGS_DIR

    @classmethod
    def get_allure_results_dir(cls) -> Path:
        return cls.ALLURE_RESULTS_DIR

    @classmethod
    def get_allure_reports_dir(cls) -> Path:
        return cls.ALLURE_REPORTS_DIR