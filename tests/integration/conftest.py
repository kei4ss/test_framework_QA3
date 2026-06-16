"""Configuração compartilhada para os testes da FakeStore API.

Inclui:
  - Fixture de verificação de conectividade (skip automático se API indisponível)
  - Fixture de RequestManager configurado para a FakeStore API
  - Fixture de credenciais válidas para autenticação
"""

import pytest
import requests

BASE_URL = "https://fakestoreapi.com"

VALID_CREDENTIALS = {
    "username": "mor_2314",
    "password": "83r5^_",
}


def _api_is_available() -> bool:
    """Verifica se a FakeStore API está acessível a partir do ambiente atual."""
    try:
        r = requests.get(f"{BASE_URL}/products/1", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


# Avalia uma única vez por sessão de testes
_API_AVAILABLE: bool | None = None


def _check_api() -> bool:
    global _API_AVAILABLE
    if _API_AVAILABLE is None:
        _API_AVAILABLE = _api_is_available()
    return _API_AVAILABLE


@pytest.fixture(autouse=True)
def skip_if_api_unavailable(request):
    """
    Pula automaticamente testes marcados como 'integration' ou 'e2e'
    se a FakeStore API não estiver acessível a partir do ambiente atual.

    Útil para ambientes sem acesso externo (sandbox, CI restrito).
    Para rodar os testes, certifique-se de que https://fakestoreapi.com
    está acessível a partir da máquina que executa a suite.
    """
    markers = {m.name for m in request.node.iter_markers()}
    if markers & {"integration", "e2e"}:
        if not _check_api():
            pytest.skip(
                "FakeStore API não acessível a partir deste ambiente "
                "(https://fakestoreapi.com retornou status != 200 ou erro de rede). "
                "Execute em uma máquina com acesso à internet pública."
            )