"""
Testes unitários para RequestManager.

Cobre:
- Singleton
- Construção de URL
- Métodos HTTP
- Headers customizados
- Bearer Token
- Parsing JSON
- Logging
- Timeout
- RequestException
- URLs absolutas
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.infrastructure.requestManager.request_manager import RequestManager
from src.config.settings import Settings


api_config = Settings().api_config()
API_BASE_URL = api_config["base_url"]
API_BASE_USERS_URL = f"{API_BASE_URL}/users"


@pytest.fixture
def request_manager():
    """
    Retorna uma instância limpa do RequestManager.
    """

    RequestManager._instance = None

    return RequestManager(
        base_url=API_BASE_URL,
        timeout=5,
        headers={
            "Content-Type": "application/json"
        },
        logger=MagicMock(),
    )


def build_response(
    status_code=200,
    json_value=None,
    json_error=None,
):
    """
    Cria um mock de Response.
    """

    response = MagicMock()

    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.raise_for_status = MagicMock()

    if json_error:
        response.json.side_effect = json_error
    else:
        response.json.return_value = (
            json_value
            if json_value is not None
            else {"success": True}
        )

    return response


# =====================================================
# Singleton
# =====================================================

class TestRequestManagerSingleton:

    def test_should_return_same_instance(self):

        RequestManager._instance = None

        manager1 = RequestManager(
            base_url="https://example.com"
        )

        manager2 = RequestManager(
            base_url="https://another.com"
        )

        assert manager1 is manager2
        assert manager2.base_url == "https://example.com"


# =====================================================
# URL
# =====================================================

class TestRequestManagerUrl:

    def test_should_build_url_correctly(
        self,
        request_manager,
    ):
        result = request_manager._build_url(
            "/users"
        )

        assert result == API_BASE_USERS_URL

    def test_should_keep_absolute_url(
        self,
        request_manager,
    ):
        url = "https://google.com"

        result = request_manager._build_url(url)

        assert result == url


# =====================================================
# GET
# =====================================================

class TestRequestManagerGet:

    @patch("requests.Session.request")
    def test_should_execute_get_request(
        self,
        mock_request,
        request_manager,
    ):
        response = build_response(
            json_value={
                "message": "success"
            }
        )

        mock_request.return_value = response

        result = request_manager.get("/users")

        assert result.status_code == 200
        assert result.json()["message"] == "success"

        mock_request.assert_called_once_with(
            method="GET",
            url=API_BASE_USERS_URL,
            params=None,
            data=None,
            json=None,
            headers={
                "Content-Type": "application/json"
            },
            timeout=5,
        )


# =====================================================
# HTTP METHODS
# =====================================================

class TestRequestManagerHttpMethods:

    @pytest.mark.parametrize(
        "method_name,http_method",
        [
            ("post", "POST"),
            ("put", "PUT"),
            ("patch", "PATCH"),
            ("delete", "DELETE"),
        ],
    )
    @patch("requests.Session.request")
    def test_should_use_correct_http_method(
        self,
        mock_request,
        request_manager,
        method_name,
        http_method,
    ):
        response = build_response()

        mock_request.return_value = response

        method = getattr(
            request_manager,
            method_name,
        )

        if method_name == "delete":
            method("/users/1")
        else:
            method(
                "/users/1",
                json={"name": "John"},
            )

        assert mock_request.call_args.kwargs[
            "method"
        ] == http_method


# =====================================================
# Headers
# =====================================================

class TestRequestManagerHeaders:

    @patch("requests.Session.request")
    def test_should_merge_custom_headers(
        self,
        mock_request,
        request_manager,
    ):
        response = build_response()

        mock_request.return_value = response

        request_manager.get(
            "/users",
            headers={
                "Authorization":
                    "Bearer token"
            },
        )

        headers = mock_request.call_args.kwargs[
            "headers"
        ]

        assert headers == {
            "Content-Type":
                "application/json",
            "Authorization":
                "Bearer token",
        }

    @patch("requests.Session.request")
    def test_should_add_default_header(
        self,
        mock_request,
        request_manager,
    ):
        response = build_response()

        mock_request.return_value = response

        request_manager.set_default_header(
            "X-Tenant",
            "123",
        )

        request_manager.get("/users")

        headers = mock_request.call_args.kwargs[
            "headers"
        ]

        assert headers["X-Tenant"] == "123"


# =====================================================
# Authentication
# =====================================================

class TestRequestManagerAuthentication:

    @patch("requests.Session.request")
    def test_should_add_bearer_token(
        self,
        mock_request,
        request_manager,
    ):
        response = build_response()

        mock_request.return_value = response

        request_manager.set_auth_token(
            "abc123"
        )

        request_manager.get("/secure")

        headers = mock_request.call_args.kwargs[
            "headers"
        ]

        assert (
            headers["Authorization"]
            == "Bearer abc123"
        )


# =====================================================
# JSON
# =====================================================

class TestRequestManagerJson:

    @patch("requests.Session.request")
    def test_should_return_parsed_json(
        self,
        mock_request,
        request_manager,
    ):
        response = build_response(
            json_value={
                "id": 1,
                "name": "John",
            }
        )

        mock_request.return_value = response

        result = request_manager.get(
            "/users/1",
            expect_json=True,
        )

        assert result == {
            "id": 1,
            "name": "John",
        }

    @patch("requests.Session.request")
    def test_should_raise_when_json_is_invalid(
        self,
        mock_request,
        request_manager,
    ):
        response = build_response(
            json_error=ValueError(
                "invalid json"
            )
        )

        mock_request.return_value = response

        with pytest.raises(
            ValueError,
            match="Invalid JSON response",
        ):
            request_manager.get(
                "/users",
                expect_json=True,
            )

    @patch("requests.Session.request")
    def test_should_handle_text_response(
        self,
        mock_request,
        request_manager,
    ):
        response = MagicMock()

        response.status_code = 200
        response.ok = True
        response.text = "Plain text response"

        response.json.side_effect = ValueError()

        mock_request.return_value = response

        result = request_manager.get(
            "/status"
        )

        assert result.text == (
            "Plain text response"
        )


# =====================================================
# Error Handling
# =====================================================

class TestRequestManagerErrors:

    @patch("requests.Session.request")
    def test_should_raise_timeout(
        self,
        mock_request,
        request_manager,
    ):
        mock_request.side_effect = (
            requests.Timeout(
                "Connection timeout"
            )
        )

        with pytest.raises(
            requests.Timeout
        ):
            request_manager.get(
                "/users"
            )

        request_manager._logger.error.assert_called()

    @patch("requests.Session.request")
    def test_should_raise_request_exception(
        self,
        mock_request,
        request_manager,
    ):
        mock_request.side_effect = (
            requests.RequestException(
                "HTTP Error"
            )
        )

        with pytest.raises(
            requests.RequestException
        ):
            request_manager.get(
                "/users"
            )

        request_manager._logger.error.assert_called()


# =====================================================
# Logging
# =====================================================

class TestRequestManagerLogging:

    @patch("requests.Session.request")
    def test_should_log_request(
        self,
        mock_request,
        request_manager,
    ):
        response = build_response()

        mock_request.return_value = response

        request_manager.get(
            "/users"
        )

        request_manager._logger.log_request\
            .assert_called_once()

