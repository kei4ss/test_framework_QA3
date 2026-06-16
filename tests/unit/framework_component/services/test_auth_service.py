"""Testes unitários para AuthService.

Verifica o comportamento do service de autenticação usando
mocks do RequestManager, sem fazer chamadas reais à API.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.services.auth_service import AuthService


VALID_CREDENTIALS = {
    "username": "mor_2314",
    "password": "83r5^_",
}

MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature"


@pytest.fixture
def mock_client():
    """RequestManager mockado para testes unitários."""
    return MagicMock()


@pytest.fixture
def auth_service(mock_client):
    """AuthService configurado com client mockado."""
    return AuthService(client=mock_client)


@pytest.mark.unit
@pytest.mark.framework_component
class TestAuthServiceLogin:
    """Testes do método AuthService.login()."""

    def test_login_deve_chamar_post_no_endpoint_correto(self, auth_service, mock_client):
        """login() deve chamar POST /auth/login."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": MOCK_TOKEN}
        mock_client.post.return_value = mock_response

        auth_service.login("mor_2314", "83r5^_")

        mock_client.post.assert_called_once_with(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )

    def test_login_deve_retornar_token_como_string(self, auth_service, mock_client):
        """login() deve retornar apenas o token JWT como string."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": MOCK_TOKEN}
        mock_client.post.return_value = mock_response

        token = auth_service.login("mor_2314", "83r5^_")

        assert token == MOCK_TOKEN
        assert isinstance(token, str)

    def test_login_deve_passar_username_e_password_no_payload(self, auth_service, mock_client):
        """login() deve incluir username e password no corpo da requisição."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": MOCK_TOKEN}
        mock_client.post.return_value = mock_response

        auth_service.login("kevinryan", "kev02937@")

        _, kwargs = mock_client.post.call_args
        assert kwargs["json"]["username"] == "kevinryan"
        assert kwargs["json"]["password"] == "kev02937@"

    def test_login_deve_levantar_key_error_se_token_ausente(self, auth_service, mock_client):
        """login() deve levantar KeyError se a resposta não tiver 'token'."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid credentials"}
        mock_client.post.return_value = mock_response

        with pytest.raises(KeyError):
            auth_service.login("usuario_errado", "senha_errada")


@pytest.mark.unit
@pytest.mark.framework_component
class TestAuthServiceLoginRaw:
    """Testes do método AuthService.login_raw()."""

    def test_login_raw_deve_retornar_response_completo(self, auth_service, mock_client):
        """login_raw() deve retornar o objeto Response sem extrair o token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": MOCK_TOKEN}
        mock_client.post.return_value = mock_response

        response = auth_service.login_raw("mor_2314", "83r5^_")

        assert response is mock_response
        assert response.status_code == 200

    def test_login_raw_deve_chamar_post_com_payload_correto(self, auth_service, mock_client):
        """login_raw() deve enviar o payload com username e password."""
        mock_response = MagicMock()
        mock_client.post.return_value = mock_response

        auth_service.login_raw("mor_2314", "83r5^_")

        mock_client.post.assert_called_once_with(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )


@pytest.mark.unit
@pytest.mark.framework_component
class TestAuthServiceLoginWithCredentials:
    """Testes do método AuthService.login_with_credentials()."""

    def test_login_with_credentials_deve_aceitar_dict(self, auth_service, mock_client):
        """login_with_credentials() deve aceitar dicionário de credenciais."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": MOCK_TOKEN}
        mock_client.post.return_value = mock_response

        token = auth_service.login_with_credentials(VALID_CREDENTIALS)

        assert token == MOCK_TOKEN

    def test_login_with_credentials_deve_extrair_username_e_password(
        self, auth_service, mock_client
    ):
        """login_with_credentials() deve usar corretamente os campos do dict."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": MOCK_TOKEN}
        mock_client.post.return_value = mock_response

        auth_service.login_with_credentials(VALID_CREDENTIALS)

        _, kwargs = mock_client.post.call_args
        assert kwargs["json"]["username"] == VALID_CREDENTIALS["username"]
        assert kwargs["json"]["password"] == VALID_CREDENTIALS["password"]

    def test_login_with_credentials_deve_levantar_key_error_sem_username(
        self, auth_service, mock_client
    ):
        """login_with_credentials() deve levantar KeyError se 'username' estiver ausente."""
        with pytest.raises(KeyError):
            auth_service.login_with_credentials({"password": "senha"})


@pytest.mark.unit
@pytest.mark.framework_component
class TestAuthServiceInstanciacao:
    """Testes de instanciação do AuthService."""

    def test_deve_aceitar_client_externo(self):
        """AuthService deve aceitar um RequestManager externo."""
        mock_client = MagicMock()
        service = AuthService(client=mock_client)
        assert service._client is mock_client

    def test_deve_criar_client_interno_quando_nenhum_fornecido(self):
        """AuthService deve criar seu próprio RequestManager se nenhum for fornecido."""
        with patch("src.services.base_service.RequestManager") as mock_rm_cls:
            mock_rm_cls.return_value = MagicMock()
            service = AuthService()
            mock_rm_cls.assert_called_once()

    def test_set_auth_token_deve_delegar_ao_client(self):
        """set_auth_token() deve chamar o método correspondente no RequestManager."""
        mock_client = MagicMock()
        service = AuthService(client=mock_client)
        service.set_auth_token("meu-token")
        mock_client.set_auth_token.assert_called_once_with("meu-token")
