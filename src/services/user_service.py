"""
Service de usuários para a FakeStore API.

Encapsula todas as chamadas aos endpoints de /users,
tornando as operações de usuário reutilizáveis em testes de integração e E2E.

Endpoints cobertos:
  GET    /users                  — listar todos os usuários
  GET    /users/{id}             — buscar usuário por ID
  GET    /users?limit={n}        — listar com limite
  GET    /users?sort={asc|desc}  — listar ordenado
  POST   /users                  — criar usuário
  PUT    /users/{id}             — atualizar usuário (completo)
  PATCH  /users/{id}             — atualizar usuário (parcial)
  DELETE /users/{id}             — deletar usuário
"""

from typing import Any, Dict, List, Optional

from src.services.base_service import BaseService


class UserService(BaseService):
    """Service responsável pelas operações CRUD de usuários.

    Exemplo de uso em testes::

        from src.services.user_service import UserService

        def test_listar_usuarios(client):
            service = UserService(client)
            users = service.get_all()
            assert len(users) == 10

        def test_criar_e_deletar_usuario(client):
            service = UserService(client)
            payload = {"email": "qa@test.com", "username": "qa_user", ...}
            user = service.create(payload)
            assert user["id"] is not None
    """

    _BASE_ENDPOINT = "/users"

    # ------------------------------------------------------------------
    # GET /users
    # ------------------------------------------------------------------

    def get_all(
        self,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista todos os usuários, com suporte a limit e sort.

        Args:
            limit: Quantidade máxima de usuários a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').

        Returns:
            Lista de dicionários representando os usuários.
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
        """Lista usuários e retorna o Response completo.

        Útil para validar status code, headers e outros metadados.

        Args:
            limit: Quantidade máxima de usuários a retornar.
            sort: Ordenação dos resultados ('asc' ou 'desc').

        Returns:
            Objeto requests.Response da chamada a GET /users.
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
    # GET /users/{id}
    # ------------------------------------------------------------------

    def get_by_id(self, user_id: int) -> Dict[str, Any]:
        """Busca um usuário pelo seu ID.

        Args:
            user_id: ID numérico do usuário.

        Returns:
            Dicionário com os dados do usuário.

        Raises:
            requests.HTTPError: Se a API retornar 404 ou outro erro HTTP.
        """
        response = self._client.get(f"{self._BASE_ENDPOINT}/{user_id}")
        return response.json()

    def get_by_id_raw(self, user_id: int) -> Any:
        """Busca um usuário pelo ID e retorna o Response completo.

        Args:
            user_id: ID numérico do usuário.

        Returns:
            Objeto requests.Response da chamada a GET /users/{id}.
        """
        return self._client.get(f"{self._BASE_ENDPOINT}/{user_id}")

    # ------------------------------------------------------------------
    # POST /users
    # ------------------------------------------------------------------

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo usuário.

        Args:
            payload: Dados do usuário a ser criado. Estrutura esperada::

                {
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

        Returns:
            Dicionário com os dados do usuário criado, incluindo o 'id'
            gerado pela API.
        """
        response = self._client.post(self._BASE_ENDPOINT, json=payload)
        return response.json()

    def create_raw(self, payload: Dict[str, Any]) -> Any:
        """Cria um usuário e retorna o Response completo.

        Args:
            payload: Dados do usuário a ser criado.

        Returns:
            Objeto requests.Response da chamada a POST /users.
        """
        return self._client.post(self._BASE_ENDPOINT, json=payload)

    # ------------------------------------------------------------------
    # PUT /users/{id}
    # ------------------------------------------------------------------

    def update(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza completamente um usuário existente (PUT).

        Args:
            user_id: ID do usuário a ser atualizado.
            payload: Dados completos do usuário para substituição.

        Returns:
            Dicionário com os dados do usuário atualizado.
        """
        response = self._client.put(
            f"{self._BASE_ENDPOINT}/{user_id}", json=payload
        )
        return response.json()

    def update_raw(self, user_id: int, payload: Dict[str, Any]) -> Any:
        """Atualiza um usuário completamente e retorna o Response completo.

        Args:
            user_id: ID do usuário a ser atualizado.
            payload: Dados completos para substituição.

        Returns:
            Objeto requests.Response da chamada a PUT /users/{id}.
        """
        return self._client.put(
            f"{self._BASE_ENDPOINT}/{user_id}", json=payload
        )

    # ------------------------------------------------------------------
    # PATCH /users/{id}
    # ------------------------------------------------------------------

    def partial_update(
        self, user_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza parcialmente um usuário existente (PATCH).

        Apenas os campos presentes no payload serão alterados.

        Args:
            user_id: ID do usuário a ser atualizado.
            payload: Campos a serem atualizados (ex.: {"phone": "..."}).

        Returns:
            Dicionário com os dados do usuário após a atualização parcial.
        """
        response = self._client.patch(
            f"{self._BASE_ENDPOINT}/{user_id}", json=payload
        )
        return response.json()

    def partial_update_raw(self, user_id: int, payload: Dict[str, Any]) -> Any:
        """Atualiza parcialmente um usuário e retorna o Response completo.

        Args:
            user_id: ID do usuário a ser atualizado.
            payload: Campos a serem atualizados.

        Returns:
            Objeto requests.Response da chamada a PATCH /users/{id}.
        """
        return self._client.patch(
            f"{self._BASE_ENDPOINT}/{user_id}", json=payload
        )

    # ------------------------------------------------------------------
    # DELETE /users/{id}
    # ------------------------------------------------------------------

    def delete(self, user_id: int) -> Dict[str, Any]:
        """Deleta um usuário pelo ID.

        Args:
            user_id: ID do usuário a ser deletado.

        Returns:
            Dicionário com os dados do usuário deletado.
        """
        response = self._client.delete(f"{self._BASE_ENDPOINT}/{user_id}")
        return response.json()

    def delete_raw(self, user_id: int) -> Any:
        """Deleta um usuário e retorna o Response completo.

        Args:
            user_id: ID do usuário a ser deletado.

        Returns:
            Objeto requests.Response da chamada a DELETE /users/{id}.
        """
        return self._client.delete(f"{self._BASE_ENDPOINT}/{user_id}")
