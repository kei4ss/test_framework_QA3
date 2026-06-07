# Execução paralela de testes automatizados

## 1. Objetivo

Esta atividade avaliou a capacidade do framework de executar testes em paralelo, identificar riscos de concorrência e comparar a performance da suíte em modo sequencial e paralelo.

## 2. Ferramenta utilizada

Foi utilizado o `pytest-xdist`, plugin oficial e amplamente adotado no ecossistema `pytest` para distribuição de testes entre múltiplos workers. Ele foi escolhido por permitir validar paralelismo real com baixo impacto no framework atual, usando a mesma suíte e a mesma interface de execução já adotada no projeto.

## 3. Configuração realizada

- `pytest-xdist` foi adicionado ao [requirements.txt](/C:/Users/Ilmara/OneDrive/Área%20de%20Trabalho/SQE3/test_framework_QA3/requirements.txt:1).
- Instalação realizada com:

```powershell
python -m pip install -r requirements.txt
```

- Comandos utilizados para validação paralela:

```powershell
python -m pytest tests/unit tests/integration tests/e2e -v -n 2 --basetemp C:\Temp\pytest-sqe3-parallel-n2-<guid>
python -m pytest tests/unit tests/integration tests/e2e -v -n 4 --basetemp C:\Temp\pytest-sqe3-parallel-n4-<guid>
python -m pytest tests/unit tests/integration tests/e2e -v -n auto --basetemp C:\Temp\pytest-sqe3-parallel-auto-<guid>
```

- Em todas as execuções foi usado `--basetemp` em `C:\Temp` para evitar problemas de permissão observados anteriormente quando diretórios temporários eram criados dentro do OneDrive.

## 4. Comparativo de performance

| Modo | Workers | Resultado | Tempo pytest | Tempo Measure-Command | Observação |
| --- | --- | --- | --- | --- | --- |
| Sequencial | 1 | 135 passed | 17.15s | 16.32s | Baseline após instalar `pytest-xdist` |
| Paralelo | 2 | 135 passed | 11.16s | 14.48s | Ganho de performance com baixo risco |
| Paralelo | 4 | 135 passed | 8.74s | 10.60s | Melhor resultado entre as execuções controladas |
| Paralelo | auto (12 workers) | 135 passed | 19.52s | 10.96s | Sem falhas, mas com pior tempo interno do pytest |

## 5. Problemas encontrados

- Nenhuma falha funcional confirmada em execução paralela.
- Nenhum teste falhou com `-n 2`, `-n 4` ou `-n auto`.
- Os principais riscos identificados nesta etapa são preventivos:
  - `Logger` com comportamento singleton/global;
  - `RequestManager` com comportamento singleton/global;
  - `ReportManager` gerando PDF em `reports/`;
  - possibilidade de logs compartilhados;
  - dependência externa do JSONPlaceholder;
  - necessidade de `basetemp` fora do OneDrive.

Esses pontos não se manifestaram como bugs reproduzíveis nas execuções realizadas, mas continuam sendo áreas sensíveis para evolução futura da suíte.

## 6. Testes refatorados para thread-safety

- Nenhum teste precisou ser refatorado nesta etapa, pois a suíte passou em execução paralela.
- Os riscos identificados foram documentados como recomendações preventivas.

## 7. Recomendações de isolamento de dados

- Usar `tmp_path` e `tmp_path_factory` para arquivos temporários e artefatos por teste.
- Evitar escrita fixa em logs compartilhados.
- Evitar dependência de ordem entre testes.
- Criar dados únicos por teste sempre que houver escrita externa ou geração de artefatos.
- Evitar estado global em singletons.
- Usar `--basetemp` fora de pastas sincronizadas como OneDrive.
- Separar testes offline e online com `markers`.

## 8. Guia de boas práticas para novos testes

- Escrever testes independentes e autocontidos.
- Usar nomes claros e específicos.
- Estruturar o teste em Arrange, Act, Assert.
- Não depender da ordem de execução.
- Não compartilhar arquivo fixo entre testes.
- Evitar APIs externas em testes críticos.
- Usar mocks quando possível.
- Usar `markers` para classificar `unit`, `integration` e `e2e`.
- Validar execução com `-n 2` antes de subir mudanças grandes que aumentem a concorrência da suíte.

## 9. Número recomendado de workers

Com base nos resultados medidos, `-n 4` é o valor inicial mais seguro e recomendado para este projeto.

Justificativa:

- foi significativamente melhor que `-n 2`;
- passou sem falhas;
- foi mais previsível que `-n auto`;
- `-n auto` não trouxe benefício proporcional no tempo interno do pytest, provavelmente por overhead de coordenação e pelo tamanho atual da suíte.

Para CI, `-n 4` tende a ser uma escolha mais estável e reprodutível do que `-n auto`, especialmente enquanto a suíte ainda depende de recursos externos e componentes com estado global.

## 10. Conclusão

A suíte executou em paralelo com sucesso, com ganho real de performance e sem falhas reproduzíveis nas execuções com `-n 2`, `-n 4` e `-n auto`. Os principais riscos de concorrência foram identificados e documentados como medidas preventivas para evolução futura do framework, sem necessidade de refatoração imediata nesta etapa.
