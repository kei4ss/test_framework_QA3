from pathlib import Path

import pytest

from src.infrastructure.schemaValidation.schema_loader import SchemaLoader
from src.infrastructure.schemaValidation.schema_validator import (
    SchemaValidationError,
    SchemaValidator,
)


SCHEMAS_DIR = (
    Path(__file__).resolve().parents[3]
    / "shared"
    / "fixtures"
    / "schemas"
    / "jsonplaceholder"
)


@pytest.fixture
def user_schema():
    return SchemaLoader.load(SCHEMAS_DIR / "user_schema.json")


@pytest.fixture
def users_list_schema():
    return SchemaLoader.load(SCHEMAS_DIR / "users_list_schema.json")


@pytest.fixture
def create_user_response_schema():
    return SchemaLoader.load(SCHEMAS_DIR / "create_user_response_schema.json")


@pytest.mark.framework_component
@pytest.mark.unit
def test_should_validate_single_object_against_schema(user_schema):
    payload = {
        "id": 1,
        "name": {
            "firstname": "test",
            "lastname": "user"
        },
        "username": "Bret",
        "email": "leanne@example.com",
        "password": "senhaSegura123"
    }

    assert SchemaValidator.validate(payload, user_schema) is True


@pytest.mark.framework_component
@pytest.mark.unit
def test_should_validate_users_list_against_schema(users_list_schema):
    payload = [
        {
            "id": 1,
            "name": "Leanne Graham",
            "username": "Bret",
            "email": "leanne@example.com",
        },
        {
            "id": 2,
            "name": "Ervin Howell",
            "username": "Antonette",
            "email": "ervin@example.com",
        },
    ]

    assert SchemaValidator.validate_many(payload, users_list_schema) is True


@pytest.mark.framework_component
@pytest.mark.unit
def test_should_raise_when_required_field_is_missing(user_schema):
    payload = {
        "id": 1,
        "name": "Leanne Graham",
        "email": "leanne@example.com",
    }

    with pytest.raises(SchemaValidationError, match="username"):
        SchemaValidator.validate(payload, user_schema)


@pytest.mark.framework_component
@pytest.mark.unit
def test_should_raise_when_field_type_is_incorrect(user_schema):
    payload = {
        "id": "1",
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "leanne@example.com",
    }

    with pytest.raises(SchemaValidationError, match="path=id"):
        SchemaValidator.validate(payload, user_schema)


@pytest.mark.framework_component
@pytest.mark.unit
def test_should_validate_create_user_response(create_user_response_schema):
    payload = {
        "id": 11,
        "name": "Test User",
        "username": "atividade5_user",
        "email": "test@example.com",
    }

    assert SchemaValidator.validate(payload, create_user_response_schema) is True


@pytest.mark.framework_component
@pytest.mark.unit
def test_should_collect_readable_validation_errors(user_schema):
    payload = {
        "id": "invalid",
        "name": "Leanne Graham",
        "username": "Bret",
    }

    errors = SchemaValidator.collect_errors(payload, user_schema)

    assert any("path=id" in error for error in errors)
    assert any("email" in error for error in errors)
