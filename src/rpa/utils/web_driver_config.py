from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from typing import Any
import json
import os

from src.rpa.utils.CONSTANTS import USER_DATA_PATH


def local_storage(driver, local_storage_path) -> Any | None:
    if os.path.exists(local_storage_path):
        try:
            with open(local_storage_path, 'r', encoding='utf-8') as file:
                local_storage_data = json.load(file)
            for key, value in local_storage_data.items():
                driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
                return driver
        except Exception as e:
            print(f"Error loading local storage from {local_storage_path}: {e}")


def load_cookies(driver, cookie_path) -> Any | None:
    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, 'r', encoding='utf-8') as file:
                cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
                return driver
        except Exception as e:
            print(f"Error loading cookies from {cookie_path}: {e}")


def web_driver(headless: bool = True, userdata: bool = False) -> webdriver.Chrome:

    options = ChromeOptions()

    if headless:
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        )

    if userdata:
        options.add_argument(rf'--user-data-dir={USER_DATA_PATH}')

    options.add_argument('--disable-blink-features=AutomationControlled')

    options.add_experimental_option(
        'prefs',
        {
            'safebrowsing.enabled': True,
        }
    )

    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])

    options.page_load_strategy = 'normal'
    options.set_capability('platformName', 'ANY')
    options.set_capability('browserName', 'chrome')

    grid_url = 'http://localhost:4444/wd/hub'
    driver = webdriver.Remote(command_executor=grid_url, options=options)

    driver.maximize_window()

    return driver