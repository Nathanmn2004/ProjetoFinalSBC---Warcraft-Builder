# Esquema do Knowledge Graph

## Labels

| Label | Significado |
|---|---|
| `Character` | NPC ou personagem relevante |
| `Faction` | facção política/militar |
| `Quest` | missão jogável |
| `Item` | item obtido/usado |
| `Region` | zona, cidade ou sub-região |
| `Dungeon` | local instanciado ou demonstrativo |
| `Event` | acontecimento narrativo |
| `Requirement` | requisito explícito, como nível |

Todos os nós possuem `id`, `name`, `description`, `source`, `source_url`, `last_updated` e `game_version`. Nós provenientes da Blizzard API incluem, quando disponíveis, `api_id`, `namespace`, `locale`, `retrieved_at` e `source_type: blizzard_api`.

## Relações

`MEMBER_OF`, `GIVES_QUEST`, `REWARDS`, `REQUIRES`, `REQUIRED_FOR`, `LOCATED_IN`, `OBJECTIVE_IN`, `REQUIRES_LEVEL`, `INVOLVES`, `ALLIED_WITH` e `PART_OF`.

Convenção: `(missaoPosterior)-[:REQUIRES]->(missaoAnterior)`.

Relações curadas que a API não expõe devem registrar proveniência no dataset de curadoria e não podem ser apresentadas como dados vindos diretamente da API.

`LOCATED_IN` indica a região de início da missão; `OBJECTIVE_IN` indica uma região que o jogador precisa visitar para concluí-la.
