"""Testes de integração para os endpoints de Users da FakeStore API.

Cobre todos os endpoints disponíveis:
  GET    /users                            - listar todos os usuários
  GET    /users/{id}                       - buscar usuário por ID
  GET    /users?limit={n}                  - listar com limite
  GET    /users?sort={asc|desc}            - listar ordenado
  POST   /users                            - criar usuário
  PUT    /users/{id}                       - atualizar usuário (completo)
  PATCH  /users/{id}                       - atualizar usuário (parcial)
  DELETE /users/{id}                       - deletar usuário
"""

import pytest

from tests.shared.factories.user_factory import UserFactory
from tests.shared.helpers.response_assertions import (
    USER_REQUIRED_KEYS,
    assert_successful_list_response,
    assert_user_address_structure,
    assert_user_email_valid,
    assert_user_geolocation,
    assert_user_has_required_fields,
    assert_user_name_structure,
    create_user,
    delete_user,
    patch_user,
    update_user,
)

NEW_USER_PAYLOAD = UserFactory.build(
    email="qa_test@example.com",
    username="qa_tester_framework",
    password="senha_segura_123",
    name={
        "firstname": "QA",
        "lastname": "Tester",
    },
    address={
        "city": "Brasília",
        "street": "QS 1 Conjunto 10",
        "number": 42,
        "zipcode": "71980-000",
        "geolocation": {
            "lat": "-15.7801",
            "long": "-47.9292",
        },
    },
    phone="61-99999-0000",
)


# ---------------------------------------------------------------------------
# GET /users
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetAllUsers:
    """Testes do endpoint GET /users."""

    def test_deve_retornar_status_200_e_lista_de_usuarios(self, client):
        """GET /users deve retornar 200 e uma lista não-vazia de usuários."""
        body = assert_successful_list_response(
            client.get("/users"), expected_keys=USER_REQUIRED_KEYS, min_length=1
        )
        assert len(body) > 0

    def test_cada_usuario_deve_conter_campos_obrigatorios(self, client):
        """Cada usuário na listagem deve conter os campos obrigatórios."""
        body = assert_successful_list_response(client.get("/users"))

        for user in body:
            assert_user_has_required_fields(user)

    def test_campo_name_deve_conter_firstname_e_lastname(self, client):
        """O campo 'name' de cada usuário deve ter 'firstname' e 'lastname'."""
        body = assert_successful_list_response(client.get("/users"))

        for user in body:
            assert_user_name_structure(user)

    def test_campo_address_deve_ter_estrutura_correta(self, client):
        """O campo 'address' deve conter cidade, rua, número e CEP."""
        body = assert_successful_list_response(client.get("/users"))

        for user in body:
            assert_user_address_structure(user)

    def test_email_dos_usuarios_deve_conter_arroba(self, client):
        """O campo 'email' de cada usuário deve conter '@'."""
        body = assert_successful_list_response(client.get("/users"))

        for user in body:
            assert_user_email_valid(user)

    def test_deve_retornar_10_usuarios_por_padrao(self, client):
        """A API deve retornar exatamente 10 usuários na listagem padrão."""
        body = assert_successful_list_response(client.get("/users"))
        assert len(body) == 10


# ---------------------------------------------------------------------------
# GET /users?limit={n}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetUsersWithLimit:
    """Testes do endpoint GET /users?limit={n}."""

    @pytest.mark.parametrize("limit", [1, 3, 5])
    def test_deve_respeitar_parametro_limit(self, client, limit):
        """GET /users?limit={n} deve retornar exatamente n usuários."""
        response = client.get("/users", params={"limit": limit})
        body = response.json()

        assert response.status_code == 200
        assert len(body) == limit


# ---------------------------------------------------------------------------
# GET /users?sort={asc|desc}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetUsersSorted:
    """Testes do endpoint GET /users?sort={asc|desc}."""

    def test_sort_asc_deve_retornar_usuarios_em_ordem_crescente(self, client):
        """GET /users?sort=asc deve retornar usuários com IDs em ordem crescente."""
        response = client.get("/users", params={"sort": "asc"})
        body = response.json()

        assert response.status_code == 200
        ids = [u["id"] for u in body]
        assert ids == sorted(ids)

    def test_sort_desc_deve_retornar_usuarios_em_ordem_decrescente(self, client):
        """GET /users?sort=desc deve retornar usuários com IDs em ordem decrescente."""
        response = client.get("/users", params={"sort": "desc"})
        body = response.json()

        assert response.status_code == 200
        ids = [u["id"] for u in body]
        assert ids == sorted(ids, reverse=True)


