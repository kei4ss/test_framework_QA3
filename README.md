# Framework de teste - Grupo C
Framework de automação de testes baseado em Python.

## Membros
- Ilmara Guimarães Soares
- Lara Matos Aguirres
- Miquéias Ferreira dos Santos
- Murillo De Morais
- Vítor Pereira Nascimento
- Willian Marques de Faria

## Documentos dos laboratórios
- [laboratório 4](https://docs.google.com/document/d/1LbDQE0a9hktl_DU-SuNVzb0S0F5qiViM5qUwGicH0mU/edit?usp=sharing)  [<- Estamos atualmente aqui]

# Diagramas
## Estrutura de pastas
```
framework-automacao/
├── src/
│   ├── infrastructure/    # Camada de infraestrutura
│   ├── services/         # Camada de serviços
│   └── utils/           # Utilitários gerais
├── tests/               # Camada de testes
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/              # Arquivos de configuração
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


## Diagrama de componentes
<img width="582" height="868" alt="diagram" src="https://github.com/user-attachments/assets/2b6ac4ca-eb43-4f1d-8337-ac5c4917965d" />

