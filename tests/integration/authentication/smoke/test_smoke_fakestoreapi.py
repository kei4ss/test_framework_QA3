"""Smoke tests para todos os endpoints da FakeStore API.

Testes rápidos para verificar que a API está online e respondendo
corretamente para cada recurso principal (Products, Carts, Users, Auth).

Execute antes de qualquer suite de regressão.
"""

import pytest

from src.infrastructure.requestManager.request_manager import RequestManager

BASE_URL = "https://fakestoreapi.com"


@pytest.fixture
def client():
    """RequestManager configurado para a FakeStore API."""
    return RequestManager(base_url=BASE_URL, timeout=10)


@pytest.mark.integration
class TestSmokeProducts:
    """Smoke tests para o recurso Products."""

    def test_api_products_esta_acessivel(self, client):
        """GET /products deve retornar 200 — API de produtos está online."""
        response = client.get("/products")
        assert response.status_code == 200

    def test_api_product_por_id_esta_acessivel(self, client):
        """GET /products/1 deve retornar 200 — busca por ID está funcional."""
        response = client.get("/products/1")
        assert response.status_code == 200

    def test_api_categories_esta_acessivel(self, client):
        """GET /products/categories deve retornar 200 — categorias disponíveis."""
        response = client.get("/products/categories")
        assert response.status_code == 200


@pytest.mark.integration
class TestSmokeCarts:
    """Smoke tests para o recurso Carts."""

    def test_api_carts_esta_acessivel(self, client):
        """GET /carts deve retornar 200 — API de carrinhos está online."""
        response = client.get("/carts")
        assert response.status_code == 200

    def test_api_cart_por_id_esta_acessivel(self, client):
        """GET /carts/1 deve retornar 200 — busca de carrinho por ID está funcional."""
        response = client.get("/carts/1")
        assert response.status_code == 200


@pytest.mark.integration
class TestSmokeUsers:
    """Smoke tests para o recurso Users."""

    def test_api_users_esta_acessivel(self, client):
        """GET /users deve retornar 200 — API de usuários está online."""
        response = client.get("/users")
        assert response.status_code == 200

    def test_api_user_por_id_esta_acessivel(self, client):
        """GET /users/1 deve retornar 200 — busca de usuário por ID está funcional."""
        response = client.get("/users/1")
        assert response.status_code == 200


@pytest.mark.integration
class TestSmokeAuth:
    """Smoke tests para o endpoint de Auth."""

    def test_api_auth_login_esta_acessivel(self, client):
        """POST /auth/login deve retornar 200 e um token — autenticação funcional."""
        response = client.post("/auth/login", json={
            "username": "mor_2314",
            "password": "83r5^_",
        })
        body = response.json()

        assert response.status_code == 200
        assert "token" in body