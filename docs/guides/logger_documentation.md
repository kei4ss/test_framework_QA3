# Sistema de Logging — Framework de Automação

## Visão Geral

O sistema de logging é um componente centralizado da camada de infraestrutura do framework.
Ele garante que todos os registros de execução, debug e auditoria de requisições
sigam um padrão único, facilitando leitura, triagem e manutenção dos logs.

---

## Arquitetura

```
src/
├── infraestructure/
│   └── logger.py           ← Classe Logger (Singleton)
└── config/
    └── logging_config.py   ← Constantes e configurações padrão

logs/                       ← Criado automaticamente (está no .gitignore)
    ├── sentinela.log       ← Todos os logs (DEBUG em diante)
    └── errors.log          ← Apenas WARNING, ERROR e CRITICAL
```

### Como os componentes se relacionam

```
              ┌─────────────────────────────┐
              │         Logger()            │  ← Singleton
              │  (src/infraestructure/      │
              │       logger.py)            │
              └──────────┬──────────────────┘
                         │ usa
              ┌──────────▼──────────────────┐
              │   SensitiveDataFormatter    │  ← Mascara dados antes de gravar
              └──────────┬──────────────────┘
                         │ alimenta
        ┌────────────────┼────────────────────┐
        ▼                ▼                    ▼
 StreamHandler    RotatingFileHandler   RotatingFileHandler
 (console)        (sentinela.log)       (errors.log)
                  todos os níveis       WARNING+
```

---

## Configuração

### Variáveis de Ambiente (`.env`)

Adicione as variáveis abaixo ao seu `.env` (ou ao `.env` do ambiente específico):

```env
LOG_LEVEL=INFO      # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_DIR=logs        # Caminho do diretório de logs (relativo à raiz)
```

**Prioridade de configuração:**

```
Parâmetro do construtor  >  settings().global_config()  >  Valor padrão do código
```

### Exemplo de `.env` por ambiente

| Ambiente | `LOG_LEVEL` recomendado | Motivo |
|----------|------------------------|--------|
| DEV      | `DEBUG`                | Ver todos os detalhes durante desenvolvimento |
| STAGING  | `INFO`                 | Acompanhar fluxo sem excesso de detalhes |
| PROD     | `WARNING`              | Registrar apenas o que precisa de atenção |

---

## Níveis de Severidade

| Nível      | Valor numérico | Quando usar |
|------------|---------------|-------------|
| `DEBUG`    | 10            | Valores de variáveis, payloads, diagnóstico fino |
| `INFO`     | 20            | Início/fim de testes, requisições bem-sucedidas |
| `WARNING`  | 30            | Timeout alto, dado próximo do limite, depreciação |
| `ERROR`    | 40            | Requisição falhou, assertion quebrou, operação impossível |
| `CRITICAL` | 50            | Sistema não consegue continuar, configuração ausente |

> Mensagens do nível configurado **e acima** são registradas.
> Ex.: com `LOG_LEVEL=WARNING`, apenas WARNING, ERROR e CRITICAL aparecem.

---

## Como Usar

### Instalação / Importação

```python
from src.infraestructure.logger import Logger
```

```python
# Logger lê LOG_LEVEL e LOG_DIR do .env automaticamente
log = Logger()
```

### Instanciação com configuração customizada

```python
# Útil para sobrescrever o .env em um contexto específico
log = Logger(log_level="DEBUG", log_dir="logs/debug_run")
```

> Como o Logger é um **Singleton**, apenas a **primeira** chamada aplica a configuração.
> Chamadas subsequentes retornam a mesma instância já configurada.

---

## Referência dos Métodos

### `log.debug(message, *args)`

```python
log.debug("Payload enviado: %s", payload)
log.debug("Variável x=%s, y=%s", x, y)
```

Use para diagnóstico fino: valores de variáveis, dados de requisição, estado interno.
Silenciado em produção (LOG_LEVEL=WARNING).

---

### `log.info(message, *args)`

```python
log.info("Teste iniciado: %s", nome_do_teste)
log.info("Usuário autenticado com sucesso")
```

