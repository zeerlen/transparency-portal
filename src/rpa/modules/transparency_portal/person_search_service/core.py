"""
Core module for person search service automation in the Transparency Portal.

Handles natural person search and data extraction.
"""

from typing import Optional, Union, List, Dict, Any
import time
import base64

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from src.rpa.modules.transparency_portal.CONSTANTS import (
    TransparencyPortalCONSTANTS,
    PersonSearchServiceCONSTANTS,
)

from src.rpa.utils.automations_utils import normalize_name, normalize_number
from src.rpa.modules.transparency_portal.person_search_service.actions import (
    GoToPersonSearchPage,
    StartSearch, SearchHandler,
)

from src.rpa.modules.transparency_portal.person_search_service.filters import FilterManager
from src.rpa.modules.transparency_portal.person_search_service.utils import PersonValidator, ResultValidator
from src.rpa.modules.transparency_portal.person_search_service.scraper import Scraper, OpenDetailPage
from src.rpa.modules.transparency_portal.person_search_service.json_exporter import JsonExporter


class PersonSearchService:
    """Search and extract natural person data from the Transparency Portal."""
    def __init__(self, web_bot: WebDriver, name: str, cpf: str, nis: Optional[str] = None,
                 search_by: str = 'cpf', search_filter: Optional[Union[str, List[str]]] = None,
                 timeout: int = 10):
        self.web_bot = web_bot
        self.name = name
        self.cpf = cpf
        self.nis = nis
        self.search_by = search_by
        self.search_filter = search_filter
        self.timeout = timeout
        self.base_url = TransparencyPortalCONSTANTS.Url.TRANSPARENCY_PORTAL
        self.json_exporter = JsonExporter()
        self.filter_manager = FilterManager(web_bot, timeout)
        self.result_validator = ResultValidator()

    def start_bot(self) -> None:
        """starts automation navigation"""
        GoToPersonSearchPage(self.web_bot, self.timeout).execute()

    def get_location(self) -> str:
        """Get the person's location"""
        try:
            return (
                WebDriverWait(self.web_bot, self.timeout)
                .until(EC.presence_of_element_located(
                    (By.XPATH, PersonSearchServiceCONSTANTS.Xpath.FETCH_LOCATION.value)
                ))
                .text.strip()
            )
        except TimeoutException:
            print("Location not found.")
            return 'Unknown'

    def get_cpf(self) -> str:
        """Get CPF from search results."""
        try:
            cpf = (
                WebDriverWait(self.web_bot, self.timeout)
                .until(EC.presence_of_element_located(
                    (By.XPATH, PersonSearchServiceCONSTANTS.Xpath.FETCH_CPF.value)
                ))
                .text.strip()
            )
            return normalize_number(cpf)
        except TimeoutException:
            print("CPF not found.")
            return 'Unknown'

    def screenshot(self, xpath: str) -> str:
        """Capture element screenshot as base64."""
        try:
            element = self.web_bot.find_element(By.XPATH, xpath)
            screenshot = base64.b64encode(element.screenshot_as_png).decode('utf-8')
            print("Screenshot captured")
            return screenshot
        except NoSuchElementException:
            print(f"Element not found: {xpath}")
            return ''
        except WebDriverException as e:
            print(f"Screenshot error: {e}")
            return ''

    def format_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format scraped data into records."""
        records = []
        for table in data:
            resource = table.pop('title')
            for row in table['rows']:
                nis = row.get('NIS', 'Não informado')
                details = []
                url = None
                if 'Detalhar' in row:
                    detail = row.pop('Detalhar')
                    url = self.base_url + detail
                    print(f"Scraping details: {resource}, URL: {url}")
                    details = OpenDetailPage(self.web_bot, url, self.timeout).execute()
                    if not details:
                        print(f"No details for {resource}")
                records.append({
                    'nome': row.get('Nome', 'Desconhecido'),
                    'nis': nis,
                    'recurso': resource,
                    'valor': row.get('Valor Recebido', 'Não informado'),
                    'link do recurso': url,
                    'extrato': details,
                })
        return records

    def extract_data(self) -> str:
        """Extract financial data and export as JSON."""
        (
            WebDriverWait(self.web_bot, self.timeout)
            .until(EC.element_to_be_clickable(
                (By.XPATH, PersonSearchServiceCONSTANTS.Xpath.FINANCIAL_RESOURCES_RECEIPTS_BTN.value)
            ))
            .click()
        )

        time.sleep(2)

        screenshot = self.screenshot(
            PersonSearchServiceCONSTANTS.Xpath.SCREENSHOT_MAIN_PAGE.value
        )

        data = Scraper(self.web_bot, self.timeout).scrape()

        return self.json_exporter.save(
            self.format_data(data),
            self.get_cpf(),
            self.get_location(),
            screenshot,
            save=True
        )

    def start_search(self, input_value: str) -> bool:
        """Start search with parameters and input value."""
        SearchHandler(self.web_bot, input_value, self.timeout).execute()
        self.filter_manager.apply(self.search_filter)
        StartSearch(self.web_bot, self.timeout).execute()
        return self.check_results(input_value)

    def check_results(self, input_value: str) -> bool:
        """Check and select matching search results."""
        try:
            time.sleep(7)
            get_lookup_values = WebDriverWait(self.web_bot, self.timeout).until(
                lambda b: b.find_element(
                    By.XPATH, PersonSearchServiceCONSTANTS.Xpath.TOTAL_VALUES_FOUND.value
                ).text.strip().replace('.', '')
            )

            values_found = int(get_lookup_values or 0)
            self.result_validator.check(values_found, input_value)

            names_found = self.web_bot.find_elements(
                By.XPATH, PersonSearchServiceCONSTANTS.Xpath.NAMES_FOUND.value
            )
            cpfs_found = self.web_bot.find_elements(
                By.XPATH, PersonSearchServiceCONSTANTS.Xpath.CPFs_FOUND.value
            )

            if len(names_found) != len(cpfs_found):
                raise ValueError('Names and CPFs mismatch')

            for name, cpf in zip(names_found, cpfs_found):
                result = PersonValidator(name.text.strip(), cpf.text.strip())
                if result.matches(self.name, self.cpf):
                    print(f"Match found: '{result.name}', CPF: {result.cpf}")
                    name.click()

                    time.sleep(2)

                    return True

            raise ValueError('No match found')

        except TimeoutException:
            print("Timeout waiting for results")
            self.result_validator.check(0, input_value)
            return False
        except NoSuchElementException as e:
            print(f"Element missing: {e}")
            self.result_validator.check(0, input_value)
            return False
        except ValueError as e:
            print(f"Error: {e}")
            return False

    @staticmethod
    def check_input(name: str, cpf: str, nis: Optional[str] = None) -> None:
        """Check if inputs are valid."""
        if not name or name.strip() == '':
            raise ValueError('Name cannot be empty.')
        if not cpf or cpf.strip() == '':
            raise ValueError('CPF cannot be empty.')
        if nis is not None and not nis.strip():
            raise ValueError('NIS cannot be empty.')

    def set_search_value(self, search_value: str) -> str:
        """Set the search value based on the options."""
        options = {'name': self.name, 'cpf': self.cpf, 'nis': self.nis}

        if search_value not in options:
            raise ValueError(f"Invalid option '{search_value}'. "
                             f"Use: {', '.join(options.keys())}")

        input_value = options[search_value]
        if not input_value:
            raise ValueError(f"Option '{search_value}' has no value.")

        return normalize_name(input_value) if search_value == 'name' else (
            normalize_number(input_value))

    def search(self) -> str:
        """Search person and return JSON data."""
        self.check_input(self.name, self.cpf, self.nis)
        input_value = self.set_search_value(self.search_by)
        self.start_bot()
        if self.start_search(input_value):
            return self.extract_data()
        return '[]'