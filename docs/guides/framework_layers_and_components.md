# Framework Layers and Components

## Visão geral
Este documento descreve como as camadas do framework se conectam e como a Atividade 5 valida o fluxo ponta a ponta usando a trilha Python.

## Camada de Testes (pytest)
- Local: `tests/unit`, `tests/integration`, `tests/e2e`
- Responsabilidade: validar comportamento isolado, integração entre componentes e fluxo completo.
- Atividade 5 adiciona:
  - `tests/integration/test_components_integration.py`
  - `tests/integration/test_api_integration.py`
  - `tests/e2e/test_user_lifecycle.py`

## Camada RequestManager
- Implementação validada: `src/infrastructure/request_manager.py`
- Responsabilidade:
  - Encapsular chamadas HTTP via `requests`
  - Aplicar base URL, timeout e headers padrão
  - Expor métodos `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
  - Integrar com Logger para registrar requisições e falhas

## Camada Data Provider
- Implementação: `src/utils/data_provider.py`
- Responsabilidade:
  - Fornecer dados de teste por múltiplas fontes (JSON, CSV, hardcoded)
  - Permitir fallback entre fontes e validação de dados

## Camada Logger
- Implementação: `src/infraestructure/logger.py`
- Responsabilidade:
  - Registrar eventos em console e arquivo rotativo
  - Registrar requisições HTTP por `log_request`
  - Mascarar dados sensíveis

## Camada de Configuração
- Implementação principal: `src/config/settings.py`
- Responsabilidade:
  - Carregar variáveis de ambiente e disponibilizar configurações globais, de API e de performance
  - Suportar fallback para `.env`, `.env.test` e `.env.example` para execução segura em testes

## Camada de Validação / Assertions
- Implementada por `pytest` com asserts explícitos:
  - status code
  - estrutura de payload
  - campos obrigatórios
  - conteúdo de logs

## Fluxo completo validado na Atividade 5
1. Data Provider gera/carrega payload de usuário.
2. RequestManager envia requisição para JSONPlaceholder.
3. Response retorna dados e status para asserções.
4. Logger registra operação HTTP.
5. Testes confirmam status, payload e log.

Esse fluxo é validado tanto em integração quanto em E2E para comprovar o funcionamento conjunto dos componentes.

## Limitação conhecida da API de teste
JSONPlaceholder simula operações de escrita (`POST`, `PUT`, `DELETE`) e retorna respostas coerentes, porém não persiste alterações no backend.
Por isso, os testes da Atividade 5 validam status code, payload de resposta e logs, sem exigir persistência posterior dos dados.

## Governança técnica
Existe um RequestManager JavaScript legado em `src/infraestructure/requestManager.js`.
Para a Atividade 5, a trilha validada é a implementação Python `src/infrastructure/request_manager.py`, por compatibilidade direta com `pytest`, `Logger` e `DataProvider`.
