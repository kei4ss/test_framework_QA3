"""Testes E2E do fluxo de ciclo de vida de usuário.

Este módulo valida fluxos completos que envolvem múltiplas operações
(CREATE, READ, UPDATE, DELETE) contra a API JSONPlaceholder.
"""

from pathlib import Path

import pytest

from src.config.data_provider_config import DataSourceType
from src.infrastructure.logger.logger import Logger
from src.infrastructure.requestManager.request_manager import RequestManager
from src.utils.data_provider import DataProvider


@pytest.mark.e2e
class TestUserLifecycle:
    """Testes do ciclo de vida completo de usuários."""
    
    def test_should_complete_full_user_lifecycle_create_update_delete(self, tmp_path):
        """Teste E2E: obter dado → criar → atualizar → deletar → validar logs."""
        # Arrange
        provider = DataProvider()
        seed_user = provider.get_data(
            source=DataSourceType.HARDCODED,
            identifier="default_user",
        )[0]
        create_payload = {
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
        
        # Act: CREATE
        created_response = rm.post("/users", json=create_payload)
        created_body = created_response.json()
        
        # Assert: CREATE
        assert created_response.status_code == 201
        assert created_body["name"] == create_payload["name"]
        assert created_body["email"] == create_payload["email"]
        
        # Act: UPDATE
        update_payload = dict(create_payload)
        update_payload["name"] = "e2e_user_updated"
        updated_response = rm.put("/users/1", json=update_payload)
        updated_body = updated_response.json()
        
        # Assert: UPDATE
        assert updated_response.status_code == 200
        assert updated_body["name"] == "e2e_user_updated"
        assert updated_body["email"] == update_payload["email"]
        
        # Act: DELETE
        deleted_response = rm.delete("/users/1")
        
        # Assert: DELETE
        assert deleted_response.status_code in (200, 204)
        
        # Assert: LOGGING
        log_content = Path(tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "HTTP POST https://jsonplaceholder.typicode.com/users" in log_content
        assert "HTTP PUT https://jsonplaceholder.typicode.com/users/1" in log_content
        assert "HTTP DELETE https://jsonplaceholder.typicode.com/users/1" in log_content

