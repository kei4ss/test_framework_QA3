"""Testes de integração da API com JSONPlaceholder.

Este módulo contém testes que validam a integração entre
o RequestManager e a API externa (JSONPlaceholder).

Nota: Estes testes usam a API real em https://jsonplaceholder.typicode.com
Para ambiente offline, considere usar mocks HTTP (responses library).
"""

import pytest
from requests import RequestException

from src.config.data_provider_config import DataSourceType
from src.infrastructure.logger.logger import Logger
from src.infrastructure.requestManager.request_manager import RequestManager
from src.utils.data_provider import DataProvider


@pytest.fixture
def api_request_manager():
    """Cria um RequestManager configurado para JSONPlaceholder."""
    return RequestManager(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=15,
    )


def _provider_payload():
    """Constrói payload de usuário a partir do DataProvider."""
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


@pytest.mark.integration
class TestGetUsersEndpoint:
    """Testes do endpoint GET /users."""
    
    def test_should_return_status_200_and_user_list_when_listing_all_users(
        self,
        api_request_manager,
    ):
        """GET /users deve retornar status 200 e lista de usuários com estrutura básica."""
        # Act
        response = api_request_manager.get("/users")
        body = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(body, list)
        assert len(body) > 0
        assert {"id", "name", "username", "email"}.issubset(body[0].keys())
    
    @pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
    def test_should_return_status_200_when_fetching_user_with_valid_id(
        self,
        api_request_manager,
        user_id,
    ):
        """GET /users/{id} com IDs válidos deve retornar status 200."""
        # Act
        response = api_request_manager.get(f"/users/{user_id}")
        body = response.json()
        
        # Assert
        assert response.status_code == 200
        assert body["id"] == user_id
        assert {"id", "name", "username", "email"}.issubset(body.keys())
    
    def test_should_handle_invalid_user_id_gracefully(self, api_request_manager):
        """GET /users/{id_invalido} valida comportamento esperado da API."""
        # Act & Assert
        try:
            response = api_request_manager.get("/users/99999")
            body = response.json()
            assert response.status_code == 200
            assert body == {} or body == []
        except RequestException as exc:
            assert isinstance(exc, RequestException)


@pytest.mark.integration
class TestPostUsersEndpoint:
    """Testes do endpoint POST /users."""
    
    def test_should_return_status_201_when_creating_user_with_valid_data(
        self,
        api_request_manager,
    ):
        """POST /users com dados válidos deve retornar 201."""
        # Arrange
        payload = _provider_payload()
        
        # Act
        response = api_request_manager.post("/users", json=payload)
        body = response.json()
        
        # Assert
        assert response.status_code == 201
        assert body["name"] == payload["name"]
        assert body["email"] == payload["email"]


@pytest.mark.integration
class TestPutUsersEndpoint:
    """Testes do endpoint PUT /users."""
    
    def test_should_return_status_200_when_updating_user(self, api_request_manager):
        """PUT /users/{id} deve retornar 200 e dados modificados."""
        # Arrange
        payload = _provider_payload()
        payload["name"] = "Updated Name"
        
        # Act
        response = api_request_manager.put("/users/1", json=payload)
        body = response.json()
        
        # Assert
        assert response.status_code == 200
        assert body["name"] == "Updated Name"
        assert body["email"] == payload["email"]


@pytest.mark.integration
class TestDeleteUsersEndpoint:
    """Testes do endpoint DELETE /users."""
    
    def test_should_return_status_200_or_204_when_deleting_user(
        self,
        api_request_manager,
    ):
        """DELETE /users/{id} deve retornar 200 ou 204."""
        # Act
        response = api_request_manager.delete("/users/1")
        
        # Assert
        assert response.status_code in (200, 204)


@pytest.mark.integration
class TestErrorHandling:
    """Testes de tratamento de erros de API."""
    
    def test_should_raise_request_exception_when_endpoint_is_invalid(
        self,
        api_request_manager,
    ):
        """Endpoint inválido deve gerar erro HTTP e não sucesso silencioso."""
        # Act & Assert
        with pytest.raises(RequestException):
            api_request_manager.get("/endpoint-invalido-atividade5")

