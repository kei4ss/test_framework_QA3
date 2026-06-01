# Refatoracao de Testes - Atividade 3

Data: 31 de maio de 2026

## Resumo

A suite de testes foi reorganizada para melhorar legibilidade, manutencao, isolamento e execucao seletiva por categorias.

## Mudancas implementadas

- Centralizacao de fixtures em `tests/conftest.py`, incluindo reset dos singletons entre testes.
- Configuracao de pytest em `pyproject.toml`, com discovery, markers e opcoes padrao.
- Inclusao de markers `unit`, `integration` e `e2e`.
- Reorganizacao dos testes em classes por responsabilidade.
- Padronizacao gradual de nomes no formato `test_should_*_when_*`.
- Atualizacao de dependencias de desenvolvimento em `requirements.txt`.

## Revisao aplicada

Durante a revisao, foi identificado que `tests/unit/logger_test.py` nao era coletado pela configuracao inicial `python_files = "test_*.py"`. A configuracao foi ajustada para incluir tambem `*_test.py`, mantendo os testes do Logger dentro da suite padrao.

## Como validar

```bash
python -m pytest tests -q
python -m pytest tests -m unit -q
python -m pytest tests -m integration -q
python -m pytest tests -m e2e -q
```

## Proximos passos recomendados

- Substituir chamadas reais HTTP por mocks com `responses` em testes de integracao que precisem ser deterministas.
- Adicionar execucao de cobertura com `pytest-cov`.
- Considerar CI para rodar unitarios e integracao separadamente.
