# Gargalos e Riscos

## Objetivo

Este documento resume os principais gargalos e riscos observados durante a evolucao recente do framework, com foco em execucao funcional, performance, ambiente e geracao de evidencias para a demo final da Issue #32.

## Gargalos identificados

- Dependencia de servico externo para parte relevante da suite de integracao e E2E.
- Sensibilidade de artefatos compartilhados durante execucao paralela.
- Necessidade de controle explicito do diretorio temporario fora do OneDrive.
- Risco preventivo associado a componentes com estado global.

## Riscos de ambiente

### OneDrive e diretorios temporarios

Ja houve risco documentado de permissao quando arquivos temporarios eram criados em area sincronizada pelo OneDrive.

### Mitigacao adotada

- usar `--basetemp` em `C:\Temp`;
- evitar criacao de temporarios dentro do workspace sincronizado;
- manter o comando documentado para reproducao local.

## Riscos de dependencia externa

### JSONPlaceholder

Os testes de integracao e E2E usam `JSONPlaceholder` como dependencia externa real.

Isso introduz risco de:

- indisponibilidade de rede;
- latencia externa;
- bloqueio por ambiente restrito;
- variacao de comportamento fora do controle do repositorio.

### Gargalo de JSONPlaceholder

Mesmo quando a suite passa integralmente, a dependencia externa continua sendo um gargalo estrutural porque parte do tempo de execucao e parte da previsibilidade da suite dependem de um servico fora do projeto.

## Riscos de relatorios e artefatos

### Geração de multiplos PDFs em `reports/`

Durante execucao paralela com `pytest-xdist`, foram observados multiplos PDFs gerados quase no mesmo instante em `reports/`.

Isso indica risco de concorrencia na geracao de evidencias, especialmente quando mais de uma sessao ou worker aciona o fluxo de relatorio.

### Impacto

- aumento de ruido na pasta `reports/`;
- dificuldade de identificar qual PDF representa a execucao principal;
- risco de duplicacao de artefatos em cenarios paralelos.

## Riscos de paralelismo

- escrita concorrente em artefatos compartilhados;
- comportamento global de `Logger`;
- comportamento global de `RequestManager`;
- comportamento global de `DataProvider`;
- dependencia de logs compartilhados;
- necessidade de isolamento de dados e temporarios por execucao.

## Singletons globais como risco preventivo

O framework usa componentes que mantem estado global ou padrao singleton. Isso nao impediu a execucao atual com `-n 4`, mas permanece como risco preventivo para futuras expansoes da suite, principalmente se houver aumento de escrita em logs, relatorios ou recursos compartilhados.

## Recomendacoes de mitigacao

- manter `--basetemp` fora do OneDrive;
- continuar usando `-n 4` como ponto inicial operacional, sem aumentar concorrencia sem nova medicao;
- documentar claramente qual relatorio representa a execucao principal;
- reduzir escrita compartilhada em artefatos quando possivel;
- manter a separacao entre testes offline e testes dependentes de servico externo;
- tratar `JSONPlaceholder` como dependencia de risco conhecida na documentacao da demo.
