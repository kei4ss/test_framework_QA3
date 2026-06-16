"""Testes unitários para UserService.

Verifica o comportamento do service de usuários usando
mocks do RequestManager, sem fazer chamadas reais à API.
"""

import pytest
from unittest.mock import MagicMock

from src.services.user_service import UserService


MOCK_USER = {
    "id": 1,
    "email": "john@gmail.com",
    "username": "johnd",
    "password": "m38rmF$",
    "name": {"firstname": "john", "lastname": "doe"},
    "address": {
        "city": "kilcoole",
        "street": "7835 new road",
        "number": 3,
        "zipcode": "12926-3874",
        "geolocation": {"lat": "-37.3159", "long": "81.1496"},
    },
    "phone": "1-570-236-7033",
}

NEW_USER_PAYLOAD = {
    "email": "qa@test.com",
    "username": "qa_tester",
    "password": "senha123",
    "name": {"firstname": "QA", "lastname": "Tester"},
    "address": {
        "city": "Brasília",
        "street": "QS 1 Conj 10",
        "number": 42,
        "zipcode": "71980-000",
        "geolocation": {"lat": "-15.78", "long": "-47.93"},
    },
    "phone": "61-99999-0000",
}


@pytest.fixture
def mock_client():
    """RequestManager mockado."""
    return MagicMock()


@pytest.fixture
def user_service(mock_client):
    """UserService com client mockado."""
    return UserService(client=mock_client)


