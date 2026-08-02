import pytest

from scenarios.registrationScenarios import RegistrationScenarios

@pytest.mark.testrail(case_id='C49')
@pytest.mark.sanity
def test_registerUser(runtimeAgent):
    RegistrationScenarios(runtimeAgent).verify_user_registration()







