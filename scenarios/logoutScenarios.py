# scenarios/loginScenario.py
# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCENARIO
# Contains all assertions for Login functionality
# Calls DAO for actions, then asserts on results
# ─────────────────────────────────────────────────────────────────────────────

import allure
from playwright.sync_api import expect

from coreAgents.loggerAgent import LoggerAgent

log = LoggerAgent.get_logger("LogoutScenarios")


class LogoutScenarios:

    def __init__(self, runtimeAgent):
        self.runtimeAgent = runtimeAgent

    @allure.step("TestCase: Validate user logout")
    def verify_user_logout(self) -> None:
        """
        Full login scenario:
        1. Navigate to login page
        2. Enter credentials
        3. Submit.
        4. Assert user logout
        """
        log.info(f"Scenario: Verify user logout ")

        # ── Action ────────────────────────────────────────────────────────────
        self.runtimeAgent.homePageDao.navigate_to_login_page()
        self.runtimeAgent.loginPageDao.enterUserEmailAndPassword()
        self.runtimeAgent.loginPageDao.clickOnLoginButton()

        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Assert: User login successfully"):
            confirmation_msg = self.runtimeAgent.myAccountPageDao.getMyAccountText()
            expect(confirmation_msg).to_have_text("My Account")
            log.info("Assertion passed: User login successfully")

        self.runtimeAgent.homePageDao.clickOnLogoutButton()

        with allure.step("Assert: User logout successfully"):
            confirmAccountLogoutText = self.runtimeAgent.homePageDao.getLogoutAccountText()
            expect(confirmAccountLogoutText).to_have_text("Account Logout")
            log.info("Assertion passed: User logout successfully")