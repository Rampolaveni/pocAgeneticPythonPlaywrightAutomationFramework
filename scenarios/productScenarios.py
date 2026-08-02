# scenarios/loginScenario.py
# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCENARIO
# Contains all assertions for Login functionality
# Calls DAO for actions, then asserts on results
# ─────────────────────────────────────────────────────────────────────────────

import allure

from coreAgents.loggerAgent import LoggerAgent

log = LoggerAgent.get_logger("ProductScenarios")


class ProductScenarios:

    def __init__(self, runtimeAgent):
        self.runtimeAgent = runtimeAgent

    @allure.step("TestCase: Validate product comparison")
    def verify_product_comparison(self) -> None:
        log.info(f"TestCase: Validate product comparison ")
        # ── Action ────────────────────────────────────────────────────────────
        self.runtimeAgent.homePageDao.navigate_to_login_page()
        self.runtimeAgent.loginPageDao.enterUserEmailAndPassword()
        self.runtimeAgent.loginPageDao.clickOnLoginButton()
        self.runtimeAgent.homePageDao.navigateToHomePage()
        self.runtimeAgent.productPageDao.searchProductWithName("iMac")
        self.runtimeAgent.productPageDao.clickOnSearchButton()
        self.runtimeAgent.productPageDao.selectProductByName("iMac")
        self.runtimeAgent.productPageDao.compareProductWithName("iMac")
        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Product comparison assertion"):
            productComparisonSuccessMessage =  self.runtimeAgent.productPageDao.getProductComparisonSuccessMessage()
            assert "Success: You have added iMac to your product comparison!" in productComparisonSuccessMessage
            log.info("Product Comparison Successful")

    @allure.step("TestCase: Validate product search")
    def verify_product_search(self) -> None:
        log.info(f"TestCase: Validate product search ")
        # ── Action ────────────────────────────────────────────────────────────
        self.runtimeAgent.homePageDao.navigate_to_login_page()
        self.runtimeAgent.loginPageDao.enterUserEmailAndPassword()
        self.runtimeAgent.loginPageDao.clickOnLoginButton()
        self.runtimeAgent.homePageDao.navigateToHomePage()
        self.runtimeAgent.productPageDao.searchProductWithName("iMac")
        self.runtimeAgent.productPageDao.clickOnSearchButton()
        productsList = self.runtimeAgent.productPageDao.getProductSearchResults()
        # ── Assertion ─────────────────────────────────────────────────────────
        with allure.step("Validating product in search results"):
            assert "iMacv" in productsList, "iMac product not found in search results"