Use para confirmar que o fluxo normal está acontecendo.

---

### `log.warning(message, *args)`

```python
log.warning("Tempo de resposta alto: %.2fs (limite: 2s)", tempo)
log.warning("Endpoint depreciado acessado: %s", url)
```

Algo inesperado, mas o sistema ainda funciona.
Gravado em `sentinela.log` **e** `errors.log`.

---

### `log.error(message, *args, **kwargs)`

```python
log.error("Requisição falhou: status %s", status_code)

# Para incluir stack trace automaticamente:
try:
    resultado = servico.buscar_usuario(user_id)
except Exception:
    log.error("Falha ao buscar usuário %s", user_id, exc_info=True)
```

Problema sério que impediu uma operação.
Gravado em `sentinela.log` **e** `errors.log`.

---

### `log.critical(message, *args)`

```python
log.critical("Arquivo de configuração não encontrado: %s", caminho)
log.critical("Ambiente de teste inacessível — abortando execução")
```

Erro grave; a execução pode não conseguir continuar.
Gravado em `sentinela.log` **e** `errors.log`.

---

### `log.log_request(method, url, status_code, response_time)`

Helper padronizado para auditoria de requisições HTTP.
O nível é escolhido automaticamente: **INFO** para 2xx/3xx, **ERROR** para 4xx/5xx.

```python
import time

inicio = time.time()
resposta = requests.get("https://api.exemplo.com/usuarios")
tempo = time.time() - inicio

log.log_request(
    method="GET",
    url="https://api.exemplo.com/usuarios",
    status_code=resposta.status_code,
    response_time=tempo
)
# Saída: HTTP GET https://api.exemplo.com/usuarios → 200 (0.342s)
```

---

## Exemplos por Cenário

### Cenário 1 — Teste de API com auditoria completa

```python
import time
import requests
from src.infraestructure.logger import Logger

log = Logger()

def test_buscar_lista_de_usuarios():
    log.info("=== INÍCIO: test_buscar_lista_de_usuarios ===")

    url = "https://jsonplaceholder.typicode.com/users"
    log.debug("Enviando GET para: %s", url)

    inicio = time.time()
    resposta = requests.get(url, timeout=10)
    tempo_resposta = time.time() - inicio

    log.log_request("GET", url, resposta.status_code, tempo_resposta)

    assert resposta.status_code == 200, f"Esperado 200, recebido {resposta.status_code}"
    assert len(resposta.json()) > 0, "Lista de usuários veio vazia"

    log.info("Usuários retornados: %d", len(resposta.json()))
    log.info("=== FIM: test_buscar_lista_de_usuarios ✓ ===")
```

**Saída no console/arquivo:**
```
[2024-05-22 14:30:00] [INFO    ] [test_usuarios:8]  === INÍCIO: test_buscar_lista_de_usuarios ===
[2024-05-22 14:30:00] [DEBUG   ] [test_usuarios:11] Enviando GET para: https://jsonplaceholder.typicode.com/users
[2024-05-22 14:30:00] [INFO    ] [test_usuarios:17] HTTP GET https://jsonplaceholder.typicode.com/users → 200 (0.342s)
[2024-05-22 14:30:00] [INFO    ] [test_usuarios:21] Usuários retornados: 10
[2024-05-22 14:30:00] [INFO    ] [test_usuarios:22] === FIM: test_buscar_lista_de_usuarios ✓ ===
```

---

### Cenário 2 — Tratamento de exceção com stack trace

```python
from src.infraestructure.logger import Logger(produto_id: int):
    log.debug("Buscando produto com ID: %d", produto_id)
    try:
        resposta = requests.get(f"/produtos/{produto_id}", timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.Timeout:
        log.error("Timeout ao buscar produto %d", produto_id)
        raise
    except requests.exceptions.HTTPError as ex:
        # exc_info=True inclui o stack trace completo no log
        log.error("Erro HTTP ao buscar produto %d: %s", produto_id, ex, exc_info=True)
        raise
```

