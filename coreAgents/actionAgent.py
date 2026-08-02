# coreAgents/actionAgent.py

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from coreAgents.loggerAgent import LoggerAgent
from coreAgents.pathAgent import PathAgent


class ActionAgent:
    """
    Central reusable UI actions layer.

    This class wraps common Playwright actions with:
    - logging
    - timeout handling
    - screenshot support
    - reusable action methods
    """

    def __init__(self, runtime_agent):
        """
        Creates ActionAgent.

        Args:
            runtime_agent: RuntimeAgent object for current test execution
        """

        self.runtime_agent = runtime_agent
        self.page = runtime_agent.get_page()
        self.timeout = runtime_agent.get_config_value("playwright_timeout")
        self.log = LoggerAgent.get_logger(self.__class__.__name__)

    def _resolve_locator(self, target: Any):
        """
        Accepts either:
        - Playwright locator object
        - selector string

        Returns Playwright locator.
        """

        if isinstance(target, str):
            return self.page.locator(target)

        return target

    def _get_target_name(self, target: Any, description: str = "") -> str:
        """
        Returns clean target name for logging.

        If description is provided, uses description.
        If target is selector string, returns selector.
        If target is Playwright Locator, extracts only selector from locator string.
        """

        if description:
            return description

        if isinstance(target, str):
            return target

        target_text = str(target)

        selector_match = re.search(
            r'selector="([^"]+)"',
            target_text,
        )

        if selector_match:
            return selector_match.group(1)

        return target_text

    def click(self, target: Any, description: str = "") -> None:
        """
        Clicks an element after waiting for visibility.
        """

        locator = self._resolve_locator(target)
        action_name = self._get_target_name(target, description)

        self.log.info(f"Clicking element: {action_name}")

        locator.wait_for(
            state="visible",
            timeout=self.timeout,
        )

        locator.click(timeout=self.timeout)

        self.log.info(f"Clicked element successfully: {action_name}")

    def fill(self, target: Any, value: str, description: str = "") -> None:
        """
        Fills text into an input field.
        """

        locator = self._resolve_locator(target)
        action_name = self._get_target_name(target, description)

        self.log.info(f"Filling value into element: {action_name}")

        locator.wait_for(
            state="visible",
            timeout=self.timeout,
        )

        locator.fill(str(value), timeout=self.timeout)

        self.log.info(f"Filled value successfully into element: {action_name}")


    def get_text(self, target: Any, description: str = "") -> str:
        """
        Gets visible text from an element.
        """

        locator = self._resolve_locator(target)
        action_name = description or str(target)

        self.log.info(f"Getting text from element: {action_name}")

        locator.wait_for(
            state="visible",
            timeout=self.timeout,
        )

        text = locator.inner_text(timeout=self.timeout).strip()

        self.log.info(f"Text found from element '{action_name}': {text}")

        return text

    def is_visible(self, target: Any, timeout: int = 5000, description: str = "") -> bool:
        """
        Checks whether element is visible.
        """

        locator = self._resolve_locator(target)
        action_name = description or str(target)

        try:
            self.log.info(f"Checking visibility of element: {action_name}")
            return locator.is_visible(timeout=timeout)

        except PlaywrightTimeoutError:
            self.log.warning(f"Element not visible within timeout: {action_name}")
            return False

    def wait_for_url_contains(self, partial_url: str, timeout: int | None = None) -> None:
        """
        Waits until current page URL contains expected partial URL.
        """

        final_timeout = timeout or self.timeout

        self.log.info(f"Waiting for URL to contain: {partial_url}")

        self.page.wait_for_url(
            f"**{partial_url}**",
            timeout=final_timeout,
        )

        self.log.info(f"URL matched successfully: {self.page.url}")

    def wait_for_page_load(self) -> None:
        """
        Waits for page DOM content load.
        """

        self.log.info("Waiting for page load")

        self.page.wait_for_load_state(
            "domcontentloaded",
            timeout=self.timeout,
        )

        self.log.info("Page loaded successfully")

    def take_screenshot(self, screenshot_name: str) -> Path:
        """
        Takes full-page screenshot and returns screenshot path.
        """

        PathAgent.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        safe_name = self._make_safe_file_name(screenshot_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        screenshot_path = PathAgent.SCREENSHOTS_DIR / f"{safe_name}_{timestamp}.png"

        self.page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        self.log.info(f"Screenshot captured: {screenshot_path}")

        return screenshot_path

    @staticmethod
    def _make_safe_file_name(name: str) -> str:
        """
        Converts text into safe file name.
        """

        safe_name = re.sub(r"[^A-Za-z0-9_]+", "_", name)
        return safe_name.strip("_").lower()