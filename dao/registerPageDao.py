# dao/registerPageDAO.py
import allure
from coreAgents.actionAgent import ActionAgent
from coreAgents.loggerAgent import LoggerAgent
from pageObjectLocators.registerPageLocators import RegisterPage

log = LoggerAgent.get_logger("RegisterPageDAO")


class RegisterPageDAO(ActionAgent):
    """
       Data Access Object for Register Page.
       Contains all actions methods for the home page.
       No assertions allowed here.
       """

    def __init__(self, runtimeAgent):
        super().__init__(runtimeAgent)
        self.registerPageLocators = RegisterPage(runtimeAgent)

    # ===== Actions / Methods =====
    @allure.step("Entering user details for registration.")
    def enterUserRegistrationDetails(self):
        self.fill(self.registerPageLocators.firstName, "Ram")
        self.fill(self.registerPageLocators.lastName, "Polaveni")
        self.fill(self.registerPageLocators.email, "rpolaveni@gmail.com")
        self.fill(self.registerPageLocators.telephone, "0404441536")
        self.fill(self.registerPageLocators.password, "test@123")
        self.fill(self.registerPageLocators.passwordConfirm, "test@123")

    @allure.step("Privacy policy checkbox checked.")
    def clickOnCheckboxPrivacyPolicy(self):
        self.check(self.registerPageLocators.checkboxPrivacyPolicy)

    @allure.step("Continued to next.")
    def clickOnContinue(self):
        self.click(self.registerPageLocators.btnContinue)
