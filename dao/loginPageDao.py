# dao/homeDAO.py
import allure

from coreAgents.actionAgent import ActionAgent
from coreAgents.loggerAgent import LoggerAgent
from pageObjectLocators.loginPageLocators import LoginPage

log = LoggerAgent.get_logger("LoginPageDAO")


class LoginPageDAO(ActionAgent):
    """
    Data Access Object for Home Page.
    Contains all actions methods for the home page.
    No assertions allowed here.
    """

    def __init__(self, runtimeAgent):
        super().__init__(runtimeAgent)
        self.loginPageLocators = LoginPage(runtimeAgent)

    @allure.step("Entering user credentials")
    def enterUserEmailAndPassword(self):
        self.fill(self.loginPageLocators.userEmail, "rpolaveni@gmail.com")
        self.fill(self.loginPageLocators.userPassword, "test@123")

    @allure.step("Clicked on login button")
    def clickOnLoginButton(self):
        self.click(self.loginPageLocators.loginButton)




