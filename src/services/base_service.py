"""Classe base para todos os services da camada de serviço.

Encapsula a criação e configuração do RequestManager,
fornecendo uma interface comum para os services concretos.
"""

from typing import Optional
from src.infrastructure.requestManager.request_manager import RequestManager


class BaseService:
    """Classe base que encapsula o RequestManager para uso nos services.

    Todos os services da aplicação devem herdar desta classe, que
    provê acesso ao cliente HTTP já configurado com a base URL e timeout
    corretos para a FakeStore API.

    Uso:
        class MeuService(BaseService):
            def minha_acao(self):
                return self._client.get("/meu-endpoint")
    """

    BASE_URL: str = "https://fakestoreapi.com"
    DEFAULT_TIMEOUT: int = 15

    def __init__(
        self,
        client: Optional[RequestManager] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """Inicializa o service com um RequestManager.

        Args:
            client: Instância de RequestManager já configurada. Se não
                    fornecida, uma nova instância é criada com os valores
                    padrão da classe.
            base_url: URL base da API. Se não fornecida, usa BASE_URL.
            timeout: Timeout em segundos. Se não fornecido, usa DEFAULT_TIMEOUT.
        """
        if client is not None:
            self._client = client
        else:
            self._client = RequestManager(
                base_url=base_url or self.BASE_URL,
                timeout=timeout if timeout is not None else self.DEFAULT_TIMEOUT,
            )

    def set_auth_token(self, token: str) -> "BaseService":
        """Configura o token de autenticação Bearer para requisições subsequentes.

        Args:
            token: Token JWT obtido via AuthService.login().

        Returns:
            self, para encadeamento de chamadas.
        """
        self._client.set_auth_token(token)
        return self
