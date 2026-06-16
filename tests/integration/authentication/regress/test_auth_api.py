"""Testes de integração para o endpoint de Auth da FakeStore API.

Cobre todos os endpoints disponíveis:
  POST   /auth/login                       - autenticar usuário e obter token JWT

Notas:
  - A FakeStore usa credenciais de usuários existentes (IDs 1-10).
  - Credenciais válidas: username="mor_2314" / password="83r5^_" (usuário ID 2).
  - O token retornado é um JWT que pode ser usado em endpoints protegidos.
"""

import pytest

from src.infrastructure.requestManager.request_manager import RequestManager

BASE_URL = "https://fakestoreapi.com"

# Credenciais válidas da FakeStore (usuário ID 2)
VALID_CREDENTIALS = {
    "username": "mor_2314",
    "password": "83r5^_",
}

# Credenciais inválidas para testes negativos
INVALID_CREDENTIALS = {
    "username": "usuario_inexistente_qa",
    "password": "senha_errada_123",
}


@pytest.fixture
def client():
    """RequestManager configurado para a FakeStore API."""
    return RequestManager(base_url=BASE_URL, timeout=15)


# ---------------------------------------------------------------------------
# POST /auth/login — cenários positivos
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestAuthLogin:
    """Testes do endpoint POST /auth/login."""

    def test_deve_retornar_status_200_com_credenciais_validas(self, client):
        """POST /auth/login com credenciais válidas deve retornar 200."""
        response = client.post("/auth/login", json=VALID_CREDENTIALS)

        assert response.status_code == 200

    def test_deve_retornar_token_com_credenciais_validas(self, client):
        """POST /auth/login com credenciais válidas deve retornar um token."""
        response = client.post("/auth/login", json=VALID_CREDENTIALS)
        body = response.json()

        assert "token" in body
        assert isinstance(body["token"], str)
        assert len(body["token"]) > 0

    def test_token_retornado_deve_ser_jwt_formato_valido(self, client):
        """O token JWT deve ter exatamente 3 partes separadas por ponto."""
        response = client.post("/auth/login", json=VALID_CREDENTIALS)
        body = response.json()
        token = body["token"]

        partes = token.split(".")
        assert len(partes) == 3, (
            f"Token JWT inválido — esperado 3 partes, encontrado {len(partes)}: {token}"
        )

    def test_token_deve_comecar_com_header_jwt_base64(self, client):
        """O primeiro segmento do JWT (header) deve ser uma string base64 válida."""
        import base64

        response = client.post("/auth/login", json=VALID_CREDENTIALS)
        body = response.json()
        token = body["token"]

        header_b64 = token.split(".")[0]
        # Adiciona padding se necessário
        padded = header_b64 + "=" * (-len(header_b64) % 4)
        try:
            decoded = base64.urlsafe_b64decode(padded)
            assert len(decoded) > 0
        except Exception as exc:
            pytest.fail(f"Header do JWT não é base64 válido: {exc}")

    @pytest.mark.parametrize("username,password", [
        ("mor_2314", "83r5^_"),
        ("kevinryan", "kev02937@"),
        ("donero", "ewedon"),
    ])
    def test_multiplos_usuarios_validos_devem_autenticar(self, client, username, password):
        """Diferentes usuários válidos da FakeStore devem conseguir fazer login."""
        response = client.post("/auth/login", json={
            "username": username,
            "password": password,
        })
        body = response.json()

        assert response.status_code == 200
        assert "token" in body
        assert len(body["token"]) > 0


# ---------------------------------------------------------------------------
# POST /auth/login — cenários negativos
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestAuthLoginNegative:
    """Testes negativos do endpoint POST /auth/login."""

    def test_deve_retornar_erro_com_credenciais_invalidas(self, client):
        """POST /auth/login com credenciais inválidas deve retornar erro HTTP."""
        from requests import RequestException

        try:
            response = client.post("/auth/login", json=INVALID_CREDENTIALS)
            # A API pode retornar 401 ou 403 para credenciais inválidas
            assert response.status_code in (400, 401, 403)
        except RequestException:
            # Levantar exceção HTTP também é comportamento válido
            pass

    def test_nao_deve_retornar_token_com_senha_errada(self, client):
        """POST /auth/login com senha errada não deve retornar token válido."""
        from requests import RequestException

        wrong_pass_payload = {
            "username": VALID_CREDENTIALS["username"],
            "password": "senha_completamente_errada",
        }

        try:
            response = client.post("/auth/login", json=wrong_pass_payload)
            body = response.json()

            # Ou retorna erro HTTP, ou retorna body sem 'token'
            assert response.status_code not in (200,) or "token" not in body
        except RequestException:
            pass  # Exceção HTTP é comportamento esperado para credenciais inválidas

    def test_nao_deve_retornar_token_com_usuario_inexistente(self, client):
        """POST /auth/login com username inexistente não deve retornar token."""
        from requests import RequestException

        try:
            response = client.post("/auth/login", json=INVALID_CREDENTIALS)
            body = response.json()

            assert response.status_code not in (200,) or "token" not in body
        except RequestException:
            pass

    def test_deve_rejeitar_payload_sem_username(self, client):
        """POST /auth/login sem o campo 'username' deve retornar erro."""
        from requests import RequestException

        try:
            response = client.post("/auth/login", json={"password": "senha123"})
            assert response.status_code in (400, 401, 403, 422)
        except RequestException:
            pass

    def test_deve_rejeitar_payload_sem_password(self, client):
        """POST /auth/login sem o campo 'password' deve retornar erro."""
        from requests import RequestException

        try:
            response = client.post("/auth/login", json={"username": "mor_2314"})
            assert response.status_code in (400, 401, 403, 422)
        except RequestException:
            pass

    def test_deve_rejeitar_payload_vazio(self, client):
        """POST /auth/login com payload vazio deve retornar erro."""
        from requests import RequestException

        try:
            response = client.post("/auth/login", json={})
            assert response.status_code in (400, 401, 403, 422)
        except RequestException:
            pass


# ---------------------------------------------------------------------------
# Fluxo de autenticação completo
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestAuthFluxoCompleto:
    """Testes de fluxo envolvendo login e uso do token."""

    def test_token_obtido_pode_ser_usado_como_bearer(self, client):
        """O token obtido no login deve poder ser configurado como Bearer token."""
        # Arrange: faz login e obtém token
        login_response = client.post("/auth/login", json=VALID_CREDENTIALS)
        body = login_response.json()

        assert "token" in body
        token = body["token"]

        # Act: configura o token no manager (padrão Bearer)
        client.set_auth_token(token)
        auth_header = client.default_headers.get("Authorization", "")

        # Assert: o header deve estar no formato correto
        assert auth_header == f"Bearer {token}"

    def test_dois_logins_consecutivos_retornam_tokens_distintos_ou_iguais(self, client):
        """Dois logins consecutivos devem retornar tokens (podendo ser iguais ou distintos)."""
        response1 = client.post("/auth/login", json=VALID_CREDENTIALS)
        response2 = client.post("/auth/login", json=VALID_CREDENTIALS)

        token1 = response1.json()["token"]
        token2 = response2.json()["token"]

        # Ambos devem ser strings válidas, independente de serem iguais
        assert isinstance(token1, str) and len(token1) > 0
        assert isinstance(token2, str) and len(token2) > 0