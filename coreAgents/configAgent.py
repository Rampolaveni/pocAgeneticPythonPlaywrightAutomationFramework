# coreAgents/configAgent.py

from copy import deepcopy
from typing import Any, Dict

from config.global_config import GLOBAL_CONFIG
from config.qa_config import QA_CONFIG
from config.uat_config import UAT_CONFIG
from config.prod_config import PROD_CONFIG


class ConfigAgent:
    """
    Builds final framework configuration.

    It combines:
        GLOBAL_CONFIG + environment config + runtime command-line values
    """

    ENV_CONFIG_MAP = {
        "qa": QA_CONFIG,
        "uat": UAT_CONFIG,
        "prod": PROD_CONFIG,
    }

    REQUIRED_KEYS = [
        "env",
        "base_url",
        "browser",
        "headed",
        "slow_mo",
        "playwright_timeout",
        "viewport",
        "locale",
        "timezone_id",
        "ignore_https_errors",
        "accept_downloads",
        "adminCredentials",
    ]

    def __init__(self, env_name: str):
        """
        Creates ConfigAgent for selected environment.

        Example:
            ConfigAgent("qa")
        """

        self.env_name = self._validate_env_name(env_name)
        self.config = self._build_base_config()

    def _validate_env_name(self, env_name: str) -> str:
        """
        Validates environment name.
        """

        if not env_name:
            raise ValueError("Environment name cannot be empty")

        env_name = env_name.lower().strip()

        if env_name not in self.ENV_CONFIG_MAP:
            raise ValueError(
                f"Invalid environment: {env_name}. "
                f"Allowed values are: {list(self.ENV_CONFIG_MAP.keys())}"
            )

        return env_name

    def _build_base_config(self) -> Dict[str, Any]:
        """
        Merges GLOBAL_CONFIG with selected environment config.

        Environment config has priority over global config.
        """

        global_config = deepcopy(GLOBAL_CONFIG)
        env_config = deepcopy(self.ENV_CONFIG_MAP[self.env_name])

        final_config = {
            **global_config,
            **env_config,
        }

        final_config["env"] = self.env_name

        return final_config

    def apply_runtime_values(
        self,
        browser: str,
        headed: bool,
        test_type: str,
        testrail_enabled: bool,
        report_enabled: bool,
    ) -> None:
        """
        Applies command-line/runtime values from Pytest.
        """

        self.config["browser"] = browser
        self.config["headed"] = headed
        self.config["test_type"] = test_type or "all"
        self.config["testrail_enabled"] = testrail_enabled
        self.config["report_enabled"] = report_enabled

        self.validate_config()

    def validate_config(self) -> None:
        """
        Validates required final config keys.
        """

        missing_keys = []

        for key in self.REQUIRED_KEYS:
            if key not in self.config:
                missing_keys.append(key)

        if missing_keys:
            raise KeyError(
                f"Missing required config keys for environment "
                f"'{self.env_name}': {missing_keys}"
            )

        if not self.config["base_url"]:
            raise ValueError(f"base_url is empty for environment: {self.env_name}")

        if "valid_email" not in self.config["adminCredentials"]:
            raise KeyError("adminCredentials.valid_email is missing")

        if "valid_password" not in self.config["adminCredentials"]:
            raise KeyError("adminCredentials.valid_password is missing")

    def get_value(self, key_path: str) -> Any:
        """
        Gets nested config value.

        Example:
            get_value("adminCredentials.valid_email")
            get_value("viewport.width")
        """

        value = self.config

        for key in key_path.split("."):
            if not isinstance(value, dict) or key not in value:
                raise KeyError(f"Config key not found: {key_path}")

            value = value[key]

        return value

    def set_value(self, key_path: str, new_value: Any) -> None:
        """
        Sets nested config value.

        Example:
            set_value("adminCredentials.valid_email", "new@email.com")
        """

        keys = key_path.split(".")
        current = self.config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}

            current = current[key]

        current[keys[-1]] = new_value

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns final config as a safe copy.
        """

        return deepcopy(self.config)