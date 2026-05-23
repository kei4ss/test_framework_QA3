# Data Provider - Documentação Completa

## Visão Geral

O **Data Provider** é um componente central do framework de automação de testes que fornece uma interface unificada e flexível para obter dados de múltiplas fontes (JSON, CSV, hardcoded).

## Objetivo

Desenvolver um sistema que permite aos testes obterem dados de entrada de forma simples e padronizada, sem precisar se preocupar com a origem ou formato dos dados.

## Arquitetura

### Padrões de Design Utilizados

1. **Singleton Pattern**: Garante apenas uma instância do DataProvider na aplicação
   - Implementado em `DataProvider` e `DataProviderConfig`
   - Evita múltiplas instâncias desnecessárias

2. **Strategy Pattern**: Permite escolher diferentes estratégias de obtenção de dados
   - Interface abstrata: `DataStrategy`
   - Implementações: `JSONDataStrategy`, `CSVDataStrategy`, `HardcodedDataStrategy`
   - Facilita extensão com novas estratégias

### Componentes Principais

```
data_provider.py
├── DataProvider (Singleton + Strategy Pattern)
├── DataStrategy (Interface abstrata)
├── JSONDataStrategy
├── CSVDataStrategy
└── HardcodedDataStrategy

file_reader.py
└── FileReader (Utilitário para leitura de arquivos)

data_validator.py
└── DataValidator (Validação de dados com regras customizáveis)

data_provider_config.py
└── DataProviderConfig (Configuração centralizada - Singleton)
```

## Como Usar

### Uso Básico

```python
from src.utils.data_provider import DataProvider
from src.config.data_provider_config import DataSourceType

# Obter instância (Singleton)
provider = DataProvider()

# Obter dados de usuários (usa fonte padrão)
users = provider.get_user_data()

# Obter dados de uma fonte específica
users_csv = provider.get_user_data(source=DataSourceType.CSV)

# Obter dados genéricos
products = provider.get_product_data()

# Obter dados com fallback automático
data = provider.get_data(identifier='qualquer_arquivo')
```

### Configuração

```python
from src.config.data_provider_config import DataProviderConfig, DataSourceType

config = DataProviderConfig()

# Definir fonte preferencial
config.set_default_source(DataSourceType.CSV)

# Ativar/desativar validação
config.validate_data = True

# Ativar/desativar fallback entre fontes
config.enable_fallback = True

# Definir caminho para arquivos
config.set_json_path('caminho/para/json')
config.set_csv_path('caminho/para/csv')
```

### Validação de Dados

```python
from src.utils.data_validator import DataValidator

validator = DataValidator()

# Adicionar regras de validação
validator.add_rule('email', [
    DataValidator.create_email_validator()
])

validator.add_rule('age', [
    DataValidator.create_range_validator(min_val=18, max_val=120)
])

validator.add_rule('role', [
    DataValidator.create_enum_validator(['user', 'admin', 'moderator'])
])

# Validar dados
data = {'email': 'test@example.com', 'age': 25, 'role': 'user'}
is_valid, errors = validator.validate(data)

if not is_valid:
    print(f"Erros: {errors}")
```

### Exemplo em Teste

```python
def test_criar_usuario():
    provider = DataProvider()
    
    # Obter dados de teste
    usuarios = provider.get_user_data()
    usuario_teste = usuarios[0]
    
    # Usar nos passos do teste
    response = api.criar_usuario(
        nome=usuario_teste['name'],
        email=usuario_teste['email'],
        senha=usuario_teste['password']
    )
    
    assert response.status_code == 201
```

## Estrutura de Dados

### Arquivo JSON (users.json)

```json
[
  {
    "id": 1,
    "name": "João Silva",
    "email": "joao.silva@example.com",
    "password": "senha123secure",
    "age": 28,
    "role": "admin",
    "active": true
  }
]
```

### Arquivo CSV (users.csv)

```
id,name,email,password,age,role,active
1,João Silva,joao.silva@example.com,senha123secure,28,admin,true
2,Maria Santos,maria.santos@example.com,senhaSegura456,32,user,true
```

## Funcionalidades Implementadas

### ✅ Múltiplas Fontes de Dados
- **JSON**: Arquivos JSON estruturados
- **CSV**: Arquivos CSV tabulares
- **Hardcoded**: Dados pré-definidos em código

### ✅ Interface Unificada
- Método único `get_data()` para todas as fontes
- Métodos específicos: `get_user_data()`, `get_product_data()`
- Abstração da origem dos dados

### ✅ Fallback Automático
- Se a fonte preferencial não tem dados, tenta automaticamente outras fontes
- Configurável via `config.enable_fallback`
- Garante que os testes não falhem por indisponibilidade de uma fonte

### ✅ Validação de Dados
- Validadores customizáveis
- Suporte a validações: email, intervalo, comprimento de string, tipo, enumeração
- Modo strict (falha em dados inválidos) e lenient (tenta recuperar)

### ✅ Configuração Centralizada
- Padrão Singleton
- Configurações por ambiente
- Paths customizáveis para diferentes fontes

### ✅ Listagem de Dados Disponíveis
- `list_available_data_files()` para ver quais dados estão disponíveis
- Suporta todas as estratégias

