# Fluxo de Geração de Relatórios — ReportManager

> Módulo: `src/infrastructure/reportManager/`  
> Relatórios salvos em: `./reports/`  
> Padrão de nome: `HH-mm-ss-DD-MM-YYYY.pdf`

---

## 1. Visão Geral

O **ReportManager** é um módulo de infraestrutura que automatiza a geração de relatórios PDF ao final de cada execução da suíte de testes. Ele não exige dependências externas além do **reportlab** (geração de PDF); toda a coleta de dados é feita por hooks nativos do pytest via `conftest.py`.

```
pytest executa os testes
        │
        ▼
conftest.py (hooks nativos)
   ├─ pytest_sessionstart   → inicializa _SessionCollector
   ├─ pytest_runtest_logreport → acumula resultado de cada teste
   └─ pytest_sessionfinish  → monta ParsedResults e chama ReportManager
                                        │
                                        ▼
                              ReportManager.generate()
                                        │
                          ┌─────────────┴─────────────┐
                          │                           │
                    ResultParser                  PDFBuilder
               (estrutura os dados)         (gera o arquivo PDF)
                          │                           │
                          └─────────────┬─────────────┘
                                        ▼
                             ./reports/HH-mm-ss-DD-MM-YYYY.pdf
```

---

## 2. Componentes do Módulo

### 2.1 `conftest.py` (raiz do projeto)

Arquivo de plugin pytest que **não requer configuração manual**. Ao rodar `pytest`, ele é carregado automaticamente e registra três hooks:

| Hook | Momento | Responsabilidade |
|---|---|---|
| `pytest_sessionstart` | Início da sessão | Inicializa o `_SessionCollector` e registra o horário de início |
| `pytest_runtest_logreport` | Após cada fase de cada teste | Classifica o resultado (passed/failed/error) por categoria |
| `pytest_sessionfinish` | Após todos os testes | Constrói o `ParsedResults` e invoca o `ReportManager` |

**Categorização por caminho:**

```
tests/unit/...          → categoria "unit"
tests/integration/...   → categoria "integration"
tests/e2e/...           → categoria "e2e"
```

Testes fora dessas pastas são ignorados silenciosamente.

---

### 2.2 `result_parser.py` — `ResultParser`

Responsável por interpretar os resultados dos testes e devolver um objeto `ParsedResults` estruturado. Suporta três modos de entrada:

| Método | Fonte | Quando usar |
|---|---|---|
| `parse_json(path)` | Arquivo `.json` gerado por `pytest-json-report` | Integração com CI/CD |
| `parse_dict(data)` | Dicionário Python já carregado | Uso programático / testes unitários do próprio módulo |
| `parse_text(path)` | Saída textual do pytest salva em arquivo | Fallback sem plugins |

**Estruturas de dados:**

```python
@dataclass
class TestCategoryResult:
    category: str       # "unit" | "integration" | "e2e"
    total: int          # total de testes executados
    passed: int         # aprovados
    failed: int         # falhos (asserção)
    errors: int         # erros (setup/teardown)
    duration: float     # duração em segundos
    failed_tests: list  # lista de node_ids com falha

    @property
    def failure_rate(self) -> float: ...  # percentual de falhas

@dataclass
class ParsedResults:
    unit: TestCategoryResult
    integration: TestCategoryResult
    e2e: TestCategoryResult
    total_duration: float
```

---

### 2.3 `pdf_builder.py` — `PDFBuilder`

Constrói o PDF usando **reportlab**. Recebe um `ParsedResults` e escreve o arquivo no caminho especificado.

**Estrutura do PDF gerado:**

```
┌──────────────────────────────────────────┐
│  Relatório de Execução de Testes          │
│  Data: DD-MM-YYYY  HH:MM:SS               │
├──────────────────────────────────────────┤
│  RESUMO GERAL (tabela)                   │
│  Total | Aprovados | Falhas | Taxa | Dur  │
├──────────────────────────────────────────┤
│  UNIT TESTS                              │
│  ┌─ Total de testes: N                   │
│  ├─ Testes aprovados: N  (verde)         │
│  ├─ Testes falhos: N     (vermelho/verde)│
│  ├─ Taxa de falha: X.XX% (vermelho/verde)│
│  └─ Duração: X.XXXs                     │
│  • lista de testes falhos (se houver)    │
├──────────────────────────────────────────┤
│  INTEGRATION TESTS  (idem)               │
├──────────────────────────────────────────┤
│  E2E TESTS  (idem)                       │
├──────────────────────────────────────────┤
│  Rodapé: gerado automaticamente          │
└──────────────────────────────────────────┘
```

---

### 2.4 `report_manager.py` — `ReportManager`

Orquestrador que une os dois componentes anteriores.

**Fluxo interno do `generate()`:**

```
generate(results_path | results_dict | parsed_results)
    │
    ├─ Se parsed_results → usa diretamente
    ├─ Se results_dict   → ResultParser.parse_dict()
    └─ Se results_path   → ResultParser.parse_json() ou parse_text()
                                    │
                            _build_output_path()
                            ├─ Cria ./reports/ se não existir
                            ├─ Nome: HH-mm-ss-DD-MM-YYYY.pdf
                            └─ Se existir → HH-mm-ss-DD-MM-YYYY_1.pdf (sem sobrescrever)
                                    │
                            PDFBuilder.build(results, output_path)
                                    │
                            retorna Path do arquivo criado
```

