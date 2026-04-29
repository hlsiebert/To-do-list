# Escopo do Projeto

## Objetivo

Descrever o escopo do MVP para a micro-API de gestão de tarefas usada internamente pela equipe. O documento define claramente o propósito do serviço, os requisitos funcionais e não funcionais, e delimita funcionalidades fora do escopo inicial.

## Requisitos Funcionais

1. Registro de tarefas
   - Criar tarefas com título, descrição e prioridade.
   - Prioridade classificada em: `baixa`, `média`, `alta`, `crítica`.
   - Atribuir status básico: `pendente`, `em andamento`, `concluída`.

2. Consulta de tarefas
   - Listar tarefas existentes.
   - Filtrar por status e prioridade.

3. Atualização de tarefas
   - Atualizar campos de tarefa: título, descrição, prioridade e status.
   - Ajustar prioridade com base em sugestões de IA.

4. Remoção de tarefas
   - Excluir tarefas pelo identificador.

5. Resposta de saúde
   - Endpoint simples para verificar disponibilidade da API.

## Requisitos Não Funcionais

1. Performance
   - Tempo de resposta da API de leitura deve ser compatível com uso interno e pequenas bases de dados.

2. Confiabilidade
   - API deve retornar erros claros em casos de entrada inválida.

3. Manutenibilidade
   - Código organizado em estrutura modular, com rotas e modelos separados.

4. Segurança básica
   - Não expor informações sensíveis no payload de erro.

5. Documentação
   - Gerar documentação automática de API via OpenAPI/Swagger.

## Fora do Escopo

- Autenticação e autorização de usuários.
- Integração com serviços de notificação ou alertas.
- Dashboard visual ou front-end.
- Suporte a múltiplos usuários com permissões.
- Processos de priorização avançada por IA além do escopo MVP.
- Persistência distribuída ou banco de dados em cluster.
