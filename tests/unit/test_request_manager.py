from unittest.mock import MagicMock, patch

import pytest
import requests

from src.infrastructure.request_manager import RequestManager


@pytest.fixture(autouse=True)
def reset_request_manager_singleton():
    RequestManager._reset_instance()
    yield
    RequestManager._reset_instance()


def _build_response(status_code=200, json_value=None, json_error=None):
    response = MagicMock()
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = json_value if json_value is not None else {"ok": True}
    return response


def test_singleton_returns_same_instance():
    a = RequestManager(base_url="https://example.com")
    b = RequestManager(base_url="https://another.com")
    assert a is b
    assert b.base_url == "https://example.com"


def test_get_calls_requests_with_expected_args():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", timeout=11, logger=logger)
    response = _build_response()

    with patch.object(manager._session, "request", return_value=response) as request_mock:
        result = manager.get("/users", params={"page": 1})

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


@pytest.mark.parametrize("method_name,verb", [
    ("post", "POST"),
    ("put", "PUT"),
    ("patch", "PATCH"),
    ("delete", "DELETE"),
])
def test_http_methods_call_requests_correctly(method_name, verb):
    manager = RequestManager(base_url="https://example.com", timeout=22, logger=MagicMock())
    response = _build_response()

    with patch.object(manager._session, "request", return_value=response) as request_mock:
        method = getattr(manager, method_name)
        method("/resource", json={"x": 1}, headers={"X-Test": "1"})

    request_mock.assert_called_once_with(
        method=verb,
        url="https://example.com/resource",
        params=None,
        data=None,
        json={"x": 1},
        headers={"X-Test": "1"},
        timeout=22,
    )


def test_timeout_exception_is_raised_and_logged():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", logger=logger)

    with patch.object(manager._session, "request", side_effect=requests.Timeout("timeout")):
        with pytest.raises(requests.Timeout):
            manager.get("/slow")

    logger.error.assert_called()


def test_request_exception_is_raised_and_logged():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", logger=logger)

    with patch.object(manager._session, "request", side_effect=requests.RequestException("network")):
        with pytest.raises(requests.RequestException):
            manager.get("/fail")

    logger.error.assert_called()


def test_invalid_json_response_raises_value_error_and_logs():
    logger = MagicMock()
    manager = RequestManager(base_url="https://example.com", logger=logger)
    response = _build_response(json_error=ValueError("invalid json"))

    with patch.object(manager._session, "request", return_value=response):
        with pytest.raises(ValueError, match="Invalid JSON response"):
            manager.get("/users", expect_json=True)

    logger.error.assert_called()


def test_expect_json_returns_parsed_json():
    manager = RequestManager(base_url="https://example.com", logger=MagicMock())
    response = _build_response(json_value={"id": 1})

    with patch.object(manager._session, "request", return_value=response):
        result = manager.get("/users/1", expect_json=True)

    assert result == {"id": 1}


def test_auth_header_is_applied():
    manager = RequestManager(base_url="https://example.com", logger=MagicMock())
    manager.set_auth_token("abc")
    response = _build_response()

    with patch.object(manager._session, "request", return_value=response) as request_mock:
        manager.get("/secure")

    assert request_mock.call_args.kwargs["headers"]["Authorization"] == "Bearer abc"
