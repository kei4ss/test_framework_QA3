from unittest.mock import MagicMock, patch

import pytest
<<<<<<< HEAD
from requests.exceptions import RequestException, Timeout

from infraestructure.request_manager import RequestManager

from config.config import API_BASE_URL
from config.config import API_BASE_USERS_URL

@pytest.fixture
def request_manager():
    """
    Fixture para fornecer instância limpa do RequestManager.
    """

    # Reseta singleton para evitar interferência entre testes
    RequestManager._instance = None

    return RequestManager(
        base_url=API_BASE_URL,
        timeout=5,
    )


def test_singleton_instance():


    RequestManager._instance = None

    manager1 = RequestManager()
    manager2 = RequestManager()

    assert manager1 is manager2


def test_build_url(request_manager):
    """
    Deve montar corretamente a URL completa.
    """

    endpoint = "/users"

    result = request_manager._build_url(endpoint)

    assert result == API_BASE_USERS_URL


@patch("requests.Session.request")
def test_get_request_success(mock_request, request_manager):
    """
    Deve executar requisição GET com sucesso.
    """

    mock_response = MagicMock()

    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {
        "message": "success"
    }

    mock_request.return_value = mock_response

    response = request_manager.get("/users")

    assert response["status_code"] == 200
    assert response["success"] is True
    assert response["data"]["message"] == "success"

    mock_request.assert_called_once_with(
        method="GET",
        url=API_BASE_USERS_URL,
        headers={"Content-Type": "application/json"},
        params=None,
        data=None,
        json=None,
        timeout=5,
    )


@patch("requests.Session.request")
def test_post_request_success(mock_request, request_manager):
    """
    Deve executar requisição POST com sucesso.
    """

    payload = {
        "name": "Murilo"
    }

    mock_response = MagicMock()

    mock_response.status_code = 201
    mock_response.ok = True
    mock_response.json.return_value = payload

    mock_request.return_value = mock_response

    response = request_manager.post(
        "/users",
        json=payload,
    )

    assert response["status_code"] == 201
    assert response["success"] is True
    assert response["data"]["name"] == "Murilo"


@patch("requests.Session.request")
def test_put_request_success(mock_request, request_manager):
    """
    Deve executar requisição PUT com sucesso.
    """

    payload = {
        "name": "Updated User"
    }

    mock_response = MagicMock()

    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = payload

    mock_request.return_value = mock_response

    response = request_manager.put(
        "/users/1",
        json=payload,
    )

    assert response["status_code"] == 200
    assert response["data"]["name"] == "Updated User"


@patch("requests.Session.request")
def test_patch_request_success(mock_request, request_manager):
    """
    Deve executar requisição PATCH com sucesso.
    """

    payload = {
        "status": "active"
    }

    mock_response = MagicMock()

    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = payload

    mock_request.return_value = mock_response

    response = request_manager.patch(
        "/users/1",
        json=payload,
    )

    assert response["status_code"] == 200
    assert response["data"]["status"] == "active"


@patch("requests.Session.request")
def test_delete_request_success(mock_request, request_manager):
    """
    Deve executar requisição DELETE com sucesso.
    """

    mock_response = MagicMock()

    mock_response.status_code = 204
    mock_response.ok = True
    mock_response.json.return_value = {}

    mock_request.return_value = mock_response

    response = request_manager.delete("/users/1")

    assert response["status_code"] == 204
    assert response["success"] is True


@patch("requests.Session.request")
def test_timeout_exception(mock_request, request_manager):
    """
    Deve tratar exceção de timeout.
    """

    mock_request.side_effect = Timeout(
        "Connection timeout"
    )

    with pytest.raises(Exception) as error:
        request_manager.get("/users")

    assert "Tempo limite excedido" in str(error.value)


@patch("requests.Session.request")
def test_request_exception(mock_request, request_manager):
    """
    Deve tratar exceções de requisição HTTP.
    """

    mock_request.side_effect = RequestException(
        "HTTP Error"
    )

    with pytest.raises(Exception) as error:
        request_manager.get("/users")

    assert "Erro na requisição HTTP" in str(error.value)


