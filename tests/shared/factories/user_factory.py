from pathlib import Path

from src.infrastructure.schemaValidation import SchemaLoader

SCHEMAS_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "schemas"
    / "jsonplaceholder"
)


class UserFactory:
    """Factory centralizada para payloads de usuários."""

    USER_SCHEMA = SchemaLoader.load(SCHEMAS_DIR / "user_schema.json")
    USERS_LIST_SCHEMA = SchemaLoader.load(SCHEMAS_DIR / "users_list_schema.json")
    CREATE_USER_RESPONSE_SCHEMA = SchemaLoader.load(
        SCHEMAS_DIR / "create_user_response_schema.json"
    )

    @staticmethod
    def build(**overrides):
        payload = {
            "email": "qa_test@example.com",
            "username": "qa_tester",
            "password": "senha123",
            "name": {"firstname": "QA", "lastname": "Tester"},
            "address": {
                "city": "Brasilia",
                "street": "Rua QA",
                "number": 1,
                "zipcode": "00000-000",
                "geolocation": {"lat": "0", "long": "0"},
            },
            "phone": "99999-9999",
        }
        payload.update(overrides)
        return payload
    