---

## 3. Fluxo Completo de Execução

```
$ pytest

Fase 1 — pytest_sessionstart
  └─ _SessionCollector() criado, start_time = agora

Fase 2 — Para cada teste:
  pytest_runtest_logreport(report)
    ├─ report.when == "call"  → classifica como unit/integration/e2e
    │    ├─ passed → bucket.passed += 1
    │    ├─ failed → bucket.failed += 1; adiciona node_id em failed_tests
    │    └─ duration acumulada
    └─ report.when == "setup" e failed → bucket.errors += 1

Fase 3 — pytest_sessionfinish
  ├─ _collector.build_results() → ParsedResults completo
  ├─ total == 0? → aborta (não gera PDF vazio)
  └─ ReportManager().generate(parsed_results=results)
       ├─ _build_output_path() → ./reports/14-32-10-28-05-2026.pdf
       └─ PDFBuilder.build()   → arquivo salvo

[ReportManager] Relatório PDF gerado: reports/14-32-10-28-05-2026.pdf
```

---

## 4. Convenção de Nome de Arquivo

```
HH-mm-ss-DD-MM-YYYY.pdf

Exemplo: 14-32-10-28-05-2026.pdf
         ↑  ↑  ↑  ↑  ↑    ↑
         │  │  │  │  │    Ano (4 dígitos)
         │  │  │  │  Mês
         │  │  │  Dia
         │  │  Segundos
         │  Minutos
         Horas
```

Caso um arquivo com o mesmo nome já exista (execuções dentro do mesmo segundo), o sistema adiciona um sufixo numérico incremental: `14-32-10-28-05-2026_1.pdf`, `14-32-10-28-05-2026_2.pdf`, etc.

---

## 5. Dependências

| Dependência | Uso | Instalação |
|---|---|---|
| `reportlab` | Geração do PDF | `pip install reportlab` |
| `pytest` | Hooks de coleta | Já presente no projeto |

Adicione `reportlab` ao `requirements.txt`:

```
reportlab
```

---

## 6. Estrutura de Arquivos Criados

```
test_framework_QA3/
├── conftest.py                                     ← NOVO: plugin pytest
├── reports/                                        ← NOVO: relatórios gerados
│   └── 14-32-10-28-05-2026.pdf
├── requirements.txt                                ← ATUALIZADO: + reportlab
└── src/
    └── infrastructure/
        └── reportManager/                          ← NOVO: módulo completo
            ├── __init__.py
            ├── report_manager.py
            ├── result_parser.py
            └── pdf_builder.py
```

---

## 7. Uso Alternativo via CLI

O `ReportManager` pode ser invocado diretamente pela linha de comando caso você tenha um arquivo de resultados JSON (por exemplo, gerado por `pytest-json-report`):

```bash
# Gerar relatório a partir de um JSON do pytest-json-report
pytest --json-report --json-report-file=.report.json
python -m src.infrastructure.reportManager.report_manager --results .report.json

# Especificar diretório de saída customizado
python -m src.infrastructure.reportManager.report_manager \
    --results .report.json \
    --reports-dir custom_reports/
```

---

## 8. Uso Programático

```python
from src.infrastructure.reportManager import ReportManager

# A partir de um arquivo JSON
rm = ReportManager()
pdf_path = rm.generate(results_path=".report.json")
print(f"Relatório salvo em: {pdf_path}")

# A partir de um ParsedResults já construído
from src.infrastructure.reportManager.result_parser import ParsedResults, TestCategoryResult

results = ParsedResults(
    unit=TestCategoryResult(category="unit", total=120, passed=118, failed=2),
    integration=TestCategoryResult(category="integration", total=45, passed=42, failed=3),
    e2e=TestCategoryResult(category="e2e", total=12, passed=12, failed=0),
    total_duration=42.7,
)
rm = ReportManager()
pdf_path = rm.generate(parsed_results=results)
```

---

## 9. Critérios de Aceitação — Verificação

| Critério | Como é atendido |
|---|---|
| PDF gerado automaticamente após execução | `conftest.py` via `pytest_sessionfinish` |
| Salvo em `./reports` | `ReportManager._reports_dir` (padrão: `<raiz>/reports/`) |
| Nome segue padrão `HH-mm-ss-DD-MM-YYYY.pdf` | `_build_output_path()` com `datetime.now().strftime(...)` |
| Separa unit / integration / e2e | `_resolve_category()` + `_SessionCollector._buckets` |
| Exibe total de testes | `TestCategoryResult.total` |
| Exibe testes aprovados | `TestCategoryResult.passed` |
| Exibe testes falhos | `TestCategoryResult.failed + errors` |
| Exibe porcentagem de falhas | `TestCategoryResult.failure_rate` |
| Não sobrescreve relatórios anteriores | Loop de sufixo `_N` em `_build_output_path()` |