@patch("requests.Session.request")
def test_response_with_text_content(mock_request, request_manager):
    """
    Deve tratar resposta textual quando não houver JSON.
    """

    mock_response = MagicMock()

    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.side_effect = ValueError()
    mock_response.text = "Plain text response"

    mock_request.return_value = mock_response

    response = request_manager.get("/status")

    assert response["data"] == "Plain text response"


@patch("requests.Session.request")
def test_custom_headers(mock_request, request_manager):
    """
    Deve adicionar headers personalizados.
    """

    mock_response = MagicMock()

    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {
        "success": True
    }

    mock_request.return_value = mock_response

    custom_headers = {
        "Authorization": "Bearer token"
    }

    request_manager.get(
        "/users",
        headers=custom_headers,
    )

    mock_request.assert_called_once_with(
        method="GET",
        url=API_BASE_USERS_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
        },
        params=None,
        data=None,
        json=None,
        timeout=5,
    )
=======
import requests

from src.infrastructure.request_manager import RequestManager


@pytest.fixture(autouse=True)
def reset_request_manager_singleton():
    RequestManager._reset_instance()
    yield
    RequestManager._reset_instance()


def _build_response(status_code=200, json_value=None, json_error=None):
    response = MagicMock()
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = json_value if json_value is not None else {"ok": True}
    return response


def test_singleton_returns_same_instance():
    a = RequestManager(base_url="https://example.com")
    b = RequestManager(base_url="https://another.com")
    assert a is b
    assert b.base_url == "https://example.com"


def test_get_calls_requests_with_expected_args():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", timeout=11, logger=logger)
    response = _build_response()

    with patch.object(manager._session, "request", return_value=response) as request_mock:
        result = manager.get("/users", params={"page": 1})

    assert result is response
    request_mock.assert_called_once_with(
        method="GET",
        url="https://example.com/users",
        params={"page": 1},
        data=None,
        json=None,
        headers={},
        timeout=11,
    )
    logger.log_request.assert_called_once()


@pytest.mark.parametrize("method_name,verb", [
    ("post", "POST"),
    ("put", "PUT"),
    ("patch", "PATCH"),
    ("delete", "DELETE"),
])
def test_http_methods_call_requests_correctly(method_name, verb):
    manager = RequestManager(base_url="https://example.com", timeout=22, logger=MagicMock())
    response = _build_response()

    with patch.object(manager._session, "request", return_value=response) as request_mock:
        method = getattr(manager, method_name)
        method("/resource", json={"x": 1}, headers={"X-Test": "1"})

    request_mock.assert_called_once_with(
        method=verb,
        url="https://example.com/resource",
        params=None,
        data=None,
        json={"x": 1},
        headers={"X-Test": "1"},
        timeout=22,
    )


def test_timeout_exception_is_raised_and_logged():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", logger=logger)

    with patch.object(manager._session, "request", side_effect=requests.Timeout("timeout")):
        with pytest.raises(requests.Timeout):
            manager.get("/slow")

    logger.error.assert_called()


def test_request_exception_is_raised_and_logged():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", logger=logger)

    with patch.object(manager._session, "request", side_effect=requests.RequestException("network")):
        with pytest.raises(requests.RequestException):
            manager.get("/fail")

    logger.error.assert_called()


def test_invalid_json_response_raises_value_error_and_logs():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", logger=logger)
    response = _build_response(json_error=ValueError("invalid json"))

    with patch.object(manager._session, "request", return_value=response):
        with pytest.raises(ValueError, match="Invalid JSON response"):
            manager.get("/users", expect_json=True)

    logger.error.assert_called()


def test_expect_json_returns_parsed_json():
    manager = RequestManager(base_url="https://example.com", logger=MagicMock())
    response = _build_response(json_value={"id": 1})

    with patch.object(manager._session, "request", return_value=response):
        result = manager.get("/users/1", expect_json=True)

    assert result == {"id": 1}


def test_auth_header_is_applied():
    manager = RequestManager(base_url="https://example.com", logger=MagicMock())
    manager.set_auth_token("abc")
    response = _build_response()

    with patch.object(manager._session, "request", return_value=response) as request_mock:
        manager.get("/secure")

    assert request_mock.call_args.kwargs["headers"]["Authorization"] == "Bearer abc"
>>>>>>> 2d7ec96db21469bc0b4313b039d388cd555682f3
