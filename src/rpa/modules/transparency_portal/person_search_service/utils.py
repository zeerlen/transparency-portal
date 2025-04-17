from src.rpa.utils.automations_utils import normalize_name, normalize_number


class PersonValidator:
    def __init__(self, name: str, cpf: str) -> None:
        """
        Normalizes and stores name and CPF for validation.
        """
        if not name or not cpf:
            raise ValueError("Name and CPF cannot be empty")

        self.name = normalize_name(name)
        self.cpf = self.trim_cpf(cpf)

    @staticmethod
    def trim_cpf(cpf: str) -> str:
        """
        Removes unnecessary characters from CPF and returns a formatted substring.
        """
        if not cpf or cpf.strip() == '':
            raise ValueError('CPF cannot be empty.')

        normalized = normalize_number(cpf)
        return normalized[3:9] if len(normalized) >= 9 else normalized

    def matches(self, name: str, cpf: str) -> bool:
        """
        Checks if the provided name and CPF match the instance's data.
        """
        try:
            if not name or not name.strip() or not cpf:
                print(f"Validation skipped: empty name or CPF")
                return False
            is_valid = (
                self.cpf == self.trim_cpf(cpf)
                and any(
                    part in self.name.split()
                    for part in normalize_name(name).split()
                    if part
                )
            )
            print(f"Validated name '{normalize_name(name)}' and CPF"
                  f"'{self.trim_cpf(cpf)}': {'success' if is_valid else 'failed'}")
            return is_valid

        except Exception as e:
            print(f"Validation failed for name '{normalize_name(name)}', CPF '{cpf}': {str(e)}")
            return False


class TooManyResultsError(Exception):
    """Raised when too many results are found."""
    pass


class ResultValidator:
    MAX_THRESHOLD = 10

    def check(self, values_found: int, input_value: str) -> None:
        """
        Validates the number of search results against a threshold.
        """
        if values_found < 0:
            raise ValueError(f"Invalid result count: {values_found}")
        if values_found > self.MAX_THRESHOLD:
            raise TooManyResultsError(
                f"Found {values_found} results for '{input_value}', "
                f"exceeds maximum of {self.MAX_THRESHOLD}"
            )
        if values_found == 0:
            raise ValueError(f"No results found for '{input_value}'")
        print(f"Validated {values_found} results for '{input_value}'")