# Instruções para agentes Codex

Leia este arquivo e o `README.md` antes de editar. Preserve mudanças de outros integrantes, execute `git status` antes e não altere o `.env` local.

## Objetivo e requisitos

O projeto é um sistema especialista acadêmico sobre uma fatia pequena e verificável de **World of Warcraft Classic Era**, centrada em Elwynn Forest. A entrega deve manter um Knowledge Graph real, Memgraph, Cypher, GraphRAG, perguntas em linguagem natural, respostas fundamentadas, fontes, scripts reprodutíveis, README, artigo SBC e slides.

A entrega pelo GitHub Classroom é até **06/08/2026 às 23h59**; a apresentação é em **07/08/2026**. A equipe é formada por Miguel Lisboa, Nathan Nóbrega e Luís Henrique Carvalho. O artigo SBC e os slides devem ser entregues em PDF e o artigo deve respeitar o limite de seis páginas, incluindo referências.

Priorize um grafo pequeno, correto, rastreável e demonstrável. Não tente cobrir todo WoW nem introduza frontend complexo, autenticação de usuários, banco vetorial ou agentes autônomos antes de concluir o escopo mínimo.

## Arquitetura oficial

```text
Blizzard Classic Game Data API
        ↓ sincronização OAuth explícita
Snapshots JSON auditáveis
        ↓ normalização e curadoria de relações ausentes
Memgraph (Knowledge Graph)
        ↓ Cypher somente leitura + GraphRAG
Fatos, caminhos e fontes
        ↓
Gemini ou fallback determinístico
```

Decisões que não devem ser substituídas sem justificativa documentada:

- fonte primária: Blizzard World of Warcraft Classic Game Data API;
- versão selecionada: **World of Warcraft Classic Era**;
- namespace padrão: `static-classic1x-us`;
- banco de grafos: Memgraph;
- consultas: Cypher parametrizado;
- recuperação: busca por entidade, caminhos e expansão de vizinhança;
- LLM: Gemini, com fallback determinístico;
- a LLM não cria nem executa Cypher;
- a aplicação responde a partir do Memgraph, não da API ao vivo.

A API é uma fonte de ingestão, não um substituto do Knowledge Graph. Use `data/api_resources.json` para selecionar endpoints documentados e `scripts/sync_blizzard.py` para gerar snapshots. Não faça scraping, coleta massiva ou chamadas dinâmicas por pergunta.

## Cobertura e curadoria

A API Classic pode não expor todos os fatos necessários sobre cadeias de missões, NPCs que iniciam/encerram missões, recompensas e pré-requisitos. Nesses casos, mantenha um fato curado explicitamente identificado. Nunca apresente uma relação curada como se tivesse vindo da API.

Cada nó deve possuir `id`, `name`, `description`, `source`, `source_url`, `last_updated` e `game_version`. Nós derivados da API devem incluir quando aplicável `api_id`, `namespace`, `locale`, `retrieved_at` e `source_type: blizzard_api`. Relações curadas devem ter fonte específica, URL verificável e `source_type: curated_relationship` em seu registro de curadoria.

Use `LOCATED_IN` para a região de início de uma missão e `OBJECTIVE_IN` para o destino/objetivo quando eles forem diferentes. Não confunda localização do giver com destino da entrega.

Não misture Retail, Classic Era ou qualquer versão de progressão na mesma cadeia sem a versão explícita. O dataset atual é um seed curado de transição e deve ser auditado antes da entrega.

## Organização

```text
app/blizzard/             OAuth e cliente da Blizzard Classic API
data/api_resources.json   lista explícita de endpoints permitidos
data/api_snapshots/       respostas geradas pelo sincronizador e manifesto
data/raw/                 seed curado de relações ainda não expostas/validadas pela API
data/normalized/          grafo gerado, nunca editado manualmente
scripts/sync_blizzard.py sincroniza recursos oficiais selecionados
scripts/normalize_data.py valida e gera o grafo
scripts/load_graph.py     carrega o Memgraph de desenvolvimento
scripts/validate_graph.py valida a integridade no Memgraph
app/graph/                intenção, resolução e recuperação GraphRAG
app/llm/                  grounding, Gemini e fallback
```

## Fluxo obrigatório da resposta

1. Receber pergunta em linguagem natural.
2. Identificar intenção e indício de entidade.
3. Resolver a entidade contra o grafo.
4. Selecionar Cypher de catálogo e validar como somente leitura.
5. Consultar o Memgraph e recuperar fatos, caminhos e fontes.
6. Enviar ao Gemini apenas pergunta e contexto estruturado recuperado.
7. Mostrar resposta, fundamentação e fontes; declarar ausência quando não houver fatos.

O Gemini não pode inventar entidades, relações, fontes ou URLs, completar lacunas com conhecimento próprio, alterar o grafo ou receber credenciais.

## Credenciais e segurança

Use apenas variáveis locais:

```env
BLIZZARD_CLIENT_ID=
BLIZZARD_CLIENT_SECRET=
BLIZZARD_REGION=us
BLIZZARD_LOCALE=en_US
BLIZZARD_NAMESPACE=static-classic1x-us
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash
MEMGRAPH_HOST=localhost
MEMGRAPH_PORT=7687
MEMGRAPH_USER=
MEMGRAPH_PASSWORD=
```

Nunca registre, teste, imprima, versione ou copie credenciais. Caso um segredo apareça em conversa, issue, commit ou log, considere-o comprometido e recomende sua revogação.

Toda consulta originada pelo usuário deve passar por `assert_read_only` e rejeitar `CREATE`, `DELETE`, `DETACH`, `DROP`, `MERGE`, `REMOVE`, `SET` e `CALL`. Scripts administrativos podem escrever no grafo, mas não devem reutilizar o caminho de consulta da interface.

## Rotina obrigatória

Antes de editar: leia este arquivo, `README.md` e documentos relacionados; verifique `git status`; confirme que a alteração preserva Classic Era e a fonte do fato.

Depois de mudanças relevantes:

```powershell
python scripts/normalize_data.py
python -m compileall -q app scripts tests
python -m pytest -q
```

Com Docker disponível:

```powershell
docker compose up -d
python scripts/load_graph.py
python scripts/validate_graph.py
```

Também teste uma pergunta informativa, uma procedural, uma sobre item, uma sobre localização e uma entidade inexistente. Não declare uma tarefa concluída sem informar verificações executadas e limitações remanescentes.

## Critério de entrega

Antes do envio, realize uma clonagem limpa e execute sincronização (quando houver credenciais), normalização, carga, validação e perguntas de demonstração. O projeto só está pronto quando o grafo for reconstruível, as fontes e a versão dos fatos estiverem auditadas, a ausência de dados não causar alucinação e os PDFs de relatório e slides estiverem presentes.
