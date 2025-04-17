"""
Actions for transparency portal automation.

Provides command classes for browser interactions.
"""

from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.rpa.modules.transparency_portal.CONSTANTS import TransparencyPortalCONSTANTS


class Bot(ABC):
    """Base class for browser automation actions."""

    def __init__(self, web_bot: WebDriver, timeout: int = 10) -> None:
        """Initialize with WebDriver and timeout."""
        self.web_bot = web_bot
        self.timeout = timeout

    @abstractmethod
    def execute(self) -> None:
        """Execute the automation action."""
        pass

    def wait_and_click(self, xpath: str) -> None:
        """Wait for element to be clickable and click it."""
        try:
            WebDriverWait(self.web_bot, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            ).click()
        except TimeoutException as e:
            raise TimeoutException(f"Failed to click element: {xpath}") from e


class AcceptCookies(Bot):
    """Accept cookies prompt on the portal."""
    XPATH = TransparencyPortalCONSTANTS.Xpath.ACCEPT_ALL_COOKIES_BTN.value

    def execute(self) -> None:
        """Click the accept cookies button."""
        try:
            self.wait_and_click(self.XPATH)
            print("Cookies accepted")
        except TimeoutException:
            print("No cookie prompt found")


class CloseTutorial(Bot):
    """Close tutorial notification on the portal."""
    XPATH = TransparencyPortalCONSTANTS.Xpath.TUTORIAL_NOTIFICATION_CLOSE_BTN.value

    def execute(self) -> None:
        """Click the close tutorial button."""
        try:
            self.wait_and_click(self.XPATH)
            print("Tutorial closed")
        except TimeoutException:
            print("No tutorial found")
