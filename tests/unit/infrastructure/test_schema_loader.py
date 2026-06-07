import json

import pytest

from src.infrastructure.schemaValidation.schema_loader import SchemaLoader


def test_should_load_schema_from_json_file(tmp_path):
    schema_path = tmp_path / "user_schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
            }
        ),
        encoding="utf-8",
    )

    result = SchemaLoader.load(schema_path)

    assert result["type"] == "object"
    assert result["properties"]["id"]["type"] == "integer"


def test_should_raise_when_schema_file_does_not_exist(tmp_path):
    missing_schema = tmp_path / "missing_schema.json"

    with pytest.raises(FileNotFoundError, match="Schema file not found"):
        SchemaLoader.load(missing_schema)


def test_should_raise_when_schema_json_is_invalid(tmp_path):
    invalid_schema = tmp_path / "invalid_schema.json"
    invalid_schema.write_text("{invalid json}", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON schema file"):
        SchemaLoader.load(invalid_schema)


def test_should_raise_when_schema_root_is_not_object(tmp_path):
    invalid_root_schema = tmp_path / "schema_array.json"
    invalid_root_schema.write_text(json.dumps([{"type": "object"}]), encoding="utf-8")

    with pytest.raises(ValueError, match="Schema root must be a JSON object"):
        SchemaLoader.load(invalid_root_schema)