---

### Cenário 3 — Mascaramento automático de dados sensíveis

```python
log = Logger()

# O Logger mascara automaticamente — você não precisa fazer nada especial
log.info("Autenticando usuário com password=minha_senha_123")
# → Gravado como: "Autenticando usuário com password=***MASKED***"

log.debug("Header de auth: authorization=Bearer eyJhbGc...")
# → Gravado como: "Header de auth: authorization=***MASKED***"
```

---

### Cenário 4 — Integração com um Serviço

```python
# src/services/usuario_service.py
from src.infraestructure.logger import Logger

class UsuarioService:
    def __init__(self):
        # Logger() retorna a mesma instância já configurada (Singleton)
        self.log = Logger()

    def criar_usuario(self, dados: dict) -> dict:
        self.log.info("Criando usuário: %s", dados.get("nome"))
        # ... lógica de criação ...
        self.log.info("Usuário criado com ID: %s", novo_id)
        return {"id": novo_id}
```

---

## Rotação de Arquivos

O Logger usa `RotatingFileHandler` para evitar que os arquivos de log
cresçam indefinidamente e ocupem todo o disco.

**Como funciona:**

```
Escrevendo logs...
    sentinela.log  (crescendo até 10 MB)
         ↓ atinge 10 MB
    sentinela.log  → renomeado para  sentinela.log.1
    sentinela.log  (novo arquivo vazio criado)
         ↓ atinge 10 MB novamente
    sentinela.log  → renomeado para  sentinela.log.1
    sentinela.log.1 → renomeado para sentinela.log.2
    ...
    sentinela.log.5 → DESCARTADO (limite de 5 backups)
```

**Configuração padrão:**

| Parâmetro       | Valor padrão | Localização para alterar |
|-----------------|-------------|--------------------------|
| Tamanho máximo  | 10 MB       | `logging_config.py` → `MAX_BYTES` |
| Backups mantidos| 5 arquivos  | `logging_config.py` → `BACKUP_COUNT` |

---

## Mascaramento de Dados Sensíveis

O `SensitiveDataFormatter` aplica expressões regulares em **toda mensagem**
antes de ela ser escrita, substituindo padrões sensíveis por marcadores.

**Padrões ativos por padrão:**

| O que detecta | Exemplo de entrada | Saída no log |
|--------------|-------------------|--------------|
| Senhas | `password=abc123` | `password=***MASKED***` |
| Tokens/API Keys | `token=eyJhbGc...` | `token=***MASKED***` |
| Cartões de crédito | `4111111111111111` | `***CARD***` |

**Como adicionar um novo padrão** (ex: CPF):

```python
# Em src/config/logging_config.py, adicione à lista SENSITIVE_PATTERNS:
(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '***CPF***'),
```

E em `logger.py`, importe e use a lista atualizada de `logging_config.py`.

---

## Executando os Testes

```bash
# Todos os testes do Logger
pytest tests/unit/logger_test.py -v

# Com output detalhado em caso de falha
pytest tests/unit/logger_test.py -v --tb=long

# Apenas um grupo de testes específico
pytest tests/unit/logger_test.py::TestMascaramentoDeSensitivos -v
pytest tests/unit/logger_test.py::TestRotacaoDeArquivos -v
```

---

## Checklist de Implementação

- [x] Classe `Logger` em `src/infraestructure/logger.py`
- [x] Padrão Singleton implementado
- [x] 5 níveis de severidade (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [x] Handler de console (StreamHandler)
- [x] Handler de arquivo geral com rotação (`sentinela.log`)
- [x] Handler de arquivo de erros com rotação (`errors.log`)
- [x] Formatação padronizada com timestamp, nível, módulo e linha
- [x] Mascaramento automático de dados sensíveis
- [x] Helper `log_request()` para auditoria de requisições HTTP
- [x] Arquivo de configuração `src/config/logging_config.py`
- [x] Testes unitários em `tests/unit/logger_test.py`
- [x] Documentação em `docs/guides/logging.md`