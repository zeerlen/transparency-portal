import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.rpa.utils.CONSTANTS import CACHE_DIR


class JsonExporter:
    """Exports data to JSON format with optional file saving."""

    def __init__(self, filename='.json') -> None:
        """Initialize JSON exporter with a default filename."""
        if not filename or not filename.strip().endswith('.json'):
            raise ValueError("Filename must be a non-empty string ending with '.json'")
        self.filename = filename

    @staticmethod
    def generate_json(cpf: str) -> str:
        """Generate JSON with CPF and timestamp in Brazilian format."""
        if not cpf.isdigit() or len(cpf) != 6:
            raise ValueError("CPF must be exactly 6 digits")
        timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        os.makedirs(CACHE_DIR, exist_ok=True)
        return rf"{CACHE_DIR}\ID_{cpf}_{timestamp}.json"

    def save(
        self,
        data: List[Dict[str, Any]],
        cpf: str,
        location: str,
        screenshot: str = '',
        save: Optional[bool] = None,
    ) -> str:
        """Constructs JSON from data with optional screenshot and saves to file if specified.

        Args:
            data: List of dictionaries containing data to export.
            cpf: CPF identifier (6 digits) to include in JSON and filename.
            location: Location identifier to include in JSON.
            screenshot: Optional screenshot path or data (default: '').
            save: If True, saves JSON to file; if False, only returns JSON string (default: False).

        Returns:
            JSON string representation of the data.

        Raises:
            ValueError: If 'data' is not a list, cpf is invalid, or location is empty.
            OSError: If file saving fails when 'save' is True.
        """
        if not isinstance(data, list):
            raise ValueError("Data must be a list")
        if not cpf or not cpf.strip():
            raise ValueError("CPF cannot be empty")
        if not location or not location.strip():
            raise ValueError("Location cannot be empty")

        enriched_data = [
            {
                'nome': item.get('nome', 'Desconhecido'),
                'cpf': cpf,
                'nis': item.get('nis', 'Não informado'),
                'localidade': location,
                'recurso': item.get('recurso', 'Não informado'),
                'valor': item.get('valor', 'Não informado'),
                'link do recurso': item.get('link do recurso', 'Não informado'),
                'extrato': item.get('extrato', []),
            }
            for item in data
        ]

        _json = {'data': enriched_data, 'screenshot': screenshot}
        json_str = json.dumps(_json, ensure_ascii=False, indent=4)

        if save:
            filename = self.generate_json(cpf)
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                print(f"Saved {len(data)} item(s) to {filename}")
            except OSError as e:
                print(f"Failed to save JSON to {filename}: {str(e)}")
                raise
        else:
            print(f"Processed {len(data)} item(s) to JSON")

        return json_str