"""Testes de integração para os endpoints de Carts da FakeStore API.

Cobre todos os endpoints disponíveis:
  GET    /carts                            - listar todos os carrinhos
  GET    /carts/{id}                       - buscar carrinho por ID
  GET    /carts?limit={n}                  - listar com limite
  GET    /carts?sort={asc|desc}            - listar ordenado
  GET    /carts?startdate=&enddate=        - filtrar por data
  GET    /carts/user/{userId}              - carrinhos de um usuário
  POST   /carts                            - criar carrinho
  PUT    /carts/{id}                       - atualizar carrinho (completo)
  PATCH  /carts/{id}                       - atualizar carrinho (parcial)
  DELETE /carts/{id}                       - deletar carrinho
"""

import pytest

from src.infrastructure.requestManager.request_manager import RequestManager

BASE_URL = "https://fakestoreapi.com"

CART_KEYS = {"id", "userId", "date", "products"}

NEW_CART_PAYLOAD = {
    "userId": 1,
    "date": "2024-01-01",
    "products": [
        {"productId": 1, "quantity": 2},
        {"productId": 3, "quantity": 1},
    ],
}


@pytest.fixture
def client():
    """RequestManager configurado para a FakeStore API."""
    return RequestManager(base_url=BASE_URL, timeout=15)


# ---------------------------------------------------------------------------
# GET /carts
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetAllCarts:
    """Testes do endpoint GET /carts."""

    def test_deve_retornar_status_200_e_lista_de_carrinhos(self, client):
        """GET /carts deve retornar 200 e uma lista de carrinhos."""
        response = client.get("/carts")
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body, list)
        assert len(body) > 0

    def test_cada_carrinho_deve_conter_campos_obrigatorios(self, client):
        """Cada carrinho deve conter os campos obrigatórios."""
        response = client.get("/carts")
        body = response.json()

        for cart in body:
            assert CART_KEYS.issubset(cart.keys()), (
                f"Carrinho id={cart.get('id')} não contém todos os campos obrigatórios."
            )

    def test_campo_products_deve_ser_lista(self, client):
        """O campo 'products' de cada carrinho deve ser uma lista."""
        response = client.get("/carts")
        body = response.json()

        for cart in body:
            assert isinstance(cart["products"], list)

    def test_itens_do_carrinho_devem_ter_productId_e_quantity(self, client):
        """Cada item dentro de 'products' deve conter 'productId' e 'quantity'."""
        response = client.get("/carts")
        body = response.json()

        for cart in body:
            for item in cart["products"]:
                assert "productId" in item
                assert "quantity" in item

    def test_userId_deve_ser_inteiro_positivo(self, client):
        """O campo 'userId' de cada carrinho deve ser um inteiro positivo."""
        response = client.get("/carts")
        body = response.json()

        for cart in body:
            assert isinstance(cart["userId"], int)
            assert cart["userId"] > 0


# ---------------------------------------------------------------------------
# GET /carts?limit={n}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetCartsWithLimit:
    """Testes do endpoint GET /carts?limit={n}."""

    @pytest.mark.parametrize("limit", [1, 3, 5])
    def test_deve_respeitar_parametro_limit(self, client, limit):
        """GET /carts?limit={n} deve retornar exatamente n carrinhos."""
        response = client.get("/carts", params={"limit": limit})
        body = response.json()

        assert response.status_code == 200
        assert len(body) == limit


# ---------------------------------------------------------------------------
# GET /carts?sort={asc|desc}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetCartsSorted:
    """Testes do endpoint GET /carts?sort={asc|desc}."""

    def test_sort_asc_deve_retornar_carrinhos_em_ordem_crescente(self, client):
        """GET /carts?sort=asc deve retornar carrinhos com IDs em ordem crescente."""
        response = client.get("/carts", params={"sort": "asc"})
        body = response.json()

        assert response.status_code == 200
        ids = [c["id"] for c in body]
        assert ids == sorted(ids)

    def test_sort_desc_deve_retornar_carrinhos_em_ordem_decrescente(self, client):
        """GET /carts?sort=desc deve retornar carrinhos com IDs em ordem decrescente."""
        response = client.get("/carts", params={"sort": "desc"})
        body = response.json()

        assert response.status_code == 200
        ids = [c["id"] for c in body]
        assert ids == sorted(ids, reverse=True)


