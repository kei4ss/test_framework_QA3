class UserFactory:
    """Factory centralizada para payloads de usuários."""

    @staticmethod
    def build(**overrides):
        payload = {
            "email": "qa_test@example.com",
            "username": "qa_tester",
            "password": "senha123",
            "name": {"firstname": "QA", "lastname": "Tester"},
            "address": {
                "city": "Brasilia",
                "street": "Rua QA",
                "number": 1,
                "zipcode": "00000-000",
                "geolocation": {"lat": "0", "long": "0"},
            },
            "phone": "99999-9999",
        }
        payload.update(overrides)
        return payload
