from typing import Optional, Dict, Any

import requests
from requests import Response, Timeout, RequestException


class RequestManager:

    _instance = None

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super(RequestManager, cls).__new__(cls)

        return cls._instance

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:


        if hasattr(self, "_initialized") and self._initialized:
            return

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        self.default_headers = default_headers or {
            "Content-Type": "application/json"
        }

        self.session.headers.update(self.default_headers)

        self._initialized = True

    def _build_url(self, endpoint: str) -> str:

        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _handle_response(self, response: Response) -> Dict[str, Any]:

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        return {
            "status_code": response.status_code,
            "success": response.ok,
            "data": response_data,
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        url = self._build_url(endpoint)

        request_headers = self.default_headers.copy()

        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return self._handle_response(response)

        except Timeout as error:
            raise Exception(
                f"Tempo limite excedido na requisição: {error}"
            ) from error

        except RequestException as error:
            raise Exception(
                f"Erro na requisição HTTP: {error}"
            ) from error

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Executa requisição GET.
        """

        return self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
            headers=headers,
        )

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:

        return self._request(
            method="POST",
            endpoint=endpoint,
            data=data,
            json=json,
            headers=headers,
        )

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:

        return self._request(
            method="PUT",
            endpoint=endpoint,
            data=data,
            json=json,
            headers=headers,
        )

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:

        return self._request(
            method="PATCH",
            endpoint=endpoint,
            data=data,
            json=json,
            headers=headers,
        )

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:


        return self._request(
            method="DELETE",
            endpoint=endpoint,
            headers=headers,
        )