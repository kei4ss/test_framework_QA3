"""Testes unitários para ProductService.

Verifica o comportamento do service de produtos usando
mocks do RequestManager, sem fazer chamadas reais à API.
"""

import pytest
from unittest.mock import MagicMock

from src.services.product_service import ProductService


MOCK_PRODUCT = {
    "id": 1,
    "title": "Fjallraven - Foldsack No. 1 Backpack",
    "price": 109.95,
    "description": "Your perfect pack for everyday use.",
    "category": "men's clothing",
    "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
}

VALID_CATEGORIES = ["electronics", "jewelery", "men's clothing", "women's clothing"]

NEW_PRODUCT_PAYLOAD = {
    "title": "Produto de Teste QA",
    "price": 49.99,
    "description": "Produto criado para fins de teste",
    "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
    "category": "electronics",
}


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def product_service(mock_client):
    return ProductService(client=mock_client)


def _mock_json_response(data, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data
    return response


@pytest.mark.unit
@pytest.mark.framework_component
class TestProductServiceGetAll:
    """Testes do método ProductService.get_all()."""

    def test_get_all_deve_chamar_get_products(self, product_service, mock_client):
        """get_all() deve chamar GET /products."""
        mock_client.get.return_value = _mock_json_response([MOCK_PRODUCT])

        product_service.get_all()

        mock_client.get.assert_called_once_with("/products", params=None)

    def test_get_all_com_limit_deve_incluir_parametro(self, product_service, mock_client):
        """get_all(limit=5) deve passar limit nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_PRODUCT])

        product_service.get_all(limit=5)

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["limit"] == 5

    def test_get_all_com_sort_deve_incluir_parametro(self, product_service, mock_client):
        """get_all(sort='desc') deve passar sort nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_PRODUCT])

        product_service.get_all(sort="desc")

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["sort"] == "desc"

    def test_get_all_deve_retornar_lista_de_produtos(self, product_service, mock_client):
        """get_all() deve retornar a lista desserializada."""
        mock_client.get.return_value = _mock_json_response([MOCK_PRODUCT])

        result = product_service.get_all()

        assert isinstance(result, list)
        assert result[0]["id"] == 1

    def test_get_all_raw_deve_retornar_response(self, product_service, mock_client):
        """get_all_raw() deve retornar o objeto Response."""
        mock_response = _mock_json_response([MOCK_PRODUCT])
        mock_client.get.return_value = mock_response

        result = product_service.get_all_raw()

        assert result is mock_response


@pytest.mark.unit
@pytest.mark.framework_component
class TestProductServiceGetById:
    """Testes do método ProductService.get_by_id()."""

    def test_get_by_id_deve_chamar_endpoint_correto(self, product_service, mock_client):
        """get_by_id(1) deve chamar GET /products/1."""
        mock_client.get.return_value = _mock_json_response(MOCK_PRODUCT)

        product_service.get_by_id(1)

        mock_client.get.assert_called_once_with("/products/1")

    def test_get_by_id_deve_retornar_produto(self, product_service, mock_client):
        """get_by_id() deve retornar o dict do produto."""
        mock_client.get.return_value = _mock_json_response(MOCK_PRODUCT)

        result = product_service.get_by_id(1)

        assert result["id"] == 1
        assert result["price"] == 109.95

    def test_get_by_id_deve_retornar_none_para_id_inexistente(
        self, product_service, mock_client
    ):
        """get_by_id() para ID inexistente retorna None (comportamento da FakeStore)."""
        mock_client.get.return_value = _mock_json_response(None)

        result = product_service.get_by_id(99999)

        assert result is None


