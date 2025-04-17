"""
Actions for person search service automation in the Transparency Portal.

Provides command classes for browser interactions.
"""

from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.rpa.modules.transparency_portal.actions import Bot
from src.rpa.modules.transparency_portal.CONSTANTS import (
    TransparencyPortalCONSTANTS,
    PersonSearchServiceCONSTANTS,
)


class GoToPersonSearchPage(Bot):
    """Navigate to the person search page."""
    PEOPLE_SEARCH_SERVICE_BTN = PersonSearchServiceCONSTANTS.Xpath.PEOPLE_SEARCH_SERVICE_BTN.value
    NATURAL_PERSON_SEARCH_BTN = PersonSearchServiceCONSTANTS.Xpath.NATURAL_PERSON_SEARCH_BTN.value

    def execute(self) -> None:
        """Click through menu to reach person search page."""
        try:
            self.wait_and_click(self.PEOPLE_SEARCH_SERVICE_BTN)
            self.wait_and_click(self.NATURAL_PERSON_SEARCH_BTN)
            print("On search page")
        except TimeoutException as e:
            raise RuntimeError("Navigation to search page failed") from e


class SearchHandler(Bot):
    """Handle search input value entry."""
    XPATH = PersonSearchServiceCONSTANTS.Xpath.ENTER_SEARCH_VALUE.value

    def __init__(
        self, web_bot: WebDriver, value_to_search: str, timeout: int = 10
    ) -> None:
        super().__init__(web_bot, timeout)
        self.value_to_search = value_to_search

    def execute(self) -> None:
        """Clear and enter search value in input field."""
        try:
            field = WebDriverWait(self.web_bot, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, self.XPATH))
            )
            field.clear()
            field.send_keys(self.value_to_search)
            print(f"Value entered: {self.value_to_search}")
        except TimeoutException as e:
            raise RuntimeError("Failed to enter search value") from e


class StartSearch(Bot):
    """Start the search process."""
    XPATH = PersonSearchServiceCONSTANTS.Xpath.SEARCH_BTN.value

    def execute(self) -> None:
        """Click the search button."""
        try:
            self.wait_and_click(self.XPATH)
            print("Search started")
        except TimeoutException as e:
            raise RuntimeError("Failed to start search") from e