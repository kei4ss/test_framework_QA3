"""Configuração centralizada de fixtures e hooks para a suíte de testes."""

import pytest
from unittest.mock import MagicMock

from src.infrastructure.request_manager import RequestManager
from src.utils.data_provider import DataProvider
from src.infraestructure.logger import Logger


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reseta todas as instâncias de singletons entre testes.
    
    Garante isolamento entre testes, evitando contaminação de estado.
    Marcadores: unit, integration, e2e
    """
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
def mock_logger():
    """
    Fornece um logger mock para testes unitários.
    
    Uso: def test_example(mock_logger): ...
    """
    return MagicMock()


@pytest.fixture
def request_manager_with_mock_logger(mock_logger):
    """
    Cria um RequestManager com logger mockado.
    
    Uso: def test_example(request_manager_with_mock_logger): ...
    """
    return RequestManager(
        base_url="https://example.com",
        timeout=10,
        logger=mock_logger,
    )


def pytest_configure(config):
    """Hook para configuração inicial do pytest."""
    config.addinivalue_line(
        "markers",
        "unit: marca testes unitários",
    )
    config.addinivalue_line(
        "markers",
        "integration: marca testes de integração",
    )
    config.addinivalue_line(
        "markers",
        "e2e: marca testes ponta-a-ponta",
    )
