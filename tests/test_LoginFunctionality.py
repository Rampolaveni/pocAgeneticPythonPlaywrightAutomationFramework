import pytest
from scenarios.loginScenarios import LoginScenarios

@pytest.mark.testrail(case_id='C46')
@pytest.mark.sanity
def test_userLogin(runtimeAgent):
    LoginScenarios(runtimeAgent).verify_successful_login()





