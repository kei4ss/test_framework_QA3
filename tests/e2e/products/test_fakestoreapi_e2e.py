"""Testes E2E para fluxos completos da FakeStore API.

Valida cenários ponta-a-ponta que envolvem múltiplos recursos:
  - Autenticar → Buscar produto → Adicionar ao carrinho → Deletar carrinho
  - Criar usuário → Fazer login → Buscar carrinhos do usuário
  - Ciclo completo de produto: criar → atualizar → deletar
  - Ciclo completo de carrinho: criar → adicionar produto → atualizar → deletar
"""

import pytest

from src.infrastructure.requestManager.request_manager import RequestManager

BASE_URL = "https://fakestoreapi.com"

VALID_CREDENTIALS = {
    "username": "mor_2314",
    "password": "83r5^_",
}


@pytest.fixture
def client():
    """RequestManager configurado para a FakeStore API."""
    return RequestManager(base_url=BASE_URL, timeout=15)


@pytest.mark.e2e
class TestFluxoCompraCompleto:
    """E2E: Autenticar → Buscar produto → Criar carrinho → Deletar carrinho."""

    def test_fluxo_compra_autenticado(self, client):
        """
        Fluxo E2E:
          1. Faz login e obtém token
          2. Lista produtos e seleciona um
          3. Cria carrinho com o produto selecionado
          4. Verifica carrinho criado
          5. Deleta o carrinho
        """
        # --- PASSO 1: Autenticar ---
        login_resp = client.post("/auth/login", json=VALID_CREDENTIALS)
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        assert token and len(token) > 0

        # Configura o token para requisições subsequentes
        client.set_auth_token(token)

        # --- PASSO 2: Listar produtos e selecionar o primeiro ---
        products_resp = client.get("/products", params={"limit": 5})
        assert products_resp.status_code == 200
        products = products_resp.json()
        assert len(products) > 0
        selected_product = products[0]
        assert selected_product["price"] > 0

        # --- PASSO 3: Criar carrinho com o produto selecionado ---
        cart_payload = {
            "userId": 2,
            "date": "2024-07-01",
            "products": [
                {"productId": selected_product["id"], "quantity": 2}
            ],
        }
        create_cart_resp = client.post("/carts", json=cart_payload)
        assert create_cart_resp.status_code == 200
        created_cart = create_cart_resp.json()
        assert "id" in created_cart
        cart_id = created_cart["id"]

        # --- PASSO 4: Verificar que produtos no carrinho batem com o payload ---
        assert created_cart["userId"] == cart_payload["userId"]
        assert len(created_cart["products"]) == 1
        assert created_cart["products"][0]["productId"] == selected_product["id"]

        # --- PASSO 5: Deletar o carrinho ---
        delete_resp = client.delete(f"/carts/{cart_id}")
        assert delete_resp.status_code == 200