def _mock_json_response(data, status_code=200):
    """Cria um mock de Response com .json() e .status_code configurados."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data
    return response


@pytest.mark.unit
@pytest.mark.framework_component
class TestUserServiceGetAll:
    """Testes do método UserService.get_all()."""

    def test_get_all_deve_chamar_get_users(self, user_service, mock_client):
        """get_all() deve chamar GET /users."""
        mock_client.get.return_value = _mock_json_response([MOCK_USER])

        user_service.get_all()

        mock_client.get.assert_called_once_with("/users", params=None)

    def test_get_all_com_limit_deve_passar_parametro(self, user_service, mock_client):
        """get_all(limit=5) deve incluir limit nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_USER])

        user_service.get_all(limit=5)

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["limit"] == 5

    def test_get_all_com_sort_deve_passar_parametro(self, user_service, mock_client):
        """get_all(sort='asc') deve incluir sort nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_USER])

        user_service.get_all(sort="asc")

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["sort"] == "asc"

    def test_get_all_deve_retornar_lista(self, user_service, mock_client):
        """get_all() deve retornar a lista de usuários desserializada."""
        mock_client.get.return_value = _mock_json_response([MOCK_USER])

        result = user_service.get_all()

        assert isinstance(result, list)
        assert result[0]["id"] == MOCK_USER["id"]

    def test_get_all_raw_deve_retornar_response_completo(self, user_service, mock_client):
        """get_all_raw() deve retornar o objeto Response."""
        mock_response = _mock_json_response([MOCK_USER])
        mock_client.get.return_value = mock_response

        result = user_service.get_all_raw()

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestUserServiceGetById:
    """Testes do método UserService.get_by_id()."""

    def test_get_by_id_deve_chamar_endpoint_correto(self, user_service, mock_client):
        """get_by_id(1) deve chamar GET /users/1."""
        mock_client.get.return_value = _mock_json_response(MOCK_USER)

        user_service.get_by_id(1)

        mock_client.get.assert_called_once_with("/users/1")

    def test_get_by_id_deve_retornar_dicionario(self, user_service, mock_client):
        """get_by_id() deve retornar o dict do usuário."""
        mock_client.get.return_value = _mock_json_response(MOCK_USER)

        result = user_service.get_by_id(1)

        assert result["id"] == 1
        assert result["username"] == "johnd"

    def test_get_by_id_raw_deve_retornar_response(self, user_service, mock_client):
        """get_by_id_raw() deve retornar o Response completo."""
        mock_response = _mock_json_response(MOCK_USER)
        mock_client.get.return_value = mock_response

        result = user_service.get_by_id_raw(1)

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestUserServiceCreate:
    """Testes do método UserService.create()."""

    def test_create_deve_chamar_post_users(self, user_service, mock_client):
        """create() deve chamar POST /users com o payload."""
        created = {**NEW_USER_PAYLOAD, "id": 11}
        mock_client.post.return_value = _mock_json_response(created)

        user_service.create(NEW_USER_PAYLOAD)

        mock_client.post.assert_called_once_with("/users", json=NEW_USER_PAYLOAD)

    def test_create_deve_retornar_usuario_com_id(self, user_service, mock_client):
        """create() deve retornar o dict do usuário criado com id."""
        created = {**NEW_USER_PAYLOAD, "id": 11}
        mock_client.post.return_value = _mock_json_response(created)

        result = user_service.create(NEW_USER_PAYLOAD)

        assert result["id"] == 11
        assert result["email"] == NEW_USER_PAYLOAD["email"]

    def test_create_raw_deve_retornar_response(self, user_service, mock_client):
        """create_raw() deve retornar o objeto Response completo."""
        mock_response = _mock_json_response({**NEW_USER_PAYLOAD, "id": 11})
        mock_client.post.return_value = mock_response

        result = user_service.create_raw(NEW_USER_PAYLOAD)

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestUserServiceUpdate:
    """Testes dos métodos UserService.update() e partial_update()."""

    def test_update_deve_chamar_put_com_id_correto(self, user_service, mock_client):
        """update(1, payload) deve chamar PUT /users/1."""
        mock_client.put.return_value = _mock_json_response(MOCK_USER)

        user_service.update(1, NEW_USER_PAYLOAD)

        mock_client.put.assert_called_once_with("/users/1", json=NEW_USER_PAYLOAD)

    def test_update_deve_retornar_usuario_atualizado(self, user_service, mock_client):
        """update() deve retornar o dict do usuário atualizado."""
        updated = {**MOCK_USER, "username": "usuario_atualizado"}
        mock_client.put.return_value = _mock_json_response(updated)

        result = user_service.update(1, NEW_USER_PAYLOAD)

        assert result["username"] == "usuario_atualizado"

    def test_partial_update_deve_chamar_patch(self, user_service, mock_client):
        """partial_update(1, payload) deve chamar PATCH /users/1."""
        mock_client.patch.return_value = _mock_json_response(MOCK_USER)

        user_service.partial_update(1, {"phone": "61-88888-1234"})

        mock_client.patch.assert_called_once_with(
            "/users/1", json={"phone": "61-88888-1234"}
        )

    def test_partial_update_deve_retornar_usuario_parcialmente_atualizado(
        self, user_service, mock_client
    ):
        """partial_update() deve retornar o dict do usuário após PATCH."""
        updated = {**MOCK_USER, "phone": "61-88888-1234"}
        mock_client.patch.return_value = _mock_json_response(updated)

        result = user_service.partial_update(1, {"phone": "61-88888-1234"})

        assert result["phone"] == "61-88888-1234"


@pytest.mark.unit
@pytest.mark.framework_component
class TestUserServiceDelete:
    """Testes do método UserService.delete()."""

    def test_delete_deve_chamar_delete_com_id_correto(self, user_service, mock_client):
        """delete(1) deve chamar DELETE /users/1."""
        mock_client.delete.return_value = _mock_json_response(MOCK_USER)

        user_service.delete(1)

        mock_client.delete.assert_called_once_with("/users/1")

    def test_delete_deve_retornar_usuario_deletado(self, user_service, mock_client):
        """delete() deve retornar o dict do usuário deletado."""
        mock_client.delete.return_value = _mock_json_response(MOCK_USER)

        result = user_service.delete(1)

        assert result["id"] == 1

    def test_delete_raw_deve_retornar_response(self, user_service, mock_client):
        """delete_raw() deve retornar o objeto Response completo."""
        mock_response = _mock_json_response(MOCK_USER)
        mock_client.delete.return_value = mock_response

        result = user_service.delete_raw(1)

        assert result is mock_response
