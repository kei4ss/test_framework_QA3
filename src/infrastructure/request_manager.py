import time
from typing import Any, Dict, Optional

import requests

try:
    from src.config.settings import settings
except Exception:  # pragma: no cover - defensive fallback
    settings = None

try:
    from src.infraestructure.logger import Logger
except Exception:  # pragma: no cover - defensive fallback
    Logger = None


class RequestManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        logger: Any = None,
    ):
        if self._initialized:
            return

        config_base_url, config_timeout = self._load_defaults_from_settings()
        self.base_url = (base_url or config_base_url or "").rstrip("/")
        self.timeout = timeout if timeout is not None else config_timeout
        self.default_headers = headers.copy() if headers else {}
        self._session = requests.Session()
        self._logger = logger if logger is not None else self._build_logger()
        self._initialized = True

    @classmethod
    def get_instance(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def _reset_instance(cls):
        cls._instance = None
        cls._initialized = False

    def set_base_url(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        return self

    def set_timeout(self, timeout: int):
        self.timeout = timeout
        return self

    def set_default_header(self, key: str, value: str):
        self.default_headers[key] = value
        return self

    def set_auth_token(self, token: str):
        self.default_headers["Authorization"] = f"Bearer {token}"
        return self

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        expect_json: bool = False,
    ):
        url = self._build_url(endpoint)
        merged_headers = {**self.default_headers, **(headers or {})}
        timeout_to_use = self.timeout if timeout is None else timeout

        start = time.monotonic()
        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=merged_headers,
                timeout=timeout_to_use,
            )
            elapsed = time.monotonic() - start
            self._log_request(method, url, response.status_code, elapsed)
            response.raise_for_status()

            if expect_json:
                try:
                    return response.json()
                except ValueError as exc:
                    self._log_error("Invalid JSON response for %s %s: %s", method.upper(), url, exc)
                    raise ValueError(f"Invalid JSON response from {url}") from exc

            return response
        except requests.Timeout as exc:
            self._log_error("Timeout during %s %s: %s", method.upper(), url, exc)
            raise
        except requests.RequestException as exc:
            self._log_error("Request failed during %s %s: %s", method.upper(), url, exc)
            raise

    def get(self, endpoint: str, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs):
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)

    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{self.base_url}{endpoint}"

    def _build_logger(self):
        if Logger is None:
            return None
        try:
            return Logger()
        except Exception:
            return None

    def _load_defaults_from_settings(self):
        if settings is None:
            return None, 30
        try:
            cfg = settings()
            api_cfg = cfg.api_config()
            perf_cfg = cfg.performance_config()
            return api_cfg.get("base_url"), perf_cfg.get("timeout", 30)
        except Exception:
            return None, 30

    def _log_request(self, method: str, url: str, status_code: int, elapsed: float):
        if self._logger is None:
            return
        if hasattr(self._logger, "log_request"):
            self._logger.log_request(method, url, status_code, elapsed)
        elif hasattr(self._logger, "info"):
            self._logger.info(
                "HTTP %s %s -> %s (%.3fs)",
                method.upper(),
                url,
                status_code,
                elapsed,
            )

    def _log_error(self, message: str, *args):
        if self._logger is not None and hasattr(self._logger, "error"):
            self._logger.error(message, *args)
