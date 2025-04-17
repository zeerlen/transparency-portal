"""
Web scraping for person search service automation in the Transparency Portal.

Extracts financial resource data from tables and detail pages.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    NoSuchWindowException,
    WebDriverException,
)

from src.rpa.modules.transparency_portal.CONSTANTS import (
    TransparencyPortalCONSTANTS,
    PersonSearchServiceCONSTANTS,
)


class Bot(ABC):
    """Base class for automation actions."""
    def __init__(self, web_bot: WebDriver, timeout: int = 10) -> None:
        """Initialize with WebDriver and timeout."""
        self.web_bot = web_bot
        self.timeout = timeout

    @abstractmethod
    def execute(self) -> None:
        """Execute the automation action."""
        pass


class ScrapeTable(Bot):
    """Scrapes resource tables."""

    def execute(self) -> List[Dict[str, Any]]:
        """Extract data from tables on the current page."""
        try:
            soup = self.get_soup()
            data = self.parse_tables(soup)
            print(f"Scraped {len(data)} table(s) from page")
            if not data:
                raise ValueError("No resource tables found")
            return data
        except Exception as e:
            print(f"Failed to scrape tables: {str(e)}")
            return []

    def get_soup(self) -> BeautifulSoup:
        """Create BeautifulSoup object from page source."""
        time.sleep(self.timeout)
        return BeautifulSoup(self.web_bot.page_source, "html.parser")

    def parse_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse tables with class into dictionaries."""
        data = []
        for table in soup.find_all("div", class_="br-table"):
            title = self.get_table_title(table)
            headers = [th.text.strip() for th in table.find("thead").find_all("th")]
            rows = [
                self.parse_row(tr, headers)
                for tr in table.find("tbody").find_all("tr")
            ]
            if rows:
                data.append({"title": title, "rows": rows})
        return data

    @staticmethod
    def get_table_title(table: Any) -> str:
        """Extract table title or return default."""
        strong = table.find("strong")
        return strong.text.strip() if strong else "No Title"

    @staticmethod
    def parse_row(tr: Any, headers: List[str]) -> Dict[str, Any]:
        """Parse a table row into a dictionary."""
        cols = [td.text.strip() for td in tr.find_all("td")]
        row = dict(zip(headers, cols))
        if link := tr.find("a"):
            row["Detalhar"] = link["href"]
        return row


class ScrapePages(Bot):
    """Scrapes paginated resource detail tables."""
    NEXT_PAGE_XPATH = PersonSearchServiceCONSTANTS.Xpath.NEXT_PAGE_BTN.value

    def execute(self) -> List[Dict[str, Any]]:
        """Extract tables from all pages of resource details."""
        rows: List[Dict[str, Any]] = []
        try:
            while True:
                if self.check_human_verification():
                    raise ValueError(f"Automation stopped: Detected 'Human Verification'")
                time.sleep(5)
                page_data = self.scrape_page()
                if page_data is None:
                    print("No data found on detail page")
                    break
                rows.extend(page_data)
                if not self.next_page():
                    break
            print(f"Scraped {len(rows)} row(s) from detail pages")
        except ValueError:
            raise
        except Exception as e:
            print(f"Failed to scrape detail pages: {str(e)}")
        return rows

    def check_human_verification(self) -> bool:
        """Check if human verification page is displayed."""
        try:
            return self.web_bot.title == "Human Verification"
        except Exception as e:
            print(f"Error checking human verification: {str(e)}")
            return False

    def scrape_page(self) -> List[Dict[str, Any]]:
        """Scrape table from the current page."""
        try:
            soup = BeautifulSoup(self.web_bot.page_source, "html.parser")
            table = soup.find("table", class_="dataTable no-footer")
            if not table:
                print("No table found on detail page")
                return []
            headers = [th.text.strip() for th in table.find("thead").find_all("th")]
            rows = [
                dict(zip(headers, [td.text.strip() for td in tr.find_all("td")]))
                for tr in table.find("tbody").find_all("tr")
            ]
            return rows
        except Exception as e:
            print(f"Failed to scrape detail page: {str(e)}")
            return []

    def next_page(self) -> bool:
        """Navigate to the next page if available."""
        try:
            time.sleep(5)
            WebDriverWait(self.web_bot, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, self.NEXT_PAGE_XPATH))
            ).click()
            print("Moved to next detail page")
            return True
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
            print("No more detail pages to scrape")
            return False


class OpenDetailPage(Bot):
    """Opens and scrapes a resource detail page."""
    def __init__(
        self,
        web_bot: WebDriver,
        resource_url: str,
        timeout: int = 10,
    ) -> None:
        """Initialize with WebDriver, resource URL, and timeout."""
        super().__init__(web_bot, timeout)
        self.resource_url = resource_url

    def execute(self) -> list[dict[str, Any]] | None:
        """Open resource detail page in new tab and scrape it."""
        details: List[Dict[str, Any]] = []
        try:
            self.open_tab()
            page_details = self.scrape_details()
            details = page_details if page_details is not None else []
        except ValueError as e:
            print(f"Failed to scrape details from {self.resource_url}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error scraping {self.resource_url}: {str(e)}")
        finally:
            self.close_tab()
        return details

    def open_tab(self) -> None:
        """Open resource URL in a new tab."""
        try:
            self.web_bot.execute_script(f"window.open('{self.resource_url}', '_blank');")
            if len(self.web_bot.window_handles) < 2:
                raise WebDriverException("No new tab")
            self.web_bot.switch_to.window(self.web_bot.window_handles[-1])
            time.sleep(5)
        except (WebDriverException, NoSuchWindowException) as e:
            raise ValueError(f"Failed to open tab for {self.resource_url}: {str(e)}") from e

    def scrape_details(self) -> List[Dict[str, Any]]:
        """Scrape details from the open page."""
        try:
            return ScrapePages(self.web_bot, self.timeout).execute()
        except ValueError:
            raise
        except Exception as e:
            print(f"Failed to scrape details: {str(e)}")
            return []

    def close_tab(self) -> None:
        """Close current tab and switch back to main tab."""
        try:
            self.web_bot.close()
            if self.web_bot.window_handles:
                self.web_bot.switch_to.window(self.web_bot.window_handles[0])
            time.sleep(2)
            print("Closed detail page tab")
        except (NoSuchWindowException, WebDriverException) as e:
            print(f"Failed to close tab: {str(e)}")


class Scraper:
    """Scrapes financial resources."""
    def __init__(self, web_bot: WebDriver, timeout: int = 10) -> None:
        """Initialize with WebDriver, timeout, and base URL."""
        self.web_bot = web_bot
        self.timeout = timeout
        self.base_url = TransparencyPortalCONSTANTS.Url.TRANSPARENCY_PORTAL

    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape resources from the current page."""
        try:
            return ScrapeTable(self.web_bot, self.timeout).execute()
        except ValueError as e:
            print(f"Failed to scrape resources: {str(e)}")
            return []