"""Service de carrinhos para a FakeStore API.

Encapsula todas as chamadas aos endpoints de /carts,
tornando as operações de carrinho reutilizáveis em testes de integração e E2E.

Endpoints cobertos:
  GET    /carts                              — listar todos os carrinhos
  GET    /carts/{id}                         — buscar carrinho por ID
  GET    /carts?limit={n}                    — listar com limite
  GET    /carts?sort={asc|desc}              — listar ordenado
  GET    /carts?startdate=...&enddate=...    — filtrar por intervalo de datas
  GET    /carts/user/{userId}               — carrinhos de um usuário específico
  POST   /carts                              — criar carrinho
  PUT    /carts/{id}                         — atualizar carrinho (completo)
  PATCH  /carts/{id}                         — atualizar carrinho (parcial)
  DELETE /carts/{id}                         — deletar carrinho
"""

from typing import Any, Dict, List, Optional

from src.services.base_service import BaseService


class CartService(BaseService):
    """Service responsável pelas operações CRUD de carrinhos.

    Exemplo de uso em testes::

        from src.services.cart_service import CartService

        def test_criar_carrinho(client):
            service = CartService(client)
            cart = service.create({
                "userId": 1,
                "date": "2024-01-01",
                "products": [{"productId": 1, "quantity": 2}],
            })
            assert cart["id"] is not None
            assert cart["userId"] == 1

        def test_carrinhos_do_usuario(client):
            service = CartService(client)
            carts = service.get_by_user(user_id=1)
            for cart in carts:
                assert cart["userId"] == 1
    """

    _BASE_ENDPOINT = "/carts"

    # ------------------------------------------------------------------
    # GET /carts
    # ------------------------------------------------------------------

    def get_all(
        self,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        startdate: Optional[str] = None,
        enddate: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista todos os carrinhos, com suporte a filtros.

        Args:
            limit: Quantidade máxima de carrinhos a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').
            startdate: Data de início do filtro no formato 'YYYY-MM-DD'.
            enddate: Data de fim do filtro no formato 'YYYY-MM-DD'.

        Returns:
            Lista de dicionários representando os carrinhos.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort
        if startdate is not None:
            params["startdate"] = startdate
        if enddate is not None:
            params["enddate"] = enddate

        response = self._client.get(
            self._BASE_ENDPOINT,
            params=params if params else None,
        )
        return response.json()

    def get_all_raw(
        self,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        startdate: Optional[str] = None,
        enddate: Optional[str] = None,
    ) -> Any:
        """Lista carrinhos e retorna o Response completo.

        Args:
            limit: Quantidade máxima de carrinhos a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').
            startdate: Data de início do filtro no formato 'YYYY-MM-DD'.
            enddate: Data de fim do filtro no formato 'YYYY-MM-DD'.

        Returns:
            Objeto requests.Response da chamada a GET /carts.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort
        if startdate is not None:
            params["startdate"] = startdate
        if enddate is not None:
            params["enddate"] = enddate

        return self._client.get(
            self._BASE_ENDPOINT,
            params=params if params else None,
        )

    # ------------------------------------------------------------------
    # GET /carts/{id}
    # ------------------------------------------------------------------

    def get_by_id(self, cart_id: int) -> Dict[str, Any]:
        """Busca um carrinho pelo seu ID.

        Args:
            cart_id: ID numérico do carrinho.

        Returns:
            Dicionário com os dados do carrinho.

        Raises:
            requests.HTTPError: Se a API retornar 404 ou outro erro HTTP.
        """
        response = self._client.get(f"{self._BASE_ENDPOINT}/{cart_id}")
        return response.json()

    def get_by_id_raw(self, cart_id: int) -> Any:
        """Busca um carrinho pelo ID e retorna o Response completo.

        Args:
            cart_id: ID numérico do carrinho.

        Returns:
            Objeto requests.Response da chamada a GET /carts/{id}.
        """
        return self._client.get(f"{self._BASE_ENDPOINT}/{cart_id}")

    # ------------------------------------------------------------------
    # GET /carts/user/{userId}
    # ------------------------------------------------------------------

    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna todos os carrinhos de um usuário específico.

        Args:
            user_id: ID do usuário cujos carrinhos serão buscados.

        Returns:
            Lista de dicionários com os carrinhos do usuário.
            Pode ser uma lista vazia se o usuário não tiver carrinhos.
        """
        response = self._client.get(f"{self._BASE_ENDPOINT}/user/{user_id}")
        return response.json()

    def get_by_user_raw(self, user_id: int) -> Any:
        """Retorna os carrinhos de um usuário e o Response completo.

        Args:
            user_id: ID do usuário cujos carrinhos serão buscados.

        Returns:
            Objeto requests.Response da chamada a GET /carts/user/{userId}.
        """
        return self._client.get(f"{self._BASE_ENDPOINT}/user/{user_id}")

    # ------------------------------------------------------------------
    # POST /carts
    # ------------------------------------------------------------------

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo carrinho.

        Args:
            payload: Dados do carrinho a ser criado. Estrutura esperada::

                {
                    "userId": 1,
                    "date": "2024-01-01",
                    "products": [
                        {"productId": 1, "quantity": 2},
                        {"productId": 3, "quantity": 1},
                    ],
                }

        Returns:
            Dicionário com os dados do carrinho criado, incluindo o 'id'
            gerado pela API.
        """
        response = self._client.post(self._BASE_ENDPOINT, json=payload)
        return response.json()

    def create_raw(self, payload: Dict[str, Any]) -> Any:
        """Cria um carrinho e retorna o Response completo.

        Args:
            payload: Dados do carrinho a ser criado.

        Returns:
            Objeto requests.Response da chamada a POST /carts.
        """
        return self._client.post(self._BASE_ENDPOINT, json=payload)

    # ------------------------------------------------------------------
    # PUT /carts/{id}
    # ------------------------------------------------------------------

    def update(self, cart_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza completamente um carrinho existente (PUT).

        Substitui todos os produtos do carrinho pelos do payload.

        Args:
            cart_id: ID do carrinho a ser atualizado.
            payload: Dados completos do carrinho para substituição.

        Returns:
            Dicionário com os dados do carrinho atualizado.
        """
        response = self._client.put(
            f"{self._BASE_ENDPOINT}/{cart_id}", json=payload
        )
        return response.json()

    def update_raw(self, cart_id: int, payload: Dict[str, Any]) -> Any:
        """Atualiza um carrinho completamente e retorna o Response completo.

        Args:
            cart_id: ID do carrinho a ser atualizado.
            payload: Dados completos para substituição.

        Returns:
            Objeto requests.Response da chamada a PUT /carts/{id}.
        """
        return self._client.put(
            f"{self._BASE_ENDPOINT}/{cart_id}", json=payload
        )

    # ------------------------------------------------------------------
    # PATCH /carts/{id}
    # ------------------------------------------------------------------

    def partial_update(
        self, cart_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza parcialmente um carrinho existente (PATCH).

        Apenas os campos presentes no payload serão alterados.

        Args:
            cart_id: ID do carrinho a ser atualizado.
            payload: Campos a serem atualizados (ex.: {"userId": 5}).

        Returns:
            Dicionário com os dados do carrinho após a atualização parcial.
        """
        response = self._client.patch(
            f"{self._BASE_ENDPOINT}/{cart_id}", json=payload
        )
        return response.json()

    def partial_update_raw(self, cart_id: int, payload: Dict[str, Any]) -> Any:
        """Atualiza parcialmente um carrinho e retorna o Response completo.

        Args:
            cart_id: ID do carrinho a ser atualizado.
            payload: Campos a serem atualizados.

        Returns:
            Objeto requests.Response da chamada a PATCH /carts/{id}.
        """
        return self._client.patch(
            f"{self._BASE_ENDPOINT}/{cart_id}", json=payload
        )

    # ------------------------------------------------------------------
    # DELETE /carts/{id}
    # ------------------------------------------------------------------

    def delete(self, cart_id: int) -> Dict[str, Any]:
        """Deleta um carrinho pelo ID.

        Args:
            cart_id: ID do carrinho a ser deletado.

        Returns:
            Dicionário com os dados do carrinho deletado.
        """
        response = self._client.delete(f"{self._BASE_ENDPOINT}/{cart_id}")
        return response.json()

    def delete_raw(self, cart_id: int) -> Any:
        """Deleta um carrinho e retorna o Response completo.

        Args:
            cart_id: ID do carrinho a ser deletado.

        Returns:
            Objeto requests.Response da chamada a DELETE /carts/{id}.
        """
        return self._client.delete(f"{self._BASE_ENDPOINT}/{cart_id}")