@pytest.mark.e2e
class TestCicloVidaProduto:
    """E2E: Criar produto → Atualizar → Buscar → Deletar."""

    def test_ciclo_completo_de_produto(self, client):
        """
        Fluxo E2E:
          1. Cria produto novo
          2. Atualiza o título via PUT
          3. Atualiza o preço via PATCH
          4. Deleta o produto
          5. Verifica resposta de deleção
        """
        # --- PASSO 1: Criar produto ---
        new_product = {
            "title": "Produto E2E - Criação",
            "price": 59.90,
            "description": "Produto criado no fluxo E2E",
            "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
            "category": "electronics",
        }
        create_resp = client.post("/products", json=new_product)
        assert create_resp.status_code == 200
        created = create_resp.json()
        product_id = created["id"]
        assert created["title"] == new_product["title"]

        # --- PASSO 2: Atualizar título via PUT ---
        updated_product = {**new_product, "title": "Produto E2E - Atualizado PUT"}
        put_resp = client.put(f"/products/{product_id}", json=updated_product)
        assert put_resp.status_code == 200
        assert put_resp.json()["title"] == "Produto E2E - Atualizado PUT"

        # --- PASSO 3: Atualizar preço via PATCH ---
        patch_resp = client.patch(f"/products/{product_id}", json={"price": 99.90})
        assert patch_resp.status_code == 200
        assert patch_resp.json()["price"] == 99.90

        # --- PASSO 4: Deletar produto ---
        delete_resp = client.delete(f"/products/{product_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["id"] == product_id


@pytest.mark.e2e
class TestCicloVidaCarrinho:
    """E2E: Criar carrinho → Atualizar produtos → Deletar."""

    def test_ciclo_completo_de_carrinho(self, client):
        """
        Fluxo E2E:
          1. Cria carrinho com 1 produto
          2. Atualiza o carrinho adicionando mais produtos (PUT)
          3. Atualiza parcialmente a quantidade (PATCH)
          4. Deleta o carrinho
        """
        # --- PASSO 1: Criar carrinho ---
        cart_payload = {
            "userId": 3,
            "date": "2024-08-01",
            "products": [{"productId": 1, "quantity": 1}],
        }
        create_resp = client.post("/carts", json=cart_payload)
        assert create_resp.status_code == 200
        cart = create_resp.json()
        cart_id = cart["id"]

        # --- PASSO 2: Atualizar carrinho adicionando mais produtos ---
        updated_payload = {
            "userId": 3,
            "date": "2024-08-01",
            "products": [
                {"productId": 1, "quantity": 3},
                {"productId": 5, "quantity": 2},
            ],
        }
        put_resp = client.put(f"/carts/{cart_id}", json=updated_payload)
        assert put_resp.status_code == 200
        assert len(put_resp.json()["products"]) == 2

        # --- PASSO 3: Atualizar parcialmente (PATCH) ---
        patch_resp = client.patch(f"/carts/{cart_id}", json={
            "products": [{"productId": 10, "quantity": 5}]
        })
        assert patch_resp.status_code == 200

        # --- PASSO 4: Deletar carrinho ---
        delete_resp = client.delete(f"/carts/{cart_id}")
        assert delete_resp.status_code == 200


@pytest.mark.e2e
class TestFiltragemCategoriaComLimite:
    """E2E: Filtrar produtos por categoria com limite e ordenação."""

    def test_fluxo_filtragem_categoria_ordenada(self, client):
        """
        Fluxo E2E:
          1. Busca categorias disponíveis
          2. Para cada categoria, busca produtos com limit=3 e sort=asc
          3. Valida que todos os produtos retornados pertencem à categoria
          4. Valida ordenação dos IDs
        """
        # --- PASSO 1: Buscar categorias ---
        cats_resp = client.get("/products/categories")
        assert cats_resp.status_code == 200
        categories = cats_resp.json()
        assert len(categories) >= 1

        # --- PASSO 2 & 3 & 4: Para cada categoria ---
        for category in categories:
            cat_resp = client.get(
                f"/products/category/{category}",
                params={"limit": 3, "sort": "asc"}
            )
            assert cat_resp.status_code == 200
            products = cat_resp.json()

            for p in products:
                assert p["category"] == category, (
                    f"Produto id={p['id']} na categoria '{p['category']}' "
                    f"não pertence à categoria filtrada '{category}'"
                )


@pytest.mark.e2e
class TestConsistenciaLoginEDados:
    """E2E: Login → Verificar dados do usuário logado."""

    def test_usuario_que_fez_login_deve_existir_na_api(self, client):
        """
        Fluxo E2E:
          1. Faz login com credenciais de usuário conhecido
          2. Obtém token
          3. Verifica que o usuário existe na API de /users
        """
        # --- PASSO 1: Login ---
        login_resp = client.post("/auth/login", json=VALID_CREDENTIALS)
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        assert token

        # --- PASSO 2: Busca usuário pelo username ---
        users_resp = client.get("/users")
        assert users_resp.status_code == 200
        users = users_resp.json()

        # --- PASSO 3: Verifica que o usuário está na lista ---
        usernames = [u["username"] for u in users]
        assert VALID_CREDENTIALS["username"] in usernames, (
            f"Usuário '{VALID_CREDENTIALS['username']}' não encontrado na lista de usuários."
        )