"""
Testes unitários para RequestManager.

Cobre:
- Comportamento singleton
- Métodos HTTP (GET, POST, PUT, PATCH, DELETE)
- Tratamento de erros e exceções
- Autenticação e headers customizados
- Parsing de JSON
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.infrastructure.request_manager import RequestManager


def _build_response(status_code=200, json_value=None, json_error=None):
    """
    Constrói um mock de Response para testes.
    
    Args:
        status_code: Status HTTP da resposta
        json_value: Valor de retorno de .json()
        json_error: Exceção a ser lançada por .json()
    
    Returns:
        MagicMock simulando uma resposta requests.Response
    """
    response = MagicMock()
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = json_value if json_value is not None else {"ok": True}
    return response


@pytest.mark.unit
class TestRequestManagerSingleton:
    """Testes do padrão Singleton do RequestManager."""
    
    def test_should_return_same_instance_when_initialized_multiple_times(self):
        """Múltiplas inicializações devem retornar a mesma instância."""
        # Arrange & Act
        first_instance = RequestManager(base_url="https://example.com")
        second_instance = RequestManager(base_url="https://another.com")
        
        # Assert
        assert first_instance is second_instance
        assert second_instance.base_url == "https://example.com"


@pytest.mark.unit
class TestRequestManagerGetMethod:
    """Testes do método GET do RequestManager."""
    
    def test_should_call_session_request_with_expected_parameters_when_get_invoked(self):
        """GET deve enviar parâmetros corretos para session.request."""
        # Arrange
        logger = MagicMock()
        manager = RequestManager(
            base_url="https://example.com",
            timeout=11,
            logger=logger,
        )
        response = _build_response()
        
        # Act
        with patch.object(manager._session, "request", return_value=response) as request_mock:
            result = manager.get("/users", params={"page": 1})
        
        # Assert
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


@pytest.mark.unit
class TestRequestManagerHttpMethods:
    """Testes dos métodos HTTP do RequestManager."""
    
    @pytest.mark.parametrize("method_name,verb", [
        ("post", "POST"),
        ("put", "PUT"),
        ("patch", "PATCH"),
        ("delete", "DELETE"),
    ])
    def test_should_call_session_request_with_correct_http_verb(
        self,
        method_name,
        verb,
    ):
        """Métodos HTTP devem usar o verbo HTTP correto."""
        # Arrange
        manager = RequestManager(
            base_url="https://example.com",
            timeout=22,
            logger=MagicMock(),
        )
        response = _build_response()
        
        # Act
        with patch.object(manager._session, "request", return_value=response) as request_mock:
            method = getattr(manager, method_name)
            method("/resource", json={"x": 1}, headers={"X-Test": "1"})
        
        # Assert
        request_mock.assert_called_once_with(
            method=verb,
            url="https://example.com/resource",
            params=None,
            data=None,
            json={"x": 1},
            headers={"X-Test": "1"},
            timeout=22,
        )


@pytest.mark.unit
class TestRequestManagerErrorHandling:
    """Testes do tratamento de erros do RequestManager."""
    
    def test_should_raise_timeout_exception_and_log_error_when_timeout_occurs(self):
        """Timeout deve ser propagado e logado como erro."""
        # Arrange
        logger = MagicMock()
        manager = RequestManager(
            base_url="https://example.com",
            logger=logger,
        )
        
        # Act & Assert
        with patch.object(
            manager._session,
            "request",
            side_effect=requests.Timeout("timeout"),
        ):
            with pytest.raises(requests.Timeout):
                manager.get("/slow")
        
        logger.error.assert_called()
    
    def test_should_raise_request_exception_and_log_error_when_network_fails(self):
        """Erro de rede deve ser propagado e logado como erro."""
        # Arrange
        logger = MagicMock()
        manager = RequestManager(
            base_url="https://example.com",
            logger=logger,
        )
        
        # Act & Assert
        with patch.object(
            manager._session,
            "request",
            side_effect=requests.RequestException("network error"),
        ):
            with pytest.raises(requests.RequestException):
                manager.get("/fail")
        
        logger.error.assert_called()
    
    def test_should_raise_value_error_when_json_parsing_fails_with_expect_json(self):
        """Erro ao parsear JSON com expect_json=True deve lançar ValueError."""
        # Arrange
        logger = MagicMock()
        manager = RequestManager(
            base_url="https://example.com",
            logger=logger,
        )
        response = _build_response(json_error=ValueError("invalid json"))
        
        # Act & Assert
        with patch.object(manager._session, "request", return_value=response):
            with pytest.raises(ValueError, match="Invalid JSON response"):
                manager.get("/users", expect_json=True)
        
        logger.error.assert_called()


@pytest.mark.unit
class TestRequestManagerJsonParsing:
    """Testes do parsing de JSON do RequestManager."""
    
    def test_should_return_parsed_json_when_expect_json_is_true(self):
        """expect_json=True deve retornar objeto parseado."""
        # Arrange
        manager = RequestManager(
            base_url="https://example.com",
            logger=MagicMock(),
        )
        response = _build_response(json_value={"id": 1, "name": "John"})
        
        # Act
        with patch.object(manager._session, "request", return_value=response):
            result = manager.get("/users/1", expect_json=True)
        
        # Assert
        assert result == {"id": 1, "name": "John"}


@pytest.mark.unit
class TestRequestManagerAuthentication:
    """Testes de autenticação do RequestManager."""
    
    def test_should_add_bearer_token_to_auth_header_when_token_is_set(self):
        """set_auth_token deve adicionar header Authorization com Bearer."""
        # Arrange
        manager = RequestManager(
            base_url="https://example.com",
            logger=MagicMock(),
        )
        manager.set_auth_token("abc123")
        response = _build_response()
        
        # Act
        with patch.object(manager._session, "request", return_value=response) as request_mock:
            manager.get("/secure")
        
        # Assert
        assert request_mock.call_args.kwargs["headers"]["Authorization"] == "Bearer abc123"
