import json
import os
from typing import Any

from src.rpa.modules.transparency_portal.CONSTANTS import TransparencyPortalCONSTANTS
from src.rpa.utils.CONSTANTS import LOCAL_STORAGE_PATH, COOKIE_PATH, SCREENSHOT_PATH
from src.rpa.utils.web_driver_config import web_driver

web_bot = web_driver(headless=False, userdata=True)


def get_cache(driver, url: str,
              local_storage_path: str, cookie_path: str) -> Any | None:

    driver.get(f'{url}')
    driver.implicitly_wait(10)

    local_storage = driver.execute_script(
        "return JSON.stringify(localStorage);"
    )

    os.makedirs(
        os.path.dirname(local_storage_path), exist_ok=True
    )

    with open(local_storage_path, 'w', encoding='utf-8') as file:
        file.write(local_storage)
        print(f"Local Storage saved in '{local_storage_path}'!")

    cookies = driver.get_cookies()

    os.makedirs(
        os.path.dirname(cookie_path), exist_ok=True
    )

    with open(cookie_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(cookies))
        print(f"Cookies salved in '{cookie_path}'!")


def main():

    get_cache(driver=web_bot,
              url=TransparencyPortalCONSTANTS.Url.TRANSPARENCY_PORTAL,
              local_storage_path=LOCAL_STORAGE_PATH,
              cookie_path=COOKIE_PATH,
              )


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        web_bot.save_screenshot(SCREENSHOT_PATH)
        print(error)
    finally:
        web_bot.quit()
