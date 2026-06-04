from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException, Timeout

from src.infrastructure.requestManager.request_manager import RequestManager
from src.config.settings import Settings

api_config = Settings().api_config()
API_BASE_URL       = api_config["base_url"]
API_BASE_USERS_URL = f"{API_BASE_URL}/{'users'}"


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
        headers={"Content-Type": "application/json"}
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

    assert response.status_code == 200
    assert response.ok is True
    assert response.json()["message"] == "success"

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

    assert response.status_code == 201
    assert response.ok is True
    assert response.json()["name"] == "Murilo"


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

    assert response.status_code == 200
    assert response.json()["name"] == "Updated User"


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

    assert response.status_code == 200
    assert response.json()["status"] == "active"


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

    assert response.status_code == 204
    assert response.ok is True


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

    assert "Connection timeout" in str(error.value)


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

    assert "HTTP Error" in str(error.value)


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

    assert response.text == "Plain text response"


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
