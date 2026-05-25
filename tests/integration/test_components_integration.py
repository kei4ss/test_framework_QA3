"""Testes de integração entre componentes centrais do framework."""

from pathlib import Path

import pytest

from src.config.data_provider_config import DataSourceType
from src.infraestructure.logger import Logger
from src.infrastructure.request_manager import RequestManager
from src.utils.data_provider import DataProvider


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reseta singletons para garantir isolamento entre cenários."""
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


def _build_payload_from_provider():
    provider = DataProvider()
    user = provider.get_data(
        source=DataSourceType.HARDCODED,
        identifier="default_user",
    )[0]
    return {
        "name": user["name"],
        "username": f"{user['name'].replace(' ', '').lower()}_qa",
        "email": user["email"],
    }


def test_integracao_request_manager_logger_gera_log(tmp_path):
    """Valida que uma chamada HTTP via RequestManager é registrada no Logger."""
    logger = Logger(log_level="INFO", log_dir=str(tmp_path))
    rm = RequestManager(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=15,
        logger=logger,
    )

    response = rm.get("/users/1")

    assert response.status_code == 200
    log_content = Path(tmp_path / "sentinela.log").read_text(encoding="utf-8")
    assert "HTTP GET https://jsonplaceholder.typicode.com/users/1" in log_content
    assert "200" in log_content


def test_integracao_request_manager_data_provider_post():
    """Valida uso de dados do DataProvider em POST via RequestManager."""
    rm = RequestManager(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=15,
    )
    payload = _build_payload_from_provider()

    response = rm.post("/users", json=payload)
    body = response.json()

    assert response.status_code == 201
    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]


def test_fluxo_completo_data_request_response_logger_assertions(tmp_path):
    """Valida o fluxo completo: Data -> Request -> Response -> Logger -> Assertions."""
    logger = Logger(log_level="INFO", log_dir=str(tmp_path))
    rm = RequestManager(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=15,
        logger=logger,
    )
    payload = _build_payload_from_provider()

    response = rm.post("/users", json=payload)
    body = response.json()

    assert response.status_code == 201
    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]

    log_content = Path(tmp_path / "sentinela.log").read_text(encoding="utf-8")
    assert "HTTP POST https://jsonplaceholder.typicode.com/users" in log_content
    assert "201" in log_content
