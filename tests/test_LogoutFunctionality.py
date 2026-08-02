import pytest
from scenarios.logoutScenarios import LogoutScenarios

@pytest.mark.testrail(case_id='C47')
@pytest.mark.sanity
def test_userLogout(runtimeAgent):
    LogoutScenarios(runtimeAgent).verify_user_logout()

