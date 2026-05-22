# PyTFrame
Este projeto tem como objetivo a concepção, desenvolvimento e implementação de
uma estrutura (framework) de automação para testes de API. O objetivo é criar uma
ferramenta robusta, escalável e de fácil manutenção, capaz de validar não apenas as
respostas e os esquemas dos endpoints, mas também a lógica de negócios e a
integridade dos dados no sistema em teste. 

## Objetivos

- [ ] **Validar a lógica de negócios**: Abranger cenários positivos, negativos, de limite
(boundary) e fluxos de ponta a ponta (E2E).

- [ ] **Garantir a integridade dos dados**: Implementar validações de esquemas (JSON
Schema) e verificar a integridade dos dados ao realizar solicitações de
API.Generative
 
- [ ] **IA**: Utilizar a GenAI para criar conjuntos de dados complexos, otimizar a geração de
scripts de teste e otimizar a refatoração de código.
 
- [ ] **Reportar com clareza**: Gerar logs detalhados e relatórios visuais de execução que
permitam identificar falhas rapidamente.

- [ ] **Escalabilidade**: Suportar execução paralela, estratégias de "falha rápida" (fail-fast)
e testes de carga/desempenho. 

# Documentação
Aqui estão todos os documentos gerados para explicar a arquitetura do projeto, fluxos de execução, construção de classes, tecnologias usadas, design escolhidos e afims... 

Documentos e diagramas devem está presentes na pasta `docs`, na raíz do projeto.

## Diagramas

### Diagramas de arquitetura
- [Diagrama de componentes](./docs/architecture/component-diagram/diagram.png)
- [Diagrama de fluxo](./docs/architecture/Execution-Flow-Diagram/diagram.png)
- [Diagrama de arquitetura geral](./docs/architecture/General-Architecture-Diagram/diagram.png)

### Diagramas de classe
- [Classe Settings](./docs/architecture/class-diagram/Settings.md)

## Estrutura de pastas
```
framework-automacao/
├── src/
|   ├── config/            # Centralização de informações
|   |   └── settings.py        # Classe que disponibiliza as configurações
│   ├── infrastructure/    # Camada de infraestrutura
│   ├── services/          # Camada de serviços
│   └── utils/             # Utilitários gerais
├── tests/               # Camada de testes
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── environments/        # Variáveis de ambiente para diferentes modos
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


# Membros
- Ilmara Guimarães Soares
- Lara Matos Aguirres
- Miquéias Ferreira dos Santos
- Murillo De Morais
- Vítor Pereira Nascimento
- Willian Marques de Faria
