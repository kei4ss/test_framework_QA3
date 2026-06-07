import json
from pathlib import Path
from typing import Any, Dict


class SchemaLoader:
    """Carrega schemas JSON versionados a partir do filesystem."""

    @staticmethod
    def load(schema_path: str | Path) -> Dict[str, Any]:
        path = Path(schema_path)

        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {path}")

        try:
            with path.open("r", encoding="utf-8") as schema_file:
                loaded_schema = json.load(schema_file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON schema file: {path}") from exc

        if not isinstance(loaded_schema, dict):
            raise ValueError(f"Schema root must be a JSON object: {path}")

        return loaded_schema
