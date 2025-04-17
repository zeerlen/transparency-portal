"""
Constants for the Transparency Portal automation.

This module defines URLs and selectors used across the automation, organized by
functional area for clarity and maintainability.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Selector:
    """
    Represents a DOM selector for web automation.

    Attributes
    ----------
    value : str
        The selector string (e.g., XPath expression).
    by : str, optional
        The selector type (default is 'xpath').
    """
    value: str
    by: Literal['xpath', 'css', 'id', 'name', 'tag_name'] = 'xpath'


class TransparencyPortalCONSTANTS:
    """
    Constants for core interactions with the Transparency Portal.
    """
    class Url:
        """
        URLs used in the automation process.
        """
        TRANSPARENCY_PORTAL: str = 'https://portaldatransparencia.gov.br'

    class Xpath:
        """
        XPaths for core portal interactions, such as cookie prompts and tutorials.
        """
        ACCEPT_ALL_COOKIES_BTN: Selector = Selector('//*[@id="accept-all-btn"]')
        TUTORIAL_NOTIFICATION_CLOSE_BTN: Selector = Selector(
            '//button[contains(@class, "botao-tutorial") and contains(text(), "Pular tutorial")]'
        )


class PersonSearchServiceCONSTANTS:
    """
    Constants for the Person Search service automation.
    """

    class Xpath:
        """
        XPaths for person search service interactions, grouped by automation flow (navigation, search, filters, results).
        """

        # Navigation
        PEOPLE_SEARCH_SERVICE_BTN: Selector = Selector(
            '//h5[contains(@class, "pl-3") and contains(@class, "pr-3") and '
            'text()="Pessoas Físicas e Jurídicas"]'
        )
        NATURAL_PERSON_SEARCH_BTN: Selector = Selector(
            '//div[@id="main-content"]'
            '//button[@onclick="location.href=\'/pessoa-fisica/busca/lista\';"]'
        )

        # Search
        ENTER_SEARCH_VALUE: Selector = Selector('//*[@id="termo"]')
        SEARCH_BTN: Selector = Selector(
            '//form[@id="form-superior"]//button[contains(@class, "br-button") and @type="submit"]'
        )

        # Filters
        FILTER_SEARCH_BTN: Selector = Selector(
            '//div[@id="accordion1"]//button[contains(@aria-controls, "busca-refinada")]'
        )
        VISIBLE_FILTER_SEARCH_BTN: Selector = Selector(
            '//div[contains(@class, "item") and contains(@class, "bordered")]'
            '//button[contains(@class, "header") and @aria-controls="box-busca-refinada"]'
            '[span[contains(@class, "title") and text()="Refine a Busca"]]'
        )
        SOCIAL_PROGRAMS_BTN: Selector = Selector(
            '//div[@id="box-busca-refinada"]//label[@for="beneficiarioProgramaSocial"]'
        )

        # Results
        NAMES_FOUND: Selector = Selector('//a[contains(@class, "link-busca-nome")]')
        CPFs_FOUND: Selector = Selector('//div[contains(@class, "mt-3")]/strong')
        TOTAL_VALUES_FOUND: Selector = Selector(
            '//*[@class="br-list"]//p[contains(., "Foram encontrados")]/strong[@id="countResultados"]'
        )
        FETCH_LOCATION: Selector = Selector(
            '//section[@class="dados-tabelados"]//div[@class="col-xs-12 col-sm-3"]'
            '[.//strong[contains(text(), "Localidade")]]/span'
        )
        FETCH_CPF: Selector = Selector(
            '//section[@class="dados-tabelados"]//div[contains(@class, "col-xs-12") and '
            'contains(.//strong, "CPF")]//span'
        )
        FINANCIAL_RESOURCES_RECEIPTS_BTN: Selector = Selector(
            '//span[contains(@class, "title") and contains(text(), "Recebimentos de recursos")]'
        )
        SCREENSHOT_MAIN_PAGE: Selector = Selector('//*[@id="main"]')
        NEXT_PAGE_BTN: Selector = Selector('//*[@id="tabelaDetalheValoresRecebidos_next"]/button')