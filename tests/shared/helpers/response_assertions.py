from src.infrastructure.schemaValidation import SchemaValidator

USER_REQUIRED_KEYS = {"id", "email", "username", "password", "name", "address", "phone"}


def assert_successful_list_response(response, expected_keys=None, min_length=1, schema=None):
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= min_length
    if expected_keys and body:
        assert expected_keys.issubset(body[0].keys())
    if schema is not None:
        SchemaValidator.validate_many(body, schema)
    return body


def assert_user_has_required_fields(user, expected_keys=USER_REQUIRED_KEYS):
    assert expected_keys.issubset(user.keys()), (
        f"Usuário id={user.get('id')} não contém todos os campos obrigatórios."
    )


def assert_user_name_structure(user):
    assert "firstname" in user["name"]
    assert "lastname" in user["name"]


def assert_user_address_structure(user):
    address = user["address"]
    for field in ("city", "street", "number", "zipcode"):
        assert field in address, (
            f"Usuário id={user['id']} sem campo '{field}' no endereço."
        )


def assert_user_email_valid(user):
    assert "@" in user["email"], (
        f"Usuário id={user['id']} tem email inválido: {user['email']}"
    )


def assert_user_geolocation(user):
    geo = user["address"]["geolocation"]
    assert "lat" in geo
    assert "long" in geo


def assert_schema(response, schema):
    body = response.json()
    SchemaValidator.validate(body, schema)
    return body


def assert_successful_action_response(response, expected_status=200, schema=None):
    assert response.status_code == expected_status
    body = response.json()
    if schema is not None:
        SchemaValidator.validate(body, schema)
    return body


def create_user(client, payload, schema=None):
    response = client.post("/users", json=payload)
    return assert_successful_action_response(response, expected_status=201, schema=schema)


def update_user(client, user_id, payload, schema=None):
    response = client.put(f"/users/{user_id}", json=payload)
    return assert_successful_action_response(response, schema=schema)


def patch_user(client, user_id, payload, schema=None):
    response = client.patch(f"/users/{user_id}", json=payload)
    return assert_successful_action_response(response, schema=schema)


def delete_user(client, user_id, schema=None):
    response = client.delete(f"/users/{user_id}")
    return assert_successful_action_response(response, schema=schema)
