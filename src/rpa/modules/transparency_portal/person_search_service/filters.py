"""
Filter management for person search service automation in the Transparency Portal.

Provides strategies to apply search filters.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.rpa.modules.transparency_portal.CONSTANTS import PersonSearchServiceCONSTANTS


class FilterStrategy(ABC):
    """Base class for filter strategies."""
    def __init__(self, web_bot: WebDriver, timeout: int = 10) -> None:
        """Initialize with WebDriver and timeout."""
        self.web_bot = web_bot
        self.timeout = timeout

    @abstractmethod
    def apply(self) -> None:
        """Apply the filter to the search."""
        pass

    def click_element(self, xpath: str, context: str) -> None:
        """Wait for element to be clickable and click it."""
        try:
            WebDriverWait(self.web_bot, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            ).click()
        except TimeoutException as e:
            raise ValueError(f"Failed to click {context}: {xpath}") from e


class SocialProgramsFilter(FilterStrategy):
    """Filter for social programs."""
    XPATH = PersonSearchServiceCONSTANTS.Xpath.SOCIAL_PROGRAMS_BTN.value

    def apply(self) -> None:
        """Click the social programs filter button."""
        self.click_element(self.XPATH, "social programs filter")


class FilterManager:
    """Manage and apply search filters."""
    VISIBLE_FILTER_SEARCH = PersonSearchServiceCONSTANTS.Xpath.VISIBLE_FILTER_SEARCH_BTN.value
    FILTER_SEARCH = PersonSearchServiceCONSTANTS.Xpath.FILTER_SEARCH_BTN.value

    def __init__(self, web_bot: WebDriver, timeout: int = 10) -> None:
        """Initialize with WebDriver, timeout, and filter strategies."""
        self.web_bot = web_bot
        self.timeout = timeout
        self.filters: Dict[str, FilterStrategy] = {
            "social_programs": SocialProgramsFilter(web_bot, timeout),
        }

    def is_visible_button(self) -> bool:
        """Ensure filter search button is active."""
        try:
            button = WebDriverWait(self.web_bot, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, self.VISIBLE_FILTER_SEARCH))
            )
            if "active" in button.get_attribute("class").split():
                print("Filter button already active")
                return True
            self.click_filter()
            return True
        except TimeoutException:
            print("Filter button unavailable")
            return False

    def click_filter(self) -> None:
        """Click the filter search button."""
        self.click_element(self.FILTER_SEARCH, "filter button")

    def click_element(self, xpath: str, context: str) -> None:
        """Wait for element to be clickable and click it."""
        try:
            WebDriverWait(self.web_bot, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            ).click()
        except TimeoutException as e:
            raise ValueError(f"Failed to click {context}: {xpath}") from e

    def validate_filters(self, filter_list: List[str]) -> List[str]:
        """Validate filters and remove duplicates."""
        available = sorted(self.filters.keys())
        invalid = sorted(f for f in filter_list if f not in self.filters)
        if invalid:
            raise ValueError(
                f"Invalid filters: {', '.join(invalid)}. Available: {', '.join(available)}"
            )
        return list(dict.fromkeys(filter_list))

    def apply(self, filters: Optional[Union[str, List[str]]] = None) -> None:
        """Apply specified filters to the search."""
        if not filters:
            print("No filters provided")
            return

        filter_list = [filters] if isinstance(filters, str) else filters
        unique_filters = self.validate_filters(filter_list)

        if len(unique_filters) < len(filter_list):
            print("Duplicates removed from filters")

        if not self.is_visible_button():
            print("Cannot apply filters: filter button unavailable")
            return

        for _filter in unique_filters:
            print(f"Applying filter: {_filter}")
            self.filters[_filter].apply()