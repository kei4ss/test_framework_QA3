"""Camada de serviço do framework de testes.

Este pacote expõe os services que encapsulam as regras de negócio
e as chamadas à FakeStore API, organizando as ações reutilizáveis
pelos testes de integração e E2E.

Services disponíveis:
  - AuthService    : autenticação (POST /auth/login)
  - UserService    : operações CRUD de usuários (/users)
  - ProductService : operações CRUD de produtos (/products)
  - CartService    : operações CRUD de carrinhos (/carts)

Uso típico em testes::

    from src.services import AuthService, UserService, ProductService, CartService
    from src.infrastructure.requestManager.request_manager import RequestManager

    @pytest.fixture
    def client():
        return RequestManager(base_url="https://fakestoreapi.com", timeout=15)

    def test_fluxo_compra(client):
        auth    = AuthService(client)
        products = ProductService(client)
        carts   = CartService(client)

        token = auth.login("mor_2314", "83r5^_")
        client.set_auth_token(token)

        lista = products.get_all(limit=1)
        cart  = carts.create({
            "userId": 2,
            "date": "2024-01-01",
            "products": [{"productId": lista[0]["id"], "quantity": 1}],
        })
        assert cart["id"] is not None
        carts.delete(cart["id"])
"""

from src.services.auth_service import AuthService
from src.services.base_service import BaseService
from src.services.cart_service import CartService
from src.services.product_service import ProductService
from src.services.user_service import UserService

__all__ = [
    "BaseService",
    "AuthService",
    "UserService",
    "ProductService",
    "CartService",
]
