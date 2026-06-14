# Resultados de Performance

## Objetivo da medicao

Este documento consolida os resultados de performance da suite do framework `test_framework_QA3`, com foco na comparacao entre execucao sequencial e execucao paralela para a demo final da Issue #32.

## Cenarios testados

Foram considerados os seguintes cenarios:

- execucao sequencial atual;
- execucao paralela atual com `-n 4`;
- medicao historica sequencial com `135` testes;
- medicao historica paralela com `-n 2`;
- medicao historica paralela com `-n 4`;
- medicao historica paralela com `-n auto`.

## Comandos utilizados

### Sequencial atual

```powershell
New-Item -ItemType Directory -Force -Path "C:\Temp" | Out-Null
$base = "C:\Temp\pytest-sqe3-lab7-functional-<guid>"
python -m pytest tests/unit tests/integration tests/e2e -v --basetemp $base
```

### Paralelo atual com `-n 4`

```powershell
$base = "C:\Temp\pytest-sqe3-lab7-performance-n4-<guid>"
python -m pytest tests/unit tests/integration tests/e2e -v -n 4 --basetemp $base
```

## Tabela comparativa

| Cenario | Resultado | Tempo | Observacao |
| --- | --- | --- | --- |
| Sequencial atual | `135 passed` | `11.55s` | Baseline funcional atual |
| Paralelo atual `-n 4` | `135 passed` | `7.01s` | Melhor medicao atual para a demo |
| Historico sequencial | `135 passed` | `17.15s` | Baseline anterior documentado |
| Historico `-n 2` | `135 passed` | `11.16s` | Ganho com baixo risco |
| Historico `-n 4` | `135 passed` | `8.74s` | Melhor medicao historica controlada |
| Historico `-n auto` | `135 passed` | `19.52s` | Sem ganho proporcional |

## Resultado atual consolidado da execucao paralela

| Indicador | Resultado |
| --- | --- |
| Total de testes | `135` |
| Passed | `135` |
| Failed | `0` |
| Errors | `0` |
| Taxa de sucesso | `100%` |
| Tempo de execucao | `7.01s` |

## Grafico comparativo simples

| Modo | Tempo |
| --- | --- |
| Sequencial atual | `11.55s` |
| Paralelo atual `-n 4` | `7.01s` |
| Historico sequencial | `17.15s` |
| Historico `-n 2` | `11.16s` |
| Historico `-n 4` | `8.74s` |
| Historico `-n auto` | `19.52s` |

## Reducao observada na medicao atual

- Reducao aproximada atual em relacao ao sequencial atual: `39.3%`.
- A suite permaneceu com `135 passed`, `0 failed` e `0 errors` no cenario paralelo avaliado.

## Identificacao de gargalos

- `-n auto` nao apresentou beneficio proporcional e teve pior tempo interno do pytest na medicao historica.
- A suite ainda depende de componentes com estado global, o que exige cuidado ao aumentar concorrencia.
- A geracao de artefatos em `reports/` pode produzir multiplos PDFs durante execucao paralela.
- A dependencia de `JSONPlaceholder` continua sendo um fator externo de variacao.

## Conclusao

Com base nas medicoes disponiveis, `-n 4` e a recomendacao operacional inicial para execucao paralela desta suite.

Essa escolha combina:

- `135 passed`;
- `0 failed` e `0 errors`;
- taxa de sucesso de `100%`;
- tempo atual de `7.01s`;
- ganho perceptivel sobre a execucao sequencial atual;
- comportamento mais previsivel do que `-n auto`.
