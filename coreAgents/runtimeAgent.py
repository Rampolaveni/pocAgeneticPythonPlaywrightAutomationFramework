# coreAgents/runtimeAgent.py

from typing import Any, Dict, Optional

from playwright.sync_api import Page

from coreAgents.actionAgent import ActionAgent
from coreAgents.configAgent import ConfigAgent
from dao.homePageDao import HomePageDAO
from dao.loginPageDao import LoginPageDAO
from dao.myAccountPageDao import MyAccountPageDAO
from dao.productPageDao import ProductPageDAO
from dao.registerPageDao import RegisterPageDAO


class RuntimeAgent:
    """
    Main test-facing framework object.

    RuntimeAgent represents everything available during one test execution.

    It holds:
    - Playwright Page object
    - ConfigAgent object
    - Current test data row later, for Excel/data-driven testing

    Later it can also hold:
    - ActionAgent
    - HomePageDAO
    - LoginPageDAO
    - MyAccountPageDAO
    """

    def __init__(self, page: Page, config_agent: ConfigAgent, test_name: str = "unknown_test"):
        """
        Creates RuntimeAgent for one test execution.
        """

        self.page = page
        self.config_agent = config_agent
        self.actionAgent = ActionAgent(self)
        self.test_name = test_name
        self.test_data = None
        self.actionAgent = ActionAgent(self)
        self.loginPageDao = LoginPageDAO(self)
        self.homePageDao = HomePageDAO(self)
        self.myAccountPageDao = MyAccountPageDAO(self)
        self.registerPageDao = RegisterPageDAO(self)
        self.productPageDao = ProductPageDAO(self)


    def get_page(self) -> Page:
        """
        Returns Playwright page object.
        """

        return self.page

    def get_config_agent(self) -> ConfigAgent:
        """
        Returns ConfigAgent object.
        """

        return self.config_agent

    def get_config(self) -> Dict[str, Any]:
        """
        Returns full runtime config as dictionary.
        """

        return self.config_agent.as_dict()

    def get_config_value(self, key_path: str) -> Any:
        """
        Gets config value using ConfigAgent.

        Examples:
            get_config_value("base_url")
            get_config_value("adminCredentials.valid_email")
            get_config_value("viewport.width")
        """

        return self.config_agent.get_value(key_path)
