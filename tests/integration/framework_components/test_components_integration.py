"""Testes de integração entre componentes centrais do framework.

Valida que os componentes principais (RequestManager, DataProvider, Logger)
funcionam corretamente quando integrados.
"""

from pathlib import Path

import pytest

from src.config.data_provider_config import DataSourceType
from src.infrastructure.logger.logger import Logger
from src.infrastructure.requestManager.request_manager import RequestManager
from src.utils.data_provider import DataProvider


def _build_payload_from_provider():
    """Constrói payload de usuário a partir do DataProvider."""
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


@pytest.mark.integration
@pytest.mark.framework_component
class TestRequestManagerAndLoggerIntegration:
    """Testes de integração entre RequestManager e Logger."""
    
    def test_should_log_http_request_when_request_manager_makes_call(self, tmp_path):
        """Validar que RequestManager registra requisições no Logger."""
        # Arrange
        logger = Logger(log_level="INFO", log_dir=str(tmp_path))
        rm = RequestManager(
            base_url="https://jsonplaceholder.typicode.com",
            timeout=15,
            logger=logger,
        )
        
        # Act
        response = rm.get("/users/1")
        
        # Assert
        assert response.status_code == 200
        log_content = Path(tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "HTTP GET https://jsonplaceholder.typicode.com/users/1" in log_content
        assert "200" in log_content


@pytest.mark.integration
@pytest.mark.framework_component
class TestRequestManagerAndDataProviderIntegration:
    """Testes de integração entre RequestManager e DataProvider."""
    
    def test_should_post_user_data_from_data_provider(self):
        """Validar que dados do DataProvider funcionam com RequestManager."""
        # Arrange
        rm = RequestManager(
            base_url="https://jsonplaceholder.typicode.com",
            timeout=15,
        )
        payload = _build_payload_from_provider()
        
        # Act
        response = rm.post("/users", json=payload)
        body = response.json()
        
        # Assert
        assert response.status_code == 201
        assert body["name"] == payload["name"]
        assert body["email"] == payload["email"]


@pytest.mark.integration
@pytest.mark.framework_component
class TestFullComponentIntegration:
    """Testes de integração completa entre todos os componentes."""
    
    def test_should_complete_full_flow_data_request_response_logging(self, tmp_path):
        """Validar fluxo completo: Data → Request → Response → Logger → Assertions."""
        # Arrange
        logger = Logger(log_level="INFO", log_dir=str(tmp_path))
        rm = RequestManager(
            base_url="https://jsonplaceholder.typicode.com",
            timeout=15,
            logger=logger,
        )
        payload = _build_payload_from_provider()
        
        # Act
        response = rm.post("/users", json=payload)
        body = response.json()
        
        # Assert: Response
        assert response.status_code == 201
        assert body["name"] == payload["name"]
        assert body["email"] == payload["email"]
        
        # Assert: Logging
        log_content = Path(tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "HTTP POST https://jsonplaceholder.typicode.com/users" in log_content
        assert "201" in log_content