# ---------------------------------------------------------------------------
# GET /users/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetSingleUser:
    """Testes do endpoint GET /users/{id}."""

    @pytest.mark.parametrize("user_id", [1, 2, 5, 10])
    def test_deve_retornar_usuario_com_id_valido(self, client, user_id):
        """GET /users/{id} com ID válido deve retornar 200 e os dados do usuário."""
        response = client.get(f"/users/{user_id}")
        body = response.json()

        assert response.status_code == 200
        assert body["id"] == user_id
        assert_user_has_required_fields(body)

    def test_deve_retornar_404_para_id_inexistente(self, client):
        """GET /users/{id} com ID inexistente deve retornar 404."""
        response = client.get("/users/99999")

        assert response.status_code == 404

    def test_usuario_deve_ter_geolocalizacao_no_endereco(self, client):
        """O campo 'address.geolocation' deve conter 'lat' e 'long'."""
        response = client.get("/users/1")
        body = response.json()

        assert_user_geolocation(body)


# ---------------------------------------------------------------------------
# POST /users
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPostUser:
    """Testes do endpoint POST /users."""

    def test_deve_retornar_status_200_ao_criar_usuario(self, client):
        """POST /users com payload válido deve retornar 200 e o usuário criado."""
        body = create_user(client, NEW_USER_PAYLOAD)

        assert body["email"] == NEW_USER_PAYLOAD["email"]
        assert body["username"] == NEW_USER_PAYLOAD["username"]

    def test_usuario_criado_deve_ter_id_atribuido(self, client):
        """O usuário criado deve receber um ID gerado pela API."""
        body = create_user(client, NEW_USER_PAYLOAD)

        assert "id" in body
        assert isinstance(body["id"], int)

    def test_nome_do_usuario_criado_deve_bater_com_payload(self, client):
        """O campo 'name' do usuário criado deve refletir o payload enviado."""
        body = create_user(client, NEW_USER_PAYLOAD)

        assert body["name"]["firstname"] == NEW_USER_PAYLOAD["name"]["firstname"]
        assert body["name"]["lastname"] == NEW_USER_PAYLOAD["name"]["lastname"]


# ---------------------------------------------------------------------------
# PUT /users/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPutUser:
    """Testes do endpoint PUT /users/{id}."""

    def test_deve_retornar_status_200_ao_atualizar_usuario(self, client):
        """PUT /users/{id} deve retornar 200 e os dados atualizados."""
        updated_payload = {**NEW_USER_PAYLOAD, "username": "usuario_atualizado_put"}
        body = update_user(client, 1, updated_payload)

        assert body["username"] == "usuario_atualizado_put"

    def test_put_deve_atualizar_email(self, client):
        """PUT deve permitir atualizar o e-mail do usuário."""
        updated_payload = {**NEW_USER_PAYLOAD, "email": "novo_email@qa.com"}
        body = update_user(client, 1, updated_payload)

        assert body["email"] == "novo_email@qa.com"


# ---------------------------------------------------------------------------
# PATCH /users/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPatchUser:
    """Testes do endpoint PATCH /users/{id}."""

    def test_deve_retornar_status_200_ao_atualizar_parcialmente(self, client):
        """PATCH /users/{id} deve retornar 200 com campos atualizados."""
        partial_payload = {"phone": "61-88888-1234"}
        body = patch_user(client, 1, partial_payload)

        assert body["phone"] == "61-88888-1234"

    def test_patch_de_email_deve_atualizar_somente_email(self, client):
        """PATCH com apenas 'email' deve atualizar somente esse campo."""
        partial_payload = {"email": "patch_email@qa.com"}
        body = patch_user(client, 1, partial_payload)

        assert body["email"] == "patch_email@qa.com"


# ---------------------------------------------------------------------------
# DELETE /users/{id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDeleteUser:
    """Testes do endpoint DELETE /users/{id}."""

    def test_deve_retornar_status_200_ao_deletar_usuario(self, client):
        """DELETE /users/{id} deve retornar 200 e o usuário deletado."""
        body = delete_user(client, 1)

        assert body["id"] == 1

    @pytest.mark.parametrize("user_id", [1, 2, 5])
    def test_delete_de_diferentes_usuarios_deve_retornar_200(self, client, user_id):
        """DELETE de diferentes IDs válidos deve sempre retornar 200."""
        delete_user(client, user_id)
