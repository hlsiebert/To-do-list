# Identificação de Riscos do Projeto

## Objetivo

Registrar os principais riscos do projeto como um todo, considerando desenvolvimento, operação, manutenção e entrega do MVP da API de tarefas.

## Riscos Identificados

1. Dependência de serviços externos de IA
   - Descrição: O projeto pode depender de um serviço externo para sugerir prioridades, o que introduz risco de indisponibilidade, latência, limites de uso e falhas de autenticação.
   - Contexto de ocorrência: Esse risco ocorre quando o sistema tenta consultar o modelo externo durante a criação ou atualização de tarefas, especialmente em ambientes sem rede estável ou com credenciais inválidas.

2. Persistência inconsistente de dados
   - Descrição: Problemas na camada de persistência podem causar perda, duplicação ou leitura incorreta de tarefas.
   - Contexto de ocorrência: Esse risco ocorre durante operações de CRUD, reinícios da aplicação, manipulação concorrente de dados ou falhas no SQLite.

3. Validação insuficiente de entradas
   - Descrição: Dados incompletos ou fora do formato esperado podem gerar erros de execução, comportamento inesperado ou registros inválidos.
   - Contexto de ocorrência: Esse risco ocorre nas rotas de criação e atualização de tarefas, principalmente quando o cliente envia campos obrigatórios ausentes, valores fora do domínio ou payloads malformados.

4. Problemas de performance em leitura e escrita
   - Descrição: Operações podem ficar lentas conforme o volume de dados cresce ou quando a aplicação executa consultas pouco eficientes.
   - Contexto de ocorrência: Esse risco ocorre em listas de tarefas maiores, em ambientes com muitos acessos simultâneos ou quando o banco local passa a ser um gargalo.

5. Falta de observabilidade
   - Descrição: Sem logs e sinais de monitoramento adequados, falhas podem demorar mais para ser detectadas e diagnosticadas.
   - Contexto de ocorrência: Esse risco ocorre em produção e homologação, principalmente quando a API apresenta erro, timeout ou comportamento inesperado sem evidências suficientes para análise.

6. Escopo crescendo além do MVP
   - Descrição: Incluir funcionalidades extras sem priorização pode atrasar a entrega e aumentar a complexidade do projeto.
   - Contexto de ocorrência: Esse risco ocorre quando surgem pedidos de autenticação, dashboard, filtros avançados, paginação ou integrações adicionais antes da estabilização do MVP.

## Observação

A lista deve ser revisada periodicamente conforme o projeto evoluir, para incluir novos riscos e ajustar os existentes com base em incidentes reais, mudanças de escopo e resultados de testes.
