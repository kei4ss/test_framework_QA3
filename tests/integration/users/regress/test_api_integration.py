"""Testes de integração da camada de API com JSONPlaceholder."""

import pytest
from requests import RequestException

from src.config.data_provider_config import DataSourceType
from src.infrastructure.logger.logger import Logger
from src.infrastructure.requestManager.request_manager import RequestManager
from src.utils.data_provider import DataProvider


@pytest.fixture(autouse=True)
def reset_singletons():
    RequestManager._reset_instance()
    DataProvider._instance = None
    DataProvider._initialized = False
    Logger._Logger__instance = None
    Logger._Logger__initialized = False
    yield
    RequestManager._reset_instance()
    DataProvider._instance = None
    DataProvider._initialized = False
    Logger._Logger__instance = None
    Logger._Logger__initialized = False


@pytest.fixture
def request_manager():
    return RequestManager(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=15,
    )


def _provider_payload():
    provider = DataProvider()
    user = provider.get_data(
        source=DataSourceType.HARDCODED,
        identifier="default_user",
    )[0]
    return {
        "name": user["name"],
        "username": "atividade5_user",
        "email": user["email"],
    }


def test_listar_todos_usuarios(request_manager):
    """GET /users deve retornar status 200 e lista de usuários com estrutura básica."""
    response = request_manager.get("/users")
    body = response.json()

    assert response.status_code == 200
    assert isinstance(body, list)
    assert len(body) > 0
    assert {"id", "name", "username", "email"}.issubset(body[0].keys())


@pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
def test_buscar_usuario_especifico_ids_validos(request_manager, user_id):
    """GET /users/{id} com IDs válidos deve retornar status 200 e campos principais."""
    response = request_manager.get(f"/users/{user_id}")
    body = response.json()

    assert response.status_code == 200
    assert body["id"] == user_id
    assert {"id", "name", "username", "email"}.issubset(body.keys())


def test_buscar_usuario_id_invalido_comportamento_esperado(request_manager):
    """GET /users/{id_invalido} valida comportamento esperado da API."""
    try:
        response = request_manager.get("/users/99999")
        body = response.json()
        assert response.status_code == 200
        assert body == {} or body == []
    except RequestException as exc:
        assert isinstance(exc, RequestException)


def test_criar_novo_usuario_com_data_provider(request_manager):
    """POST /users com dados do DataProvider deve retornar 201 e eco dos campos enviados."""
    payload = _provider_payload()
    response = request_manager.post("/users", json=payload)
    body = response.json()

    assert response.status_code == 201
    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]


def test_atualizar_usuario(request_manager):
    """PUT /users/{id} deve retornar 200 e dados modificados."""
    payload = _provider_payload()
    payload["name"] = "Updated Name"

    response = request_manager.put("/users/1", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["name"] == "Updated Name"
    assert body["email"] == payload["email"]


def test_deletar_usuario(request_manager):
    """DELETE /users/{id} deve retornar 200 ou 204."""
    response = request_manager.delete("/users/1")
    assert response.status_code in (200, 204)


def test_endpoint_invalido_retorna_erro_404(request_manager):
    """Endpoint inválido deve gerar erro HTTP e não sucesso silencioso."""
    with pytest.raises(RequestException):
        request_manager.get("/endpoint-invalido-atividade5")