@pytest.mark.unit
@pytest.mark.framework_component
class TestProductServiceGetCategories:
    """Testes dos métodos de categoria do ProductService."""

    def test_get_categories_deve_chamar_endpoint_correto(
        self, product_service, mock_client
    ):
        """get_categories() deve chamar GET /products/categories."""
        mock_client.get.return_value = _mock_json_response(VALID_CATEGORIES)

        product_service.get_categories()

        mock_client.get.assert_called_once_with("/products/categories")

    def test_get_categories_deve_retornar_lista_de_strings(
        self, product_service, mock_client
    ):
        """get_categories() deve retornar lista de strings."""
        mock_client.get.return_value = _mock_json_response(VALID_CATEGORIES)

        result = product_service.get_categories()

        assert isinstance(result, list)
        assert all(isinstance(c, str) for c in result)

    def test_get_by_category_deve_chamar_endpoint_com_categoria(
        self, product_service, mock_client
    ):
        """get_by_category('electronics') deve chamar GET /products/category/electronics."""
        mock_client.get.return_value = _mock_json_response([MOCK_PRODUCT])

        product_service.get_by_category("electronics")

        mock_client.get.assert_called_once_with(
            "/products/category/electronics", params=None
        )

    def test_get_by_category_com_limit_deve_incluir_parametro(
        self, product_service, mock_client
    ):
        """get_by_category() com limit deve incluir nos params."""
        mock_client.get.return_value = _mock_json_response([MOCK_PRODUCT])

        product_service.get_by_category("electronics", limit=3)

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["limit"] == 3


@pytest.mark.unit
@pytest.mark.framework_component
class TestProductServiceCreate:
    """Testes do método ProductService.create()."""

    def test_create_deve_chamar_post_products(self, product_service, mock_client):
        """create() deve chamar POST /products com o payload."""
        created = {**NEW_PRODUCT_PAYLOAD, "id": 21}
        mock_client.post.return_value = _mock_json_response(created, status_code=201)

        product_service.create(NEW_PRODUCT_PAYLOAD)

        mock_client.post.assert_called_once_with("/products", json=NEW_PRODUCT_PAYLOAD)

    def test_create_deve_retornar_produto_com_id(self, product_service, mock_client):
        """create() deve retornar o produto criado com id."""
        created = {**NEW_PRODUCT_PAYLOAD, "id": 21}
        mock_client.post.return_value = _mock_json_response(created, status_code=201)

        result = product_service.create(NEW_PRODUCT_PAYLOAD)

        assert result["id"] == 21
        assert result["title"] == NEW_PRODUCT_PAYLOAD["title"]

    def test_create_raw_deve_retornar_response(self, product_service, mock_client):
        """create_raw() deve retornar o Response completo (com status_code 201)."""
        mock_response = _mock_json_response({**NEW_PRODUCT_PAYLOAD, "id": 21}, status_code=201)
        mock_client.post.return_value = mock_response

        result = product_service.create_raw(NEW_PRODUCT_PAYLOAD)

        assert result is mock_response
        assert result.status_code == 201


@pytest.mark.unit
@pytest.mark.framework_component
class TestProductServiceUpdate:
    """Testes dos métodos de atualização do ProductService."""

    def test_update_deve_chamar_put_com_id_correto(self, product_service, mock_client):
        """update(1, payload) deve chamar PUT /products/1."""
        mock_client.put.return_value = _mock_json_response(MOCK_PRODUCT)

        product_service.update(1, NEW_PRODUCT_PAYLOAD)

        mock_client.put.assert_called_once_with("/products/1", json=NEW_PRODUCT_PAYLOAD)

    def test_partial_update_deve_chamar_patch(self, product_service, mock_client):
        """partial_update(1, payload) deve chamar PATCH /products/1."""
        mock_client.patch.return_value = _mock_json_response(MOCK_PRODUCT)

        product_service.partial_update(1, {"price": 299.99})

        mock_client.patch.assert_called_once_with(
            "/products/1", json={"price": 299.99}
        )

    def test_partial_update_deve_retornar_produto_atualizado(
        self, product_service, mock_client
    ):
        """partial_update() deve retornar o produto após atualização."""
        updated = {**MOCK_PRODUCT, "price": 299.99}
        mock_client.patch.return_value = _mock_json_response(updated)

        result = product_service.partial_update(1, {"price": 299.99})

        assert result["price"] == 299.99


@pytest.mark.unit
@pytest.mark.framework_component
class TestProductServiceDelete:
    """Testes do método ProductService.delete()."""

    def test_delete_deve_chamar_delete_com_id_correto(self, product_service, mock_client):
        """delete(1) deve chamar DELETE /products/1."""
        mock_client.delete.return_value = _mock_json_response(MOCK_PRODUCT)

        product_service.delete(1)

        mock_client.delete.assert_called_once_with("/products/1")

    def test_delete_deve_retornar_produto_deletado(self, product_service, mock_client):
        """delete() deve retornar o dict do produto deletado."""
        mock_client.delete.return_value = _mock_json_response(MOCK_PRODUCT)

        result = product_service.delete(1)

        assert result["id"] == 1
