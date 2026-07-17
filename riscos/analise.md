# Análise dos Riscos do Projeto

## Objetivo

Aprofundar os riscos identificados no projeto, destacando o impacto esperado em caso de ocorrência e os fatores que aumentam ou reduzem a probabilidade de cada risco se concretizar.

## Análise dos Riscos

1. Dependência de serviços externos de IA
   - Impacto: Alto. Pode afetar funcionalidades de sugestão de prioridade, causar atraso em respostas da API e exigir fallback para manter o sistema operando.
   - Fatores condicionantes: Qualidade da conexão com a internet, validade da chave de acesso, limites de uso do provedor, tempo de resposta do serviço externo e existência de estratégia de fallback local.

2. Persistência inconsistente de dados
   - Impacto: Alto. Pode resultar em perda de informações, dados duplicados, leituras incorretas e comprometimento da confiança no sistema.
   - Fatores condicionantes: Confiabilidade do SQLite, tratamento de exceções, atomicidade das operações, concorrência de acesso e testes de persistência.

3. Validação insuficiente de entradas
   - Impacto: Alto. Pode gerar erros em tempo de execução, rejeição de requisições válidas, gravação de dados incorretos ou exposição de comportamentos inesperados.
   - Fatores condicionantes: Regras de validação nas rotas, uso correto dos modelos Pydantic, cobertura de testes de borda, qualidade dos payloads recebidos e tratamento de erros.

4. Problemas de performance em leitura e escrita
   - Impacto: Médio. Pode causar lentidão perceptível, degradar a experiência do usuário e limitar o crescimento da base de dados.
   - Fatores condicionantes: Volume de tarefas armazenadas, número de requisições simultâneas, eficiência das consultas, capacidade do ambiente de execução e uso de indexação adequada.

5. Falta de observabilidade
   - Impacto: Médio a alto. Dificulta diagnóstico de falhas, aumenta o tempo de resposta a incidentes e pode ocultar degradação silenciosa do sistema.
   - Fatores condicionantes: Presença de logs estruturados, nível de detalhamento dos erros, monitoramento de métricas, rastreabilidade das requisições e estratégia de alertas.

6. Escopo crescendo além do MVP
   - Impacto: Alto. Pode atrasar entregas, aumentar o número de dependências técnicas e desviar foco dos objetivos principais do projeto.
   - Fatores condicionantes: Entrada frequente de novos pedidos, ausência de priorização formal, disponibilidade da equipe, pressão por novas funcionalidades e disciplina de gestão de escopo.

## Conclusão

Os riscos de maior impacto estão relacionados à integração com serviços externos, configuração de ambiente, persistência e validação de dados. Para reduzir o efeito desses riscos, o projeto deve manter documentação atualizada, testes automatizados, tratamento de erros consistente e estratégia de fallback quando houver dependência externa.
