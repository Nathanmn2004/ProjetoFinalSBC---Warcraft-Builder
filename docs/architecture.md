# Arquitetura

O sistema usa a Blizzard World of Warcraft Classic Game Data API como fonte primária de ingestão, selecionada por uma lista explícita de recursos. O sincronizador obtém snapshots JSON autenticados por OAuth e registra namespace, locale e momento da coleta. O Memgraph materializa fatos e relacionamentos e é a única fonte de contexto para respostas.

```text
API Classic -> snapshots auditáveis -> normalização/curadoria -> Memgraph -> GraphRAG -> Gemini/fallback
```

1. O parser identifica intenção e indício de entidade.
2. O resolvedor compara o texto com nomes no grafo.
3. Uma consulta Cypher parametrizada e somente leitura recupera fatos e caminhos.
4. O Gemini recebe apenas a pergunta e os fatos recuperados.
5. A resposta apresenta fundamentação e URLs preservadas no grafo.

A API não é chamada durante perguntas. Relações que a API não expõe, especialmente cadeias de missões, são curadas explicitamente e preservam fonte e versão. Essa separação impede que a LLM altere o banco ou complete fatos ausentes. O GraphRAG expande `REQUIRES`, `LOCATED_IN`, `REWARDS` e a vizinhança genérica.
