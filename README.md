# Sentenela project
Este projeto tem como objetivo a concepção, desenvolvimento e implementação de
uma estrutura (framework) de automação para testes de API. O objetivo é criar uma
ferramenta robusta, escalável e de fácil manutenção, capaz de validar não apenas as
respostas e os esquemas dos endpoints, mas também a lógica de negócios e a
integridade dos dados no sistema em teste. 

De maneira geral, temos o propósito de fornecer camadas reutilizáveis e utilitários para escrever e executar testes E2E, de integração e unitários de forma consistente.


## Objetivos

- [ ] **Validar a lógica de negócios**: Abranger cenários positivos, negativos, de limite
(boundary) e fluxos de ponta a ponta (E2E).

- [ ] **Garantir a integridade dos dados**: Implementar validações de esquemas (JSON
Schema) e verificar a integridade dos dados ao realizar solicitações de
API.Generative
 
- [ ] **IA**: Utilizar a GenAI para criar conjuntos de dados complexos, otimizar a geração de
scripts de teste e otimizar a refatoração de código.
 
- [ ] **Reportar com clareza**: Gerar logs detalhados e relatórios visuais de execução que
permitam identificar falhas rapidamente.

- [ ] **Escalabilidade**: Suportar execução paralela, estratégias de "falha rápida" (fail-fast)
e testes de carga/desempenho.


## Camadas e Responsabilidades
- **src/config**: Configurações do framework e provedores de dados. Arquivos principais: [src/config/settings.py](src/config/settings.py)
- **src/infrastructure/logger**: Logger centralizado usado por serviços e testes.
- **src/infrastructure/requestManager**: Gerencia chamadas HTTP e timeouts.
- **src/infrastructure/reportManager**: Gera/empacota relatórios em PDF e processa resultados de execução.
- **src/services**: Implementações de serviços que encapsulam lógica de chamada de API (ex.: `user_service`, `product_service`).
- **src/utils**: Utilitários para leitura de arquivos, validação de dados e provider de dados usados pelos testes.
- **tests/**: Estrutura de testes organizada em `unit`, `integration`, `e2e` com conftest específicos por nível.

## Como usar

### Ambiente Python (venv)

Instruções para criar um ambiente virtual Python usando `venv` (Linux) e instalar dependências:

```bash
# criar o ambiente
python3 -m venv .venv

# ativar
source .venv/bin/activate

# instalar dependências do projeto
pip install -r requirements.txt

# desativar e remover o ambiente (quando não precisar mais)
deactivate
rm -rf .venv
```

### Windows (PowerShell)

```powershell
# criar o ambiente
python -m venv .venv

# ativar (PowerShell)
.\.venv\Scripts\Activate.ps1

# instalar dependências
pip install -r requirements.txt

# desativar e remover o ambiente (quando necessário)
deactivate
Remove-Item -Recurse -Force .venv
```

### Windows (cmd)

```cmd
:: criar o ambiente
python -m venv .venv

:: ativar (cmd)
.venv\Scripts\activate.bat

:: instalar dependências
pip install -r requirements.txt

:: desativar remover o ambiente
deactivate
rmdir /s /q .venv
```

### Executar todos os testes

```bash
pytest -q
```
### Executar uma pasta específica (ex.: e2e produtos):

```bash
pytest tests/e2e/products -q
```

## Configuração de ambientes
 As variáveis e arquivos de configuração estão em `environments/` (dev, staging, prod). Ajuste conforme necessário antes de rodar testes E2E.

## Markers disponíveis (pytest)
- **smoke**: Testes rápidos para validar fluxo principal.
- **regress**: Testes de regressão completos.
- **e2e**: Testes ponta-a-ponta que podem depender de ambiente externo.
- **integration**: Testes de integração entre componentes.
- **unit**: Testes unitários.

Exemplos de uso de markers:

```bash
# rodar apenas testes de smoke
pytest -m smoke

# rodar smoke e e2e (ou com -m "smoke or e2e")
pytest -m "smoke or e2e"

# rodar regress exceto os testes marcados como slow
pytest -m regress -k "not slow"
```

## Helpers de teste e utilitários
- **Fábricas e fixtures:** Em `shared/factories` e `shared/fixtures` há helpers para criar objetos de teste e fixtures reutilizáveis.
- **Validação de dados:** `src/utils/data_validator.py` provê validações comuns usadas antes de assertivas.
- **Data provider:** `src/utils/data_provider.py` lê `data/` e alimenta testes parametrizados.
- **Leitura de arquivos:** `src/utils/file_reader.py` abstrai leitura de JSON/CSV para testes.
- **Uso em testes (exemplo):**

```python
def test_cria_usuario(api_client, user_factory):
    user = user_factory.build()
    resp = api_client.create_user(user)
    assert resp.status_code == 201
```

## Estrutura do projeto
- **tests/**: `unit`, `integration`, `e2e` com `conftest.py` locais e globais em `conftest.py` na raiz.
- **data/**: Dados de teste e fixtures estáticas (`products.json`, `users.csv`, `users.json`).
- **docs/** e **doc/**: Documentação de arquitetura, guias e resultados de otimização/performance.

```
framework-automacao/
├── src/
|   ├── config/            # Centralização de informações
|   |   └── settings.py        # Classe que disponibiliza as configurações
│   ├── infrastructure/    # Camada de infraestrutura
│   ├── services/          # Camada de serviços
│   └── utils/             # Utilitários gerais
├── tests/               # Camada de testes
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── environments/        # Variáveis de ambiente para diferentes modos
│   ├── dev/
│   ├── staging/
│   └── prod/
├── data/                # Dados para testes
│   ├── test_data/
│   └── fixtures/
├── logs/                # Arquivos de log (gitignore)
├── docs/                # Documentação
│   ├── architecture/
│   └── guides/
├── .pylintrc           # Configuração do linter
├── .env.example        # Exemplo de variáveis de ambiente
├── requirements.txt    # Dependências do projeto
└── README.md          # Documentação principal
```

## Execução local — dicas rápidas
- Rodar com maior verbosidade: `pytest -q -k <nome_do_teste> -s`.
- Gerar relatório JUnit: `pytest --junitxml=reports/results.xml`.
- Paralelizar testes (se plugin instalado): `pytest -n auto`.



# Contribuindo
- Abra uma issue descrevendo a mudança ou bug.
- Crie um branch com nome claro `feature/<descricao>` ou `fix/<descricao>`.
- Garanta que novos testes adicionados rodem localmente.

## Contato
- Para dúvidas sobre o framework, consulte os guias em `docs/guides` ou abra uma issue.


# Membros
- Ilmara Guimarães Soares
- Lara Matos Aguirres
- Miquéias Ferreira dos Santos
- Murillo De Morais
- Vítor Pereira Nascimento
- Willian Marques de Faria
