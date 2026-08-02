# dao/homeDAO.py
import allure

from coreAgents.actionAgent import ActionAgent
from coreAgents.loggerAgent import LoggerAgent
from pageObjectLocators.myAccountPageLocators import MyAccountPage

log = LoggerAgent.get_logger("MyAccountPageDAO")


class MyAccountPageDAO(ActionAgent):
    """
    Data Access Object for MyAccountPage.
    Contains all actions methods for the home page.
    No assertions allowed here.
    """

    def __init__(self, runtimeAgent):
        super().__init__(runtimeAgent)

        self.pageManager = runtimeAgent
        self.myAccountPageLocators = MyAccountPage(runtimeAgent)

    @allure.step("Confirmed Log-In")
    def getMyAccountText(self):
        return self.myAccountPageLocators.myAccountText


