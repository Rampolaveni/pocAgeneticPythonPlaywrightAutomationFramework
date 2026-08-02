# scenarios/loginScenario.py
# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCENARIO
# Contains all assertions for Login functionality
# Calls DAO for actions, then asserts on results
# ─────────────────────────────────────────────────────────────────────────────

import allure
from playwright.sync_api import expect

from conftest import runtimeAgent
from coreAgents.loggerAgent import LoggerAgent

log = LoggerAgent.get_logger("RegistrationScenarios")


class RegistrationScenarios:

    def __init__(self, runtimeAgent):
        self.runtimeAgent = runtimeAgent

    @allure.step("TestCase: Validate user register")
    def verify_user_registration(self) -> None:
        log.info(f"TestCase: Validate user register ")

        # ── Action ────────────────────────────────────────────────────────────
        self.runtimeAgent.homePageDao.navigate_to_register_page()
        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Register page loaded successfully "):
            confirmationMsg = self.runtimeAgent.homePageDao.getRegisterAccountText()
            expect(confirmationMsg).to_have_text("Register Account")

        self.runtimeAgent.registerPageDao.enterUserRegistrationDetails()
        self.runtimeAgent.registerPageDao.clickOnCheckboxPrivacyPolicy()
        self.runtimeAgent.registerPageDao.clickOnContinue()
        allure.step("User registration successfully")
