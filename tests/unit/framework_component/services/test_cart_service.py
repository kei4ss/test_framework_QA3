"""Testes unitários para CartService.

Verifica o comportamento do service de carrinhos usando
mocks do RequestManager, sem fazer chamadas reais à API.
"""

import pytest
from unittest.mock import MagicMock

from src.services.cart_service import CartService


MOCK_CART = {
    "id": 1,
    "userId": 1,
    "date": "2020-03-02T00:00:00.000Z",
    "products": [
        {"productId": 1, "quantity": 4},
        {"productId": 2, "quantity": 1},
        {"productId": 3, "quantity": 6},
    ],
}

NEW_CART_PAYLOAD = {
    "userId": 1,
    "date": "2024-01-01",
    "products": [
        {"productId": 1, "quantity": 2},
        {"productId": 3, "quantity": 1},
    ],
}


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def cart_service(mock_client):
    return CartService(client=mock_client)


def _mock_json_response(data, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data
    return response


@pytest.mark.unit
@pytest.mark.framework_component
class TestCartServiceGetAll:
    """Testes do método CartService.get_all()."""

    def test_get_all_deve_chamar_get_carts(self, cart_service, mock_client):
        """get_all() deve chamar GET /carts."""
        mock_client.get.return_value = _mock_json_response([MOCK_CART])

        cart_service.get_all()

        mock_client.get.assert_called_once_with("/carts", params=None)

    def test_get_all_com_limit_deve_incluir_parametro(self, cart_service, mock_client):
        """get_all(limit=3) deve incluir limit nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_CART])

        cart_service.get_all(limit=3)

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["limit"] == 3

    def test_get_all_com_sort_deve_incluir_parametro(self, cart_service, mock_client):
        """get_all(sort='asc') deve incluir sort nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_CART])

        cart_service.get_all(sort="asc")

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["sort"] == "asc"

    def test_get_all_com_filtro_de_data(self, cart_service, mock_client):
        """get_all(startdate=..., enddate=...) deve incluir ambas as datas nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_CART])

        cart_service.get_all(startdate="2020-01-01", enddate="2020-12-31")

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["startdate"] == "2020-01-01"
        assert kwargs["params"]["enddate"] == "2020-12-31"

    def test_get_all_deve_retornar_lista_de_carrinhos(self, cart_service, mock_client):
        """get_all() deve retornar a lista desserializada."""
        mock_client.get.return_value = _mock_json_response([MOCK_CART])

        result = cart_service.get_all()

        assert isinstance(result, list)
        assert result[0]["userId"] == MOCK_CART["userId"]

    def test_get_all_raw_deve_retornar_response(self, cart_service, mock_client):
        """get_all_raw() deve retornar o objeto Response."""
        mock_response = _mock_json_response([MOCK_CART])
        mock_client.get.return_value = mock_response

        result = cart_service.get_all_raw()

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestCartServiceGetById:
    """Testes do método CartService.get_by_id()."""

    def test_get_by_id_deve_chamar_endpoint_correto(self, cart_service, mock_client):
        """get_by_id(1) deve chamar GET /carts/1."""
        mock_client.get.return_value = _mock_json_response(MOCK_CART)

        cart_service.get_by_id(1)

        mock_client.get.assert_called_once_with("/carts/1")

    def test_get_by_id_deve_retornar_carrinho(self, cart_service, mock_client):
        """get_by_id() deve retornar o dict do carrinho."""
        mock_client.get.return_value = _mock_json_response(MOCK_CART)

        result = cart_service.get_by_id(1)

        assert result["id"] == 1
        assert isinstance(result["products"], list)

    def test_get_by_id_raw_deve_retornar_response(self, cart_service, mock_client):
        """get_by_id_raw() deve retornar o Response completo."""
        mock_response = _mock_json_response(MOCK_CART)
        mock_client.get.return_value = mock_response

        result = cart_service.get_by_id_raw(1)

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestCartServiceGetByUser:
    """Testes do método CartService.get_by_user()."""

    def test_get_by_user_deve_chamar_endpoint_correto(self, cart_service, mock_client):
        """get_by_user(1) deve chamar GET /carts/user/1."""
        mock_client.get.return_value = _mock_json_response([MOCK_CART])

        cart_service.get_by_user(1)

        mock_client.get.assert_called_once_with("/carts/user/1")

    def test_get_by_user_deve_retornar_lista(self, cart_service, mock_client):
        """get_by_user() deve retornar a lista de carrinhos do usuário."""
        mock_client.get.return_value = _mock_json_response([MOCK_CART])

        result = cart_service.get_by_user(1)

        assert isinstance(result, list)
        assert result[0]["userId"] == 1


@pytest.mark.unit
@pytest.mark.framework_component
class TestCartServiceCreate:
    """Testes do método CartService.create()."""

    def test_create_deve_chamar_post_carts(self, cart_service, mock_client):
        """create() deve chamar POST /carts com o payload."""
        created = {**NEW_CART_PAYLOAD, "id": 8}
        mock_client.post.return_value = _mock_json_response(created)

        cart_service.create(NEW_CART_PAYLOAD)

        mock_client.post.assert_called_once_with("/carts", json=NEW_CART_PAYLOAD)

    def test_create_deve_retornar_carrinho_com_id(self, cart_service, mock_client):
        """create() deve retornar o carrinho criado com id."""
        created = {**NEW_CART_PAYLOAD, "id": 8}
        mock_client.post.return_value = _mock_json_response(created)

        result = cart_service.create(NEW_CART_PAYLOAD)

        assert result["id"] == 8
        assert result["userId"] == NEW_CART_PAYLOAD["userId"]

    def test_create_raw_deve_retornar_response(self, cart_service, mock_client):
        """create_raw() deve retornar o objeto Response completo."""
        mock_response = _mock_json_response({**NEW_CART_PAYLOAD, "id": 8})
        mock_client.post.return_value = mock_response

        result = cart_service.create_raw(NEW_CART_PAYLOAD)

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestCartServiceUpdate:
    """Testes dos métodos de atualização do CartService."""

    def test_update_deve_chamar_put_com_id_correto(self, cart_service, mock_client):
        """update(1, payload) deve chamar PUT /carts/1."""
        mock_client.put.return_value = _mock_json_response(MOCK_CART)

        cart_service.update(1, NEW_CART_PAYLOAD)

        mock_client.put.assert_called_once_with("/carts/1", json=NEW_CART_PAYLOAD)

    def test_update_deve_retornar_carrinho_atualizado(self, cart_service, mock_client):
        """update() deve retornar o dict do carrinho atualizado."""
        updated = {**MOCK_CART, "userId": 3}
        mock_client.put.return_value = _mock_json_response(updated)

        result = cart_service.update(1, NEW_CART_PAYLOAD)

        assert result["userId"] == 3

    def test_partial_update_deve_chamar_patch(self, cart_service, mock_client):
        """partial_update(1, payload) deve chamar PATCH /carts/1."""
        mock_client.patch.return_value = _mock_json_response(MOCK_CART)

        cart_service.partial_update(1, {"userId": 7})

        mock_client.patch.assert_called_once_with("/carts/1", json={"userId": 7})

    def test_partial_update_deve_retornar_carrinho_parcialmente_atualizado(
        self, cart_service, mock_client
    ):
        """partial_update() deve retornar o carrinho após PATCH."""
        updated = {**MOCK_CART, "userId": 7}
        mock_client.patch.return_value = _mock_json_response(updated)

        result = cart_service.partial_update(1, {"userId": 7})

        assert result["userId"] == 7

    def test_partial_update_raw_deve_retornar_response(self, cart_service, mock_client):
        """partial_update_raw() deve retornar o Response completo."""
        mock_response = _mock_json_response(MOCK_CART)
        mock_client.patch.return_value = mock_response

        result = cart_service.partial_update_raw(1, {"userId": 7})

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestCartServiceDelete:
    """Testes do método CartService.delete()."""

    def test_delete_deve_chamar_delete_com_id_correto(self, cart_service, mock_client):
        """delete(1) deve chamar DELETE /carts/1."""
        mock_client.delete.return_value = _mock_json_response(MOCK_CART)

        cart_service.delete(1)

        mock_client.delete.assert_called_once_with("/carts/1")

    def test_delete_deve_retornar_carrinho_deletado(self, cart_service, mock_client):
        """delete() deve retornar o dict do carrinho deletado."""
        mock_client.delete.return_value = _mock_json_response(MOCK_CART)

        result = cart_service.delete(1)

        assert result["id"] == 1

    def test_delete_raw_deve_retornar_response(self, cart_service, mock_client):
        """delete_raw() deve retornar o objeto Response completo."""
        mock_response = _mock_json_response(MOCK_CART)
        mock_client.delete.return_value = mock_response

        result = cart_service.delete_raw(1)

        assert result is mock_response
