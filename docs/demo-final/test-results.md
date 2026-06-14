# Resultados dos Testes Funcionais

## Escopo dos testes funcionais

A medicao funcional atual considera a execucao conjunta das suites:

- `tests/unit`
- `tests/integration`
- `tests/e2e`

O objetivo desta execucao foi consolidar o estado funcional atual do framework para a demo final da Issue #32.

## Comando utilizado

```powershell
New-Item -ItemType Directory -Force -Path "C:\Temp" | Out-Null
$base = "C:\Temp\pytest-sqe3-lab7-functional-<guid>"
python -m pytest tests/unit tests/integration tests/e2e -v --basetemp $base
```

## Resultado atual consolidado

| Indicador | Resultado |
| --- | --- |
| Total de testes | `135` |
| Passed | `135` |
| Failed | `0` |
| Errors | `0` |
| Taxa de sucesso | `100%` |
| Taxa de falha | `0%` |
| Tempo de execucao | `11.55s` |

## Leitura do resultado atual

- A suite funcional atual esta estavel no ambiente local analisado.
- Nao houve falhas funcionais nem erros de setup/teardown nesta medicao.
- O total atual de `135` testes mostra ampliacao de cobertura funcional em relacao a medicoes historicas anteriores.

## Tendencia historica com os dados disponiveis

| Momento / referencia | Resultado | Tempo |
| --- | --- | --- |
| Entrega anterior documentada | `99 passed` | `12.12s` |
| Medicao historica sequencial com 135 testes | `135 passed` | `17.15s` |
| Medicao funcional atual | `135 passed` | `11.55s` |

## Interpretacao da tendencia

- O framework evoluiu de `99` para `135` testes documentados.
- Mesmo com aumento no volume total de casos, a execucao funcional atual permaneceu controlada.
- O tempo atual de `11.55s` e melhor que a medicao historica sequencial de `17.15s`.

## Relatorios em `reports/`

- O projeto possui `103` PDFs em `reports/`.
- Esses arquivos funcionam como evidencias historicas de execucao.
- A pasta `reports/` esta no `.gitignore`, portanto os artefatos nao fazem parte do versionamento do repositorio.

## Observacao sobre `--basetemp` fora do OneDrive

Foi mantido o uso de `--basetemp` em `C:\Temp` para evitar problemas ja observados quando diretorios temporarios eram criados dentro de pasta sincronizada pelo OneDrive.

Essa medida reduz o risco de erros de permissao e melhora a previsibilidade da execucao local.
