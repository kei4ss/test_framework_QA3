"""Configuração compartilhada para os testes E2E da FakeStore API."""

import pytest
import requests

BASE_URL = "https://fakestoreapi.com"

_API_AVAILABLE: bool | None = None


def _api_is_available() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/products/1", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def _check_api() -> bool:
    global _API_AVAILABLE
    if _API_AVAILABLE is None:
        _API_AVAILABLE = _api_is_available()
    return _API_AVAILABLE


@pytest.fixture(autouse=True)
def skip_if_api_unavailable(request):
    """Pula testes E2E se a FakeStore API não estiver acessível."""
    markers = {m.name for m in request.node.iter_markers()}
    if markers & {"e2e"}:
        if not _check_api():
            pytest.skip(
                "FakeStore API não acessível a partir deste ambiente. "
                "Execute em uma máquina com acesso à internet pública."
            )