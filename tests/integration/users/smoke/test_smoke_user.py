import pytest

from tests.shared.factories.user_factory import UserFactory
from tests.shared.helpers.response_assertions import (
    USER_REQUIRED_KEYS,
    assert_successful_list_response,
    assert_user_has_required_fields,
    assert_schema
)

@pytest.mark.smoke
class TestGET():
    def test_deve_retornar_todos_os_usuarios(self, client):
        users = assert_successful_list_response(
            client.get("/users")
        )
        for u in users:assert_user_has_required_fields(u)

    def test_a_user_have_correct_schema(self, client):
        user = client.get("/users/1")
        assert_schema(user, UserFactory.USER_SCHEMA)

