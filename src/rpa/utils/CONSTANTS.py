import os

USER_DATA_PATH = os.path.join(
    os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default'
)

RPA_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)

CACHE_DIR = os.path.join(RPA_BASE_DIR, 'cache')

COOKIE_PATH = os.path.join(CACHE_DIR, 'cookies.json')

LOCAL_STORAGE_PATH = os.path.join(CACHE_DIR, 'local_storage.json')

ERROR_PATH = os.path.join(RPA_BASE_DIR, 'log', 'error.txt')

SCREENSHOT_ERROR_PATH = os.path.join(RPA_BASE_DIR, 'logs', 'error.png')
