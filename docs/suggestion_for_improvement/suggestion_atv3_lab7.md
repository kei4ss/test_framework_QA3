# Proposta de Estratégia para Testes de Desempenho — Framework Sentinela

## 1. Análise da Situação Atual (Pytest vs. Postman)

Para tomar uma decisão arquitetural fundamentada, avaliou-se o comportamento das ferramentas já utilizadas pela equipe frente aos requisitos de testes de performance:

### 1.1 Postman (Postman Newman / Postman CLI)

**Funcionalidades de Performance:** O Postman possui uma interface nativa para testes de performance locais (com usuários virtuais concorrentes), mas a execução em larga escala e automação via CLI (Newman) possui severas limitações de concorrência real e geração de carga volumétrica distribuída.

**Vantagens:** Reaproveitamento imediato das coleções de requisições de API (collections) e scripts de asserção já desenvolvidos pelo time no Lab 2.

**Desvantagens:** Alto consumo de memória por usuário virtual simulado, relatórios de latência limitados no modo CLI e dificuldade para simular rampas complexas de carga (ex: Spike Tests ou Stress Tests estáveis).

### 1.2 Pytest (Ecossistema Python)

**Funcionalidades de Performance:** O pytest nativo foi projetado para asserções funcionais sequenciais. O uso do plugin `pytest-xdist` (validado no projeto com `-n 4`) distribui testes para acelerar a execução, mas não funciona como um gerador de carga concorrente ou gerador de requisições por segundo (RPS).

**Vantagens:** Integração total com a infraestrutura atual do Sentinela (`RequestManager`, `Logger`, `Settings`, e a geração de relatórios em PDF do `ReportManager`).

**Desvantagens:** Tentar forçar o pytest a atuar como uma ferramenta de carga via loops ou threads gerará gargalos de I/O no próprio runner do teste, resultando em métricas falsas de tempo de resposta da API (overhead do cliente).


## 2. Solução Proposta: Abordagem Híbrida Direcionada

Forçar o pytest ou o Postman puro para testes de volume compromete a confiabilidade das métricas. Portanto, a solução ideal divide-se em **duas frentes estratégicas complementares**:

```
                      ┌─────────────────────────────┐
                      │ Estratégia de Performance   │
                      └──────────────┬──────────────┘
                                     │
            ┌────────────────────────┴────────────────────────┐
            ▼                                                 ▼
【 Front 1: Micro-benchmarks 】                  【 Front 2: Testes de Carga Real 】
  Ferramenta: Pytest + pytest-benchmark            Ferramenta: Locust (Extensão da Infra)
  Foco: Latência isolada e regressão               Foco: Concorrência, Vazão e Estresse
```

### Front 1: Micro-benchmarks e Asserção de SLA via pytest

Utilizar o ecossistema Python do framework para validar o tempo de resposta sob condições normais de uso (Performance não-funcional base).

**Como funcionaria:** Acoplar o plugin `pytest-benchmark` ou criar asserções explícitas de tempo decorrido (`elapsed`) dentro dos testes de integração já existentes baseados no `RequestManager`.

**Critério de Aceitação:** Garantir que requisições críticas não ultrapassem o limite definido em `Settings`:

```python
assert response.elapsed.total_seconds() < 2.0
```

### Front 2: Testes de Carga e Concorrência Real via Locust (Recomendado)

Para testes de Carga, Estresse e Pico, a melhor prática de engenharia de software é adotar uma ferramenta baseada em código (As-Code) nativa para isso. O **Locust** se encaixa perfeitamente no Sentinela porque:

- **É 100% Python:** Permite reaproveitar as classes de configuração do `Settings` e utilitários do framework.
- **Alta Escalabilidade:** Utiliza arquitetura baseada em eventos (`gevent`), permitindo simular milhares de usuários simultâneos em uma única máquina local ou pipeline de CI.
- **Casos de Teste Legíveis:** Os cenários de carga são escritos como métodos decorados (ex: `@task`), mantendo a legibilidade técnica exigida na Jala University.


## 3. Planejamento da Implementação (Roadmap)

Respeitando as premissas arquiteturais do projeto, a futura expansão deve seguir estes passos estruturados:

### Passo 1: Definição de Métricas e SLAs

Antes do código, mapear os limites aceitáveis para as APIs de teste (como o ambiente simulado do JSONPlaceholder):

| Métrica | Valor Alvo |
|---|---|
| Tempo de Resposta Padrão (P95) | < 500 ms para requisições GET |
| Taxa de Erro Tolerável | No máximo 1% sob carga nominal |
| Vazão Alvo | Suportar X requisições por segundo (RPS) simuladas |

### Passo 2: Estruturação dos Arquivos

A criação de uma pasta dedicada na estrutura do projeto manterá a separação de responsabilidades (Clean Architecture):

```
framework-automacao/
├── tests/
│   ├── performance/             # Nova pasta dedicada
│   │   ├── locustfile.py        # Scripts de cenários de carga concorrente
│   │   └── test_performance.py  # Testes funcionais do pytest validando tempos de resposta (SLA)
```

### Passo 3: Integração com o Relatório Geral (ReportManager)

- Estender o `ResultParser` do Sentinela para ler o output gerado pelos testes de desempenho (seja em formato CSV/JSON do Locust ou do `pytest-benchmark`).
- Modificar o `PDFBuilder` para incluir uma seção visual de **"Performance & SLA Report"**, exibindo gráficos de tempo de resposta por endpoint e taxas de erro sob estresse.

