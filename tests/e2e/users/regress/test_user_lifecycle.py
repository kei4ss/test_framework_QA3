"""Teste E2E do fluxo de ciclo de vida de usuário com JSONPlaceholder."""

from pathlib import Path

import pytest

from src.config.data_provider_config import DataSourceType
from src.infraestructure.logger import Logger
from src.infrastructure.request_manager import RequestManager
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


def test_fluxo_e2e_ciclo_de_vida_usuario(tmp_path):
    """Fluxo completo E2E: obter dado -> criar -> atualizar -> deletar -> validar logs."""
    provider = DataProvider()
    seed_user = provider.get_data(
        source=DataSourceType.HARDCODED,
        identifier="default_user",
    )[0]
    payload = {
        "name": seed_user["name"],
        "username": "e2e_user_atividade5",
        "email": seed_user["email"],
    }

    logger = Logger(log_level="INFO", log_dir=str(tmp_path))
    rm = RequestManager(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=15,
        logger=logger,
    )

    created = rm.post("/users", json=payload)
    created_body = created.json()
    assert created.status_code == 201
    assert created_body["name"] == payload["name"]

    updated_payload = dict(payload)
    updated_payload["name"] = "e2e_user_updated"
    updated = rm.put("/users/1", json=updated_payload)
    updated_body = updated.json()
    assert updated.status_code == 200
    assert updated_body["name"] == "e2e_user_updated"

    deleted = rm.delete("/users/1")
    assert deleted.status_code in (200, 204)

    log_content = Path(tmp_path / "sentinela.log").read_text(encoding="utf-8")
    assert "HTTP POST https://jsonplaceholder.typicode.com/users" in log_content
    assert "HTTP PUT https://jsonplaceholder.typicode.com/users/1" in log_content
    assert "HTTP DELETE https://jsonplaceholder.typicode.com/users/1" in log_content
