# dao/homeDAO.py
import allure

from coreAgents.actionAgent import ActionAgent
from coreAgents.loggerAgent import LoggerAgent
from pageObjectLocators.productPageLocators import ProductPage

log = LoggerAgent.get_logger("ProductPageDAO")


class ProductPageDAO(ActionAgent):
    """
    Data Access Object for Product Page.
    Contains all actions methods for the home page.
    No assertions allowed here.
    """

    def __init__(self, runtimeAgent):
        super().__init__(runtimeAgent)
        self.productPageLocators = ProductPage(runtimeAgent)

    # ===== Actions / Methods =====
    @allure.step("Entered product")
    def searchProductWithName(self, productName):
        self.fill(self.productPageLocators.searchBar, productName)

    @allure.step("Clicked on search button")
    def clickOnSearchButton(self):
        self.click(self.productPageLocators.searchButton)

    @allure.step("Getting results")
    def getProductSearchResults(self):
        productNames = self.productPageLocators.productSearchResults.all_text_contents()
        return productNames

    @allure.step("Product selected")
    def selectProductByName(self, productName):
        selectProductByName = f"//h4/a[text()='{productName}']"
        self.click(selectProductByName)

    @allure.step("Product compared")
    def compareProductWithName(self, productName):
        compareProductWithName = f"//div/h1[text()='{productName}']/parent::div//button[@data-original-title='Compare this Product']"
        self.click(compareProductWithName)

    @allure.step("product comparison successful")
    def getProductComparisonSuccessMessage(self):
        return self.get_text(self.productPageLocators.getProductComparisonSuccessMessage)


