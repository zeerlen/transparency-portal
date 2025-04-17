"""
Core module for the Transparency Portal automation.

This module defines the `TransparencyPortal` class, which orchestrates web scraping
and data extraction from the Brazilian Transparency Portal.
"""

from typing import Optional, Union, List
from tenacity import retry, stop_after_attempt, wait_fixed

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from src.rpa.utils.CONSTANTS import LOCAL_STORAGE_PATH, COOKIE_PATH
from src.rpa.utils.web_driver_config import local_storage, load_cookies
from src.rpa.modules.transparency_portal.actions import AcceptCookies, CloseTutorial
from src.rpa.modules.transparency_portal.CONSTANTS import TransparencyPortalCONSTANTS
from src.rpa.modules.transparency_portal.person_search_service.core import PersonSearchService


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
class TransparencyPortal:
    """
    Orchestrates automations for the Brazilian Transparency Portal.

    This class serves as the main entry point for web scraping and data extraction,
    providing lazy-initialized access to specialized modules like `PersonQuery`.
    It configures the WebDriver, navigates to the portal, and ensures robust
    automation tailored for the portal's dynamic content.

    Parameters
    ----------
    web_bot : WebDriverProtocol
        The Selenium WebDriver instance for browser automation.
    timeout : int, optional
        Timeout in seconds for WebDriver operations (default is 10).
    auto_start : bool, optional
        Whether to navigate to the portal on initialization (default is True).

    Attributes
    ----------
    __person_search_service : PersonSearchService
        The lazily-initialized module for person-related queries.

    Raises
    ------
    ValueError
        If `web_bot` is None or `timeout` is negative.
    RuntimeError
        If navigation to the portal fails after retries.

    Examples
    --------
    >>> from selenium.webdriver.chrome.webdriver import WebDriver
    >>> transparency_portal = TransparencyPortal(WebDriver())
    >>> transparency_portal.person_search_service(name="Alen Silva", cpf="12345678901")
    """

    def __init__(self, web_bot: WebDriver, timeout: int = 10, auto_start: bool = True) -> None:
        """
        Initializes the TransparencyPortal orchestrator.
        """

        if web_bot is None:
            raise ValueError("WebDriver cannot be None")
        if timeout < 0:
            raise ValueError("Timeout cannot be negative")

        self.__web_bot = web_bot
        self.__timeout = timeout
        self.__person_search_service: PersonSearchService | None = None
        if auto_start:
            self.start_bot()

    def person_search_service(self, name: str, cpf: str, nis: Optional[str] = None, search_by: str = 'cpf',
                              search_filter: Optional[Union[str, List[str]]] = None) -> PersonSearchService:
        """
        Provides access to the PersonSearchService module.
        The module is initialized lazily on first access to optimize resource usage.
        """

        if self.__person_search_service is None:
            self.__person_search_service = PersonSearchService(
                self.__web_bot, name=name, cpf=cpf, nis=nis, search_by=search_by,
                search_filter=search_filter, timeout=self.__timeout).search()
        return self.__person_search_service

    def start_bot(self) -> None:
        """
        Navigates to the Transparency Portal and verifies page load.

        This method initializes the WebDriver by loading the portal's main page and
        ensures the page is fully accessible. It uses retries to handle transient
        network issues and includes a fallback wait for dynamic content.
        """
        try:
            self.__web_bot.get(TransparencyPortalCONSTANTS.Url.TRANSPARENCY_PORTAL)
            load_cookies(self.__web_bot, COOKIE_PATH)
            local_storage(self.__web_bot, LOCAL_STORAGE_PATH)
            AcceptCookies(self.__web_bot, self.__timeout).execute()
            CloseTutorial(self.__web_bot, self.__timeout).execute()
        except WebDriverException as e:
            raise RuntimeError(f"Failed to load Transparency Portal: {e}") from e