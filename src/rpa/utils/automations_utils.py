import os
import re


def clear_cache(path) -> None:
    extension = '.json'
    for filename in os.listdir(path):
        if filename.endswith(extension):
            file_path = os.path.join(path, filename)
            os.remove(file_path)
            print(f'File {filename} has been deleted.')


def normalize_number(number: str) -> str:
    """
    Normalize a numeric string by removing extra spaces and non-numeric characters.
    """
    number = re.sub(r'\D', '', number)
    number = re.sub(r'\s+', ' ', number.strip())

    return number


def normalize_name(name: str) -> str:
    """
    Normalize a name string by removing extra spaces, converting to uppercase,
    and removing special characters.
    """
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name.strip())

    return name.upper()
