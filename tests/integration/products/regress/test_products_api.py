"""Testes de integração para os endpoints de Products da FakeStore API.

Cobre todos os endpoints disponíveis:
  GET    /products                         - listar todos os produtos
  GET    /products/{id}                    - buscar produto por ID
  GET    /products?limit={n}               - listar com limite
  GET    /products?sort={asc|desc}         - listar ordenado
  GET    /products/categories              - listar categorias
  GET    /products/category/{category}     - listar por categoria
  POST   /products                         - criar produto
  PUT    /products/{id}                    - atualizar produto (completo)
  PATCH  /products/{id}                    - atualizar produto (parcial)
  DELETE /products/{id}                   - deletar produto
"""

import pytest

from src.infrastructure.requestManager.request_manager import RequestManager

BASE_URL = "https://fakestoreapi.com"

PRODUCT_KEYS = {"id", "title", "price", "description", "category", "image"}

VALID_CATEGORIES = [
    "electronics",
    "jewelery",
    "men's clothing",
    "women's clothing",
]

NEW_PRODUCT_PAYLOAD = {
    "title": "Produto de Teste QA",
    "price": 49.99,
    "description": "Produto criado para fins de teste automatizado",
    "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
    "category": "electronics",
}


@pytest.fixture
def client():
    """RequestManager configurado para a FakeStore API."""
    return RequestManager(base_url=BASE_URL, timeout=15)


# ---------------------------------------------------------------------------
# GET /products
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetAllProducts:
    """Testes do endpoint GET /products."""

    def test_deve_retornar_status_200_e_lista_de_produtos(self, client):
        """GET /products deve retornar 200 e uma lista não-vazia de produtos."""
        response = client.get("/products")
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body, list)
        assert len(body) > 0

    def test_cada_produto_deve_conter_campos_obrigatorios(self, client):
        """Cada produto na listagem deve conter os campos obrigatórios."""
        response = client.get("/products")
        body = response.json()

        for product in body:
            assert PRODUCT_KEYS.issubset(product.keys()), (
                f"Produto id={product.get('id')} não contém todos os campos obrigatórios."
            )

    def test_campos_de_produto_devem_ter_tipos_corretos(self, client):
        """Os tipos dos campos de produto devem estar corretos."""
        response = client.get("/products")
        body = response.json()
        produto = body[0]

        assert isinstance(produto["id"], int)
        assert isinstance(produto["title"], str)
        assert isinstance(produto["price"], (int, float))
        assert isinstance(produto["description"], str)
        assert isinstance(produto["category"], str)
        assert isinstance(produto["image"], str)

    def test_preco_dos_produtos_deve_ser_positivo(self, client):
        """O campo 'price' de todos os produtos deve ser um número positivo."""
        response = client.get("/products")
        body = response.json()

        for product in body:
            assert product["price"] > 0, (
                f"Produto id={product['id']} tem preço inválido: {product['price']}"
            )

    def test_deve_retornar_20_produtos_por_padrao(self, client):
        """A API deve retornar exatamente 20 produtos na listagem padrão."""
        response = client.get("/products")
        body = response.json()

        assert len(body) == 20


# ---------------------------------------------------------------------------
# GET /products?limit={n}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetProductsWithLimit:
    """Testes do endpoint GET /products?limit={n}."""

    @pytest.mark.parametrize("limit", [1, 5, 10])
    def test_deve_respeitar_parametro_limit(self, client, limit):
        """GET /products?limit={n} deve retornar exatamente n produtos."""
        response = client.get("/products", params={"limit": limit})
        body = response.json()

        assert response.status_code == 200
        assert len(body) == limit

    def test_limit_zero_deve_retornar_lista_vazia_ou_padrao(self, client):
        """GET /products?limit=0 não deve causar erro."""
        response = client.get("/products", params={"limit": 0})

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /products?sort={asc|desc}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetProductsSorted:
    """Testes do endpoint GET /products?sort={asc|desc}."""

    def test_sort_asc_deve_retornar_produtos_em_ordem_crescente_de_id(self, client):
        """GET /products?sort=asc deve retornar produtos com IDs em ordem crescente."""
        response = client.get("/products", params={"sort": "asc"})
        body = response.json()

        assert response.status_code == 200
        ids = [p["id"] for p in body]
        assert ids == sorted(ids)

    def test_sort_desc_deve_retornar_produtos_em_ordem_decrescente_de_id(self, client):
        """GET /products?sort=desc deve retornar produtos com IDs em ordem decrescente."""
        response = client.get("/products", params={"sort": "desc"})
        body = response.json()

        assert response.status_code == 200
        ids = [p["id"] for p in body]
        assert ids == sorted(ids, reverse=True)