### ✅ Validação de Schema
- `validate_file_schema()` para verificar se os dados seguem um schema esperado
- Útil para garantir integridade de dados de teste

## Arquivo de Configuração

### .env

```
MODE=DEV
LOG_LEVEL=INFO
APP_NAME=Test Framework
APP_VERSION=1.0.0
TIMEZONE=UTC
DEFAULT_LANGUAGE=pt-BR
```

### data_provider_config.py

Configuração centralizada acessível globalmente via Singleton:

```python
config = DataProviderConfig()
print(config.default_source)  # DataSourceType.JSON
print(config.data_path)       # caminho/para/data/test_data
print(config.enable_fallback) # True
```

## Testes Implementados

Total de **45 testes unitários** cobrindo:

### FileReader (10 testes)
- Leitura de JSON e CSV
- Conversão de tipos
- Listagem de arquivos
- Tratamento de erros

### DataValidator (8 testes)
- Validação de email
- Validação de intervalos
- Validação de comprimento de string
- Validação de tipo
- Validação de enumeração

### DataProvider (13 testes)
- Padrão Singleton
- Obtenção de dados (JSON, CSV, Hardcoded)
- Fallback automático
- Listagem de arquivos
- Alteração de fonte padrão
- Validação de schema

### Estratégias (6 testes)
- JSONDataStrategy
- CSVDataStrategy
- HardcodedDataStrategy

### Configuração (4 testes)
- Padrão Singleton
- Valores padrão
- Configuração de fonte

### Integração (2 testes)
- Workflow completo com fallback
- Consistência entre fontes

**Resultado: ✅ 45/45 testes passando (100%)**

## Extensibilidade

### Adicionar Nova Estratégia

```python
class DatabaseDataStrategy(DataStrategy):
    def __init__(self, connection_string):
        self.conn_string = connection_string
    
    def get_data(self, identifier):
        # Implementação da lógica de acesso ao banco
        pass
    
    def is_available(self):
        # Verificar disponibilidade do banco
        pass

# Registrar a nova estratégia
provider = DataProvider()
provider.register_custom_strategy('database', DatabaseDataStrategy(conn_str))
```

### Adicionar Novo Validador

```python
def validate_cpf(value):
    # Implementação da validação de CPF
    return is_valid, error_message

validator.add_rule('cpf', [validate_cpf])
```

## Benefícios

1. **Separação de Preocupações**: Testes não precisam saber de onde vêm os dados
2. **Reutilização**: Mesmos dados em múltiplos testes
3. **Manutenibilidade**: Alterar dados em um arquivo, afeta todos os testes
4. **Flexibilidade**: Trocar fonte de dados sem alterar testes
5. **Escalabilidade**: Fácil adicionar novas fontes ou validadores
6. **Confiabilidade**: Validação automática garante qualidade dos dados

## Estrutura de Pastas

```
test_framework_QA3/
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_provider.py      ← Componente principal
│   │   ├── file_reader.py        ← Leitura de arquivos
│   │   └── data_validator.py     ← Validação
│   └── config/
│       ├── settings.py
│       └── data_provider_config.py ← Configuração
├── data/
│   └── test_data/
│       ├── users.json
│       ├── users.csv
│       └── products.json
└── tests/
    └── unit/
        └── test_data_provider.py  ← Testes
```

## Critérios de Aceitação - ✅ TODOS CUMPRIDOS

- ✅ Classe Data Provider implementada em `/src/utils/data_provider.py`
- ✅ Classes auxiliares (FileReader, DataValidator) implementadas
- ✅ Arquivos de exemplo (JSON, CSV) em `/data/test_data/`
- ✅ Configuração de data provider implementada
- ✅ Testes em `/tests/unit/test_data_provider.py` - **45 testes passando**
- ✅ Documentação completa com exemplos
- ✅ Padrão Strategy implementado
- ✅ Múltiplas fontes de dados funcionando
- ✅ Fallback automático implementado
- ✅ Validação de dados implementada

## Comandos Úteis

```bash
# Executar todos os testes
python -m pytest tests/unit/test_data_provider.py -v

# Executar testes de uma classe específica
python -m pytest tests/unit/test_data_provider.py::TestDataProvider -v

# Executar um teste específico
python -m pytest tests/unit/test_data_provider.py::TestDataProvider::test_singleton_instance -v

# Executar com cobertura
python -m pytest tests/unit/test_data_provider.py --cov=src.utils --cov-report=html

# Verificar qualidade do código
pylint src/utils/data_provider.py
```

## Considerações Futuras

1. **Cache de Dados**: Implementar cache para dados frequentemente acessados
2. **API REST**: Integrar com APIs externas como fonte de dados
3. **Banco de Dados**: Suporte a múltiplos bancos de dados (PostgreSQL, MongoDB)
4. **Geração de Dados**: Integração com bibliotecas de geração de dados (Faker)
5. **Criptografia**: Mascarar dados sensíveis (senhas, tokens)
6. **Relatórios**: Gerar relatórios de qualidade dos dados de teste

## Contato

Para dúvidas ou sugestões sobre o Data Provider, abra uma issue no repositório.
