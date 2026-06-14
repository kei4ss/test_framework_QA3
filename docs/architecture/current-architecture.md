# Arquitetura Atual do Framework

Este documento consolida a arquitetura atual do framework para a demo final da Issue #32.

Os arquivos `.drawio` e `.png` existentes em `docs/architecture/` continuam como historico visual do projeto. Este arquivo em Markdown com Mermaid representa a visao consolidada mais atual do framework, considerando `schema validation`, `report manager` e execucao paralela com `pytest-xdist`.

## 1. Diagrama geral da arquitetura

```mermaid
flowchart LR
    subgraph Testes
        U[tests/unit]
        I[tests/integration]
        E[tests/e2e]
        C[conftest.py]
    end

    subgraph Execucao
        PX[pytest-xdist]
    end

    subgraph Framework
        RM[RequestManager]
        LG[Logger]
        DP[DataProvider]
        SL[SchemaLoader]
        SV[SchemaValidator]
        RPM[ReportManager]
        RP[ResultParser]
        PDF[PDFBuilder]
    end

    subgraph Artefatos
        RPTS[reports/]
    end

    EXT[JSONPlaceholder]

    PX --> U
    PX --> I
    PX --> E
    C --> RPM
    C --> RP

    U --> DP
    U --> RM
    U --> LG
    U --> SL
    U --> SV

    I --> RM
    I --> DP
    I --> LG
    I --> SL
    I --> SV

    E --> RM
    E --> DP
    E --> LG

    RM --> EXT
    RM --> LG
    SL --> SV
    RP --> RPM
    RPM --> PDF
    PDF --> RPTS
```

## 2. Diagrama de fluxo de execucao

```mermaid
flowchart TD
    A[pytest inicia a execucao] --> B[conftest.py registra fixtures e hooks]
    B --> C[testes unit, integration e e2e executam]
    C --> D[componentes do framework sao chamados]
    D --> E[RequestManager executa requisicoes]
    E --> F[JSONPlaceholder responde quando aplicavel]
    F --> G[SchemaValidator valida a resposta quando aplicavel]
    E --> H[Logger registra a execucao]
    B --> I[ReportManager consolida evidencias]
    I --> J[ResultParser organiza os resultados]
    I --> K[PDFBuilder gera o PDF]
    K --> L[PDF salvo em reports/]
```

## 3. Diagrama de modulos e componentes

```mermaid
flowchart TB
    subgraph SRC[src/]
        CFG[src/config]
        INF[src/infrastructure]
        UTL[src/utils]
    end

    subgraph TESTS[tests/]
        TUNIT[tests/unit]
        TINT[tests/integration]
        TE2E[tests/e2e]
        TSH[tests/shared/fixtures]
    end

    REP[reports/]
    DOCS[docs/]

    TUNIT --> INF
    TUNIT --> UTL
    TINT --> INF
    TINT --> UTL
    TE2E --> INF
    TE2E --> UTL
    TSH --> TINT
    TSH --> TE2E
    CFG --> INF
    INF --> REP
    DOCS --> CFG
    DOCS --> INF
    DOCS --> UTL
```

## 4. Observacoes arquiteturais relevantes

- `tests/unit`, `tests/integration` e `tests/e2e` representam a organizacao funcional atual da suite.
- `conftest.py` participa do fluxo de coleta e geracao de relatorios.
- `RequestManager`, `Logger` e `DataProvider` continuam como componentes centrais de apoio aos testes.
- `SchemaLoader` e `SchemaValidator` representam a camada de validacao de contrato adicionada recentemente.
- `ReportManager`, `ResultParser` e `PDFBuilder` representam a cadeia de geracao de evidencias em PDF.
- `JSONPlaceholder` permanece como dependencia externa usada por parte da suite.
- `pytest-xdist` representa a estrategia atual de execucao paralela recomendada para o projeto.
