import pytest
from scenarios.productScenarios import ProductScenarios

@pytest.mark.testrail(case_id='C50')
@pytest.mark.sanity
def test_searchFunctionality(runtimeAgent):
    ProductScenarios(runtimeAgent).verify_product_search()
