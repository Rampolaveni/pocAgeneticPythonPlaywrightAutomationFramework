# dao/homeDAO.py
import allure

from coreAgents.actionAgent import ActionAgent
from coreAgents.loggerAgent import LoggerAgent
from pageObjectLocators.homePageLocators import HomePage

log = LoggerAgent.get_logger("HomePageDAO")


class HomePageDAO(ActionAgent):
    """
    Data Access Object for Home Page.
    Contains all actions methods for the home page.
    No assertions allowed here.
    """

    def __init__(self, runtimeAgent):
        super().__init__(runtimeAgent)
        self.homePageLocators = HomePage(runtimeAgent)

    def clickOnMyAccountDropdown(self):
        self.click(self.homePageLocators.myAccountDropdownHomepage)

    def clickOnRegisterButton(self):
        self.click(self.homePageLocators.registerButtonHomepage)

    def clickOnLoginButton(self):
        self.click(self.homePageLocators.loginButtonHomepage)

    def getRegisterAccountText(self):
        return self.homePageLocators.txtRegisterAccount

    @allure.step("Clicked on logout button")
    def clickOnLogoutButton(self):
        self.click(self.homePageLocators.logoutButtonHomepage)

    def getLogoutAccountText(self):
        return self.homePageLocators.logoutConfirmationText

    @allure.step("Navigate to Home page")
    def navigateToHomePage(self):
        self.click(self.homePageLocators.homePage)

    @allure.step("Navigate to Login page via My Account menu")
    def navigate_to_login_page(self):
        log.info("Navigating to Login page")
        self.clickOnMyAccountDropdown()
        self.clickOnLoginButton()

    @allure.step("Navigate to Register page via My Account menu")
    def navigate_to_register_page(self):
        log.info("Navigating to Register page")
        self.clickOnMyAccountDropdown()
        self.clickOnRegisterButton()
