"""Service de autenticação para a FakeStore API.

Encapsula as chamadas ao endpoint POST /auth/login,
tornando o fluxo de login reutilizável em qualquer teste.

Endpoints cobertos:
  POST /auth/login  — autenticar usuário e obter token JWT
"""

from typing import Any, Dict

from src.services.base_service import BaseService


class AuthService(BaseService):
    """Service responsável pelas operações de autenticação.

    Exemplo de uso em testes::

        from src.services.auth_service import AuthService

        def test_login(client):
            auth = AuthService(client)
            token = auth.login("mor_2314", "83r5^_")
            assert token and len(token) > 0

        def test_login_retorna_response_completo(client):
            auth = AuthService(client)
            response = auth.login_raw("mor_2314", "83r5^_")
            assert response.status_code == 200
            assert "token" in response.json()
    """

    _ENDPOINT = "/auth/login"

    def login(self, username: str, password: str) -> str:
        """Autentica um usuário e retorna o token JWT.

        Realiza POST /auth/login com as credenciais fornecidas
        e extrai diretamente o token do corpo da resposta.

        Args:
            username: Nome de usuário cadastrado na FakeStore.
            password: Senha do usuário.

        Returns:
            String com o token JWT retornado pela API.

        Raises:
            KeyError: Se o corpo da resposta não contiver o campo 'token'.
            requests.RequestException: Se a requisição falhar (ex.: 401).
        """
        response = self.login_raw(username, password)
        return response.json()["token"]

    def login_raw(self, username: str, password: str) -> Any:
        """Autentica um usuário e retorna o objeto Response completo.

        Útil quando se precisa inspecionar o status code, headers ou
        corpo completo da resposta de autenticação.

        Args:
            username: Nome de usuário cadastrado na FakeStore.
            password: Senha do usuário.

        Returns:
            Objeto requests.Response da chamada a POST /auth/login.

        Raises:
            requests.RequestException: Se a requisição falhar.
        """
        payload = {"username": username, "password": password}
        return self._client.post(self._ENDPOINT, json=payload)

    def login_with_credentials(self, credentials: Dict[str, str]) -> str:
        """Autentica usando um dicionário de credenciais e retorna o token.

        Atalho conveniente quando as credenciais já estão em um dict
        (ex.: carregadas de um DataProvider ou fixture).

        Args:
            credentials: Dicionário com chaves 'username' e 'password'.

        Returns:
            String com o token JWT.

        Raises:
            KeyError: Se 'username' ou 'password' não estiverem no dict,
                      ou se 'token' não estiver na resposta.
            requests.RequestException: Se a requisição falhar.
        """
        return self.login(credentials["username"], credentials["password"])
