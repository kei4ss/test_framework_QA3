"""Service de produtos para a FakeStore API.

Encapsula todas as chamadas aos endpoints de /products,
tornando as operações de produto reutilizáveis em testes de integração e E2E.

Endpoints cobertos:
  GET    /products                          — listar todos os produtos
  GET    /products/{id}                     — buscar produto por ID
  GET    /products?limit={n}                — listar com limite
  GET    /products?sort={asc|desc}          — listar ordenado
  GET    /products/categories               — listar categorias disponíveis
  GET    /products/category/{category}      — listar por categoria
  POST   /products                          — criar produto
  PUT    /products/{id}                     — atualizar produto (completo)
  PATCH  /products/{id}                     — atualizar produto (parcial)
  DELETE /products/{id}                     — deletar produto
"""

from typing import Any, Dict, List, Optional
from src.services.base_service import BaseService


class ProductService(BaseService):
    """Service responsável pelas operações CRUD de produtos.

    Exemplo de uso em testes::

        from src.services.product_service import ProductService

        def test_listar_produtos(client):
            service = ProductService(client)
            products = service.get_all(limit=5)
            assert len(products) == 5

        def test_ciclo_produto(client):
            service = ProductService(client)
            produto = service.create({
                "title": "Produto QA",
                "price": 10.0,
                "description": "Teste",
                "image": "http://...",
                "category": "electronics",
            })
            assert produto["id"] is not None
            service.delete(produto["id"])
    """

    _BASE_ENDPOINT = "/products"

    # ------------------------------------------------------------------
    # GET /products
    # ------------------------------------------------------------------

    def get_all(
        self,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista todos os produtos, com suporte a limit e sort.

        Args:
            limit: Quantidade máxima de produtos a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').

        Returns:
            Lista de dicionários representando os produtos.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        response = self._client.get(
            self._BASE_ENDPOINT,
            params=params if params else None,
        )
        return response.json()

    def get_all_raw(
        self,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> Any:
        """Lista produtos e retorna o Response completo.

        Args:
            limit: Quantidade máxima de produtos a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').

        Returns:
            Objeto requests.Response da chamada a GET /products.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        return self._client.get(
            self._BASE_ENDPOINT,
            params=params if params else None,
        )

    # ------------------------------------------------------------------
    # GET /products/{id}
    # ------------------------------------------------------------------

    def get_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Busca um produto pelo seu ID.

        Nota: A FakeStore retorna 200 com body null para IDs inexistentes,
        em vez de 404. Este método reflete esse comportamento retornando None.

        Args:
            product_id: ID numérico do produto.

        Returns:
            Dicionário com dados do produto, ou None se não encontrado.
        """
        response = self._client.get(f"{self._BASE_ENDPOINT}/{product_id}")
        return response.json()

    def get_by_id_raw(self, product_id: int) -> Any:
        """Busca um produto pelo ID e retorna o Response completo.

        Args:
            product_id: ID numérico do produto.

        Returns:
            Objeto requests.Response da chamada a GET /products/{id}.
        """
        return self._client.get(f"{self._BASE_ENDPOINT}/{product_id}")

    # ------------------------------------------------------------------
    # GET /products/categories
    # ------------------------------------------------------------------

    def get_categories(self) -> List[str]:
        """Retorna a lista de categorias disponíveis na FakeStore.

        Returns:
            Lista de strings com os nomes das categorias
            (ex.: ['electronics', 'jewelery', "men's clothing", "women's clothing"]).
        """
        response = self._client.get(f"{self._BASE_ENDPOINT}/categories")
        return response.json()

    def get_categories_raw(self) -> Any:
        """Retorna as categorias e o Response completo.

        Returns:
            Objeto requests.Response da chamada a GET /products/categories.
        """
        return self._client.get(f"{self._BASE_ENDPOINT}/categories")

    # ------------------------------------------------------------------
    # GET /products/category/{category}
    # ------------------------------------------------------------------

    def get_by_category(
        self,
        category: str,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista os produtos de uma categoria específica.

        Args:
            category: Nome da categoria (ex.: 'electronics').
            limit: Quantidade máxima de produtos a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').

        Returns:
            Lista de produtos pertencentes à categoria.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        response = self._client.get(
            f"{self._BASE_ENDPOINT}/category/{category}",
            params=params if params else None,
        )
        return response.json()

    def get_by_category_raw(
        self,
        category: str,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> Any:
        """Lista produtos por categoria e retorna o Response completo.

        Args:
            category: Nome da categoria.
            limit: Quantidade máxima de produtos a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').

        Returns:
            Objeto requests.Response da chamada a GET /products/category/{category}.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        return self._client.get(
            f"{self._BASE_ENDPOINT}/category/{category}",
            params=params if params else None,
        )

    # ------------------------------------------------------------------
    # POST /products
    # ------------------------------------------------------------------

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo produto.

        Args:
            payload: Dados do produto a ser criado. Estrutura esperada::

                {
                    "title": "Nome do Produto",
                    "price": 49.99,
                    "description": "Descrição do produto",
                    "image": "https://example.com/img.jpg",
                    "category": "electronics",
                }

        Returns:
            Dicionário com os dados do produto criado, incluindo o 'id'
            gerado pela API.
        """
        response = self._client.post(self._BASE_ENDPOINT, json=payload)
        return response.json()

    def create_raw(self, payload: Dict[str, Any]) -> Any:
        """Cria um produto e retorna o Response completo.

        Útil para validar o status code 201 (Created) retornado pela FakeStore.

        Args:
            payload: Dados do produto a ser criado.

        Returns:
            Objeto requests.Response da chamada a POST /products.
        """
        return self._client.post(self._BASE_ENDPOINT, json=payload)

    # ------------------------------------------------------------------
    # PUT /products/{id}
    # ------------------------------------------------------------------

    def update(self, product_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza completamente um produto existente (PUT).

        Args:
            product_id: ID do produto a ser atualizado.
            payload: Dados completos do produto para substituição.

        Returns:
            Dicionário com os dados do produto atualizado.
        """
        response = self._client.put(
            f"{self._BASE_ENDPOINT}/{product_id}", json=payload
        )
        return response.json()

    def update_raw(self, product_id: int, payload: Dict[str, Any]) -> Any:
        """Atualiza um produto completamente e retorna o Response completo.

        Args:
            product_id: ID do produto a ser atualizado.
            payload: Dados completos para substituição.

        Returns:
            Objeto requests.Response da chamada a PUT /products/{id}.
        """
        return self._client.put(
            f"{self._BASE_ENDPOINT}/{product_id}", json=payload
        )

    # ------------------------------------------------------------------
    # PATCH /products/{id}
    # ------------------------------------------------------------------

    def partial_update(
        self, product_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza parcialmente um produto existente (PATCH).

        Apenas os campos presentes no payload serão alterados.

        Args:
            product_id: ID do produto a ser atualizado.
            payload: Campos a serem atualizados (ex.: {"price": 99.99}).

        Returns:
            Dicionário com os dados do produto após a atualização parcial.
        """
        response = self._client.patch(
            f"{self._BASE_ENDPOINT}/{product_id}", json=payload
        )
        return response.json()

    def partial_update_raw(self, product_id: int, payload: Dict[str, Any]) -> Any:
        """Atualiza parcialmente um produto e retorna o Response completo.

        Args:
            product_id: ID do produto a ser atualizado.
            payload: Campos a serem atualizados.

        Returns:
            Objeto requests.Response da chamada a PATCH /products/{id}.
        """
        return self._client.patch(
            f"{self._BASE_ENDPOINT}/{product_id}", json=payload
        )

    # ------------------------------------------------------------------
    # DELETE /products/{id}
    # ------------------------------------------------------------------

    def delete(self, product_id: int) -> Dict[str, Any]:
        """Deleta um produto pelo ID.

        Args:
            product_id: ID do produto a ser deletado.

        Returns:
            Dicionário com os dados do produto deletado.
        """
        response = self._client.delete(f"{self._BASE_ENDPOINT}/{product_id}")
        return response.json()

    def delete_raw(self, product_id: int) -> Any:
        """Deleta um produto e retorna o Response completo.

        Args:
            product_id: ID do produto a ser deletado.

        Returns:
            Objeto requests.Response da chamada a DELETE /products/{id}.
        """
        return self._client.delete(f"{self._BASE_ENDPOINT}/{product_id}")