# ---------------------------------------------------------------------------
# GET /products/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetSingleProduct:
    """Testes do endpoint GET /products/{id}."""

    @pytest.mark.parametrize("product_id", [1, 5, 10, 20])
    def test_deve_retornar_produto_com_id_valido(self, client, product_id):
        """GET /products/{id} com ID válido deve retornar 200 e os dados do produto."""
        response = client.get(f"/products/{product_id}")
        body = response.json()

        assert response.status_code == 200
        assert body["id"] == product_id
        assert PRODUCT_KEYS.issubset(body.keys())

    def test_deve_retornar_resposta_vazia_para_id_inexistente(self, client):
        """GET /products/{id} com ID inexistente deve retornar 200 com body null.

        Comportamento real da FakeStore: retorna 200 com body `null` em vez de 404.
        A API não valida se o ID existe — é uma limitação conhecida do serviço.
        """
        response = client.get("/products/99999")
        body = response.json()

        assert response.status_code == 200
        assert body is None

    def test_produto_retornado_deve_ter_imagem_url_valida(self, client):
        """O campo 'image' do produto deve ser uma URL válida (http/https)."""
        response = client.get("/products/1")
        body = response.json()

        assert body["image"].startswith("http")


# ---------------------------------------------------------------------------
# GET /products/categories
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetProductCategories:
    """Testes do endpoint GET /products/categories."""

    def test_deve_retornar_status_200_e_lista_de_categorias(self, client):
        """GET /products/categories deve retornar 200 e lista de categorias."""
        response = client.get("/products/categories")
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body, list)
        assert len(body) > 0

    def test_categorias_retornadas_devem_ser_strings(self, client):
        """Todas as categorias devem ser strings."""
        response = client.get("/products/categories")
        body = response.json()

        for category in body:
            assert isinstance(category, str)

    def test_categorias_esperadas_devem_estar_presentes(self, client):
        """As 4 categorias padrão da FakeStore devem estar na resposta."""
        response = client.get("/products/categories")
        body = response.json()

        for expected in VALID_CATEGORIES:
            assert expected in body, f"Categoria '{expected}' não encontrada."


# ---------------------------------------------------------------------------
# GET /products/category/{category}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetProductsByCategory:
    """Testes do endpoint GET /products/category/{category}."""

    @pytest.mark.parametrize("category", VALID_CATEGORIES)
    def test_deve_retornar_produtos_da_categoria_correta(self, client, category):
        """GET /products/category/{cat} deve retornar somente produtos daquela categoria."""
        response = client.get(f"/products/category/{category}")
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body, list)
        assert len(body) > 0

        for product in body:
            assert product["category"] == category

    def test_categoria_invalida_deve_retornar_lista_vazia_ou_erro(self, client):
        """GET /products/category/{invalida} não deve retornar dados de outra categoria."""
        response = client.get("/products/category/categoria-inexistente")

        assert response.status_code in (200, 404)
        if response.status_code == 200:
            body = response.json()
            assert body == []


# ---------------------------------------------------------------------------
# POST /products
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPostProduct:
    """Testes do endpoint POST /products."""

    def test_deve_retornar_status_201_ao_criar_produto(self, client):
        """POST /products com payload válido deve retornar 201 e o produto criado.

        A FakeStore retorna 201 (Created) para criação de recursos,
        seguindo o padrão REST correto — diferente do que a documentação indica.
        """
        response = client.post("/products", json=NEW_PRODUCT_PAYLOAD)
        body = response.json()

        assert response.status_code == 201
        assert body["title"] == NEW_PRODUCT_PAYLOAD["title"]
        assert body["price"] == NEW_PRODUCT_PAYLOAD["price"]
        assert body["category"] == NEW_PRODUCT_PAYLOAD["category"]

    def test_produto_criado_deve_ter_id_atribuido(self, client):
        """O produto criado deve receber um ID gerado pela API."""
        response = client.post("/products", json=NEW_PRODUCT_PAYLOAD)
        body = response.json()

        assert "id" in body
        assert isinstance(body["id"], int)

    def test_deve_persistir_todos_os_campos_enviados(self, client):
        """Todos os campos enviados no payload devem estar presentes na resposta."""
        response = client.post("/products", json=NEW_PRODUCT_PAYLOAD)
        body = response.json()

        for field, value in NEW_PRODUCT_PAYLOAD.items():
            assert body[field] == value, (
                f"Campo '{field}' não confere: esperado={value}, recebido={body.get(field)}"
            )


# ---------------------------------------------------------------------------
# PUT /products/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPutProduct:
    """Testes do endpoint PUT /products/{id}."""

    def test_deve_retornar_status_200_ao_atualizar_produto(self, client):
        """PUT /products/{id} deve retornar 200 e os dados atualizados."""
        updated_payload = {**NEW_PRODUCT_PAYLOAD, "title": "Produto Atualizado PUT"}
        response = client.put("/products/1", json=updated_payload)
        body = response.json()

        assert response.status_code == 200
        assert body["title"] == "Produto Atualizado PUT"

    def test_todos_campos_devem_ser_atualizados_no_put(self, client):
        """PUT deve atualizar todos os campos enviados no payload."""
        updated_payload = {**NEW_PRODUCT_PAYLOAD, "price": 199.99, "description": "Desc atualizada"}
        response = client.put("/products/1", json=updated_payload)
        body = response.json()

        assert body["price"] == 199.99
        assert body["description"] == "Desc atualizada"


# ---------------------------------------------------------------------------
# PATCH /products/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPatchProduct:
    """Testes do endpoint PATCH /products/{id}."""

    def test_deve_retornar_status_200_ao_atualizar_parcialmente(self, client):
        """PATCH /products/{id} deve retornar 200 e atualizar apenas os campos enviados."""
        partial_payload = {"title": "Título Parcialmente Atualizado"}
        response = client.patch("/products/1", json=partial_payload)
        body = response.json()

        assert response.status_code == 200
        assert body["title"] == "Título Parcialmente Atualizado"

    def test_patch_de_preco_deve_atualizar_somente_preco(self, client):
        """PATCH com apenas 'price' deve atualizar somente esse campo."""
        partial_payload = {"price": 299.99}
        response = client.patch("/products/1", json=partial_payload)
        body = response.json()

        assert response.status_code == 200
        assert body["price"] == 299.99


# ---------------------------------------------------------------------------
# DELETE /products/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDeleteProduct:
    """Testes do endpoint DELETE /products/{id}."""

    def test_deve_retornar_status_200_ao_deletar_produto(self, client):
        """DELETE /products/{id} deve retornar 200 e o produto deletado."""
        response = client.delete("/products/1")
        body = response.json()

        assert response.status_code == 200
        assert body["id"] == 1

    @pytest.mark.parametrize("product_id", [1, 5, 10])
    def test_delete_de_diferentes_produtos_deve_retornar_200(self, client, product_id):
        """DELETE de diferentes IDs válidos deve sempre retornar 200."""
        response = client.delete(f"/products/{product_id}")

        assert response.status_code == 200