import io
import traceback

from src.rpa.modules.transparency_portal import TransparencyPortal
from src.rpa.utils.CONSTANTS import ERROR_PATH, SCREENSHOT_ERROR_PATH
from src.rpa.utils.web_driver_config import web_driver

web_bot = web_driver()


def main():
    transparency_portal = TransparencyPortal(web_bot)

    result_data = transparency_portal.person_search_service(
        name='Alen Silva',
        cpf='12345678901',
        nis='12345678901',
        search_by='cpf',
        search_filter='social_programs')

    print(result_data)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        web_bot.save_screenshot(
          SCREENSHOT_ERROR_PATH
        )
        log_buffer = io.StringIO()
        traceback.print_exc(file=log_buffer)
        with open(ERROR_PATH, "w") as log_file:
            log_file.write(log_buffer.getvalue())
        print(error)
    finally:
        web_bot.quit()