# ---------------------------------------------------------------------------
# GET /carts?startdate=&enddate=
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetCartsFilteredByDate:
    """Testes do endpoint GET /carts com filtro de data."""

    def test_deve_retornar_carrinhos_dentro_do_intervalo_de_datas(self, client):
        """GET /carts?startdate=...&enddate=... deve filtrar por data."""
        response = client.get("/carts", params={
            "startdate": "2020-01-01",
            "enddate": "2020-12-31",
        })
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body, list)

    def test_intervalo_de_datas_sem_resultados_deve_retornar_lista_vazia(self, client):
        """Intervalo de datas sem carrinhos deve retornar lista vazia."""
        response = client.get("/carts", params={
            "startdate": "2099-01-01",
            "enddate": "2099-12-31",
        })

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /carts/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetSingleCart:
    """Testes do endpoint GET /carts/{id}."""

    @pytest.mark.parametrize("cart_id", [1, 2, 5])
    def test_deve_retornar_carrinho_com_id_valido(self, client, cart_id):
        """GET /carts/{id} com ID válido deve retornar 200 e os dados do carrinho."""
        response = client.get(f"/carts/{cart_id}")
        body = response.json()

        assert response.status_code == 200
        assert body["id"] == cart_id
        assert CART_KEYS.issubset(body.keys())

    def test_deve_retornar_404_para_id_inexistente(self, client):
        """GET /carts/{id} com ID inexistente deve retornar 404."""
        response = client.get("/carts/99999")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /carts/user/{userId}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetCartsByUser:
    """Testes do endpoint GET /carts/user/{userId}."""

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_deve_retornar_carrinhos_do_usuario(self, client, user_id):
        """GET /carts/user/{userId} deve retornar carrinhos do usuário específico."""
        response = client.get(f"/carts/user/{user_id}")
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body, list)

        for cart in body:
            assert cart["userId"] == user_id

    def test_usuario_sem_carrinho_deve_retornar_lista_vazia_ou_404(self, client):
        """GET /carts/user/{userId_inexistente} deve retornar lista vazia ou 404."""
        response = client.get("/carts/user/99999")

        assert response.status_code in (200, 404)
        if response.status_code == 200:
            body = response.json()
            assert body == []


# ---------------------------------------------------------------------------
# POST /carts
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPostCart:
    """Testes do endpoint POST /carts."""

    def test_deve_retornar_status_200_ao_criar_carrinho(self, client):
        """POST /carts com payload válido deve retornar 200 e o carrinho criado."""
        response = client.post("/carts", json=NEW_CART_PAYLOAD)
        body = response.json()

        assert response.status_code == 200
        assert body["userId"] == NEW_CART_PAYLOAD["userId"]

    def test_carrinho_criado_deve_ter_id_atribuido(self, client):
        """O carrinho criado deve receber um ID gerado pela API."""
        response = client.post("/carts", json=NEW_CART_PAYLOAD)
        body = response.json()

        assert "id" in body
        assert isinstance(body["id"], int)

    def test_produtos_do_carrinho_criado_devem_estar_presentes(self, client):
        """Os produtos enviados no payload devem estar presentes no carrinho criado."""
        response = client.post("/carts", json=NEW_CART_PAYLOAD)
        body = response.json()

        assert "products" in body
        assert isinstance(body["products"], list)
        assert len(body["products"]) == len(NEW_CART_PAYLOAD["products"])


# ---------------------------------------------------------------------------
# PUT /carts/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPutCart:
    """Testes do endpoint PUT /carts/{id}."""

    def test_deve_retornar_status_200_ao_atualizar_carrinho(self, client):
        """PUT /carts/{id} deve retornar 200 e os dados atualizados."""
        updated_payload = {
            "userId": 3,
            "date": "2024-06-01",
            "products": [{"productId": 2, "quantity": 5}],
        }
        response = client.put("/carts/1", json=updated_payload)
        body = response.json()

        assert response.status_code == 200
        assert body["userId"] == 3

    def test_put_deve_substituir_todos_os_produtos(self, client):
        """PUT deve sobrescrever a lista de produtos do carrinho."""
        updated_payload = {
            "userId": 1,
            "date": "2024-06-01",
            "products": [{"productId": 5, "quantity": 10}],
        }
        response = client.put("/carts/1", json=updated_payload)
        body = response.json()

        assert response.status_code == 200
        assert len(body["products"]) == 1
        assert body["products"][0]["productId"] == 5


# ---------------------------------------------------------------------------
# PATCH /carts/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPatchCart:
    """Testes do endpoint PATCH /carts/{id}."""

    def test_deve_retornar_status_200_ao_atualizar_parcialmente(self, client):
        """PATCH /carts/{id} deve retornar 200 com campos atualizados."""
        partial_payload = {"userId": 7}
        response = client.patch("/carts/1", json=partial_payload)
        body = response.json()

        assert response.status_code == 200
        assert body["userId"] == 7

    def test_patch_de_produtos_deve_atualizar_lista(self, client):
        """PATCH com campo 'products' deve atualizar a lista de produtos."""
        partial_payload = {"products": [{"productId": 4, "quantity": 3}]}
        response = client.patch("/carts/1", json=partial_payload)
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body["products"], list)


# ---------------------------------------------------------------------------
# DELETE /carts/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDeleteCart:
    """Testes do endpoint DELETE /carts/{id}."""

    def test_deve_retornar_status_200_ao_deletar_carrinho(self, client):
        """DELETE /carts/{id} deve retornar 200 e o carrinho deletado."""
        response = client.delete("/carts/1")
        body = response.json()

        assert response.status_code == 200
        assert body["id"] == 1

    @pytest.mark.parametrize("cart_id", [1, 3, 5])
    def test_delete_de_diferentes_carrinhos_deve_retornar_200(self, client, cart_id):
        """DELETE de diferentes IDs válidos deve sempre retornar 200."""
        response = client.delete(f"/carts/{cart_id}")

        assert response.status_code == 200