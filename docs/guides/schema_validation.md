# Schema Validation no Framework

## Objetivo

Adicionar validação de contrato de resposta JSON no framework de automação, com foco em respostas de API.

## Ferramenta escolhida

A biblioteca adotada foi `jsonschema`.

### Por que `jsonschema`

- é a solução mais aderente para validar respostas JSON de API usando JSON Schema;
- funciona sem acoplar o contrato aos modelos Python da aplicação;
- se encaixa bem em testes de contrato, integração e regressão;
- permite versionar schemas localmente no repositório;
- produz erros objetivos quando um campo obrigatório, tipo ou estrutura deixa de seguir o contrato.

## Alternativas avaliadas

### `pydantic`

Boa opção para modelagem e parsing de objetos Python. Não foi escolhida como implementação principal porque a necessidade desta atividade é validar contrato JSON de API com baixo acoplamento aos modelos internos.

### `cerberus`

É simples para regras de validação, mas menos padrão para contratos JSON de API do que JSON Schema.

### OpenAPI / Swagger

É a melhor opção quando a aplicação expõe um contrato oficial. Permite derivar ou reutilizar schemas diretamente da especificação da API.

## Decisão atual

Nesta atividade, a decisão foi usar `jsonschema` com schemas versionados localmente.

Motivos:

- o projeto atual consome a API pública JSONPlaceholder;
- não existe hoje, no framework, um pipeline de consumo automático de contrato OpenAPI;
- a execução no sandbox já tem limitação de rede, então depender de descoberta remota do schema reduziria a previsibilidade dos testes.

## Possibilidade de obtenção automática de schema

Há dois caminhos principais:

1. Consumir um arquivo OpenAPI/Swagger publicado pela aplicação.
2. Gerar um baseline de schema a partir de respostas reais e revisá-lo manualmente antes de versionar.

### Recomendação futura

Quando a aplicação-alvo expuser OpenAPI/Swagger de forma estável, o ideal é substituir ou complementar os schemas locais com carregamento automatizado do contrato oficial.

## Estrutura adicionada

### Módulo de infraestrutura

- `src/infrastructure/schemaValidation/schema_loader.py`
- `src/infrastructure/schemaValidation/schema_validator.py`

### Schemas versionados

- `tests/shared/fixtures/schemas/jsonplaceholder/user_schema.json`
- `tests/shared/fixtures/schemas/jsonplaceholder/users_list_schema.json`
- `tests/shared/fixtures/schemas/jsonplaceholder/create_user_response_schema.json`

### Testes unitários

- `tests/unit/infrastructure/test_schema_loader.py`
- `tests/unit/infrastructure/test_schema_validator.py`

## Como usar nos testes

Exemplo de uso:

```python
from pathlib import Path

from src.infrastructure.schemaValidation import SchemaLoader, SchemaValidator

schemas_dir = Path("tests/shared/fixtures/schemas/jsonplaceholder")
user_schema = SchemaLoader.load(schemas_dir / "user_schema.json")

response = api_request_manager.get("/users/1")
body = response.json()

SchemaValidator.validate(body, user_schema)
```

## Integração aplicada nesta atividade

Foram integrados checks de schema em três fluxos de API já existentes:

- `GET /users`
- `GET /users/{id}`
- `POST /users`

## Limitações atuais

- testes de integração e e2e continuam dependentes de rede para acessar JSONPlaceholder;
- no sandbox atual, chamadas externas podem falhar por bloqueio de rede;
- os schemas locais precisam ser revisados manualmente se o contrato da API de destino mudar;
- esta implementação valida contrato JSON, mas não substitui validação semântica de negócio.
