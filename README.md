# Azeroth's Oracle

Sistema especialista acadêmico sobre a progressão de Elwynn Forest em **World of Warcraft Classic Era**. A fonte primária planejada é a [Blizzard World of Warcraft Classic Game Data API](https://community.developer.battle.net/documentation/world-of-warcraft-classic/game-data-apis); os fatos são materializados no Memgraph e consultados por GraphRAG.

## Arquitetura

```text
Blizzard Classic Game Data API -> snapshots JSON -> normalização -> Memgraph
                                                              ↓
Pergunta -> intenção -> Cypher somente leitura -> fatos/caminhos -> Gemini ou fallback
```

A API é usada durante a sincronização, nunca pela LLM e nunca diretamente a cada pergunta. Isso preserva a reprodutibilidade e permite que a demonstração funcione quando a API estiver indisponível. O Memgraph continua sendo a fonte de conhecimento usada pelas respostas.

Algumas relações de campanha, como giver, turn-in e pré-requisitos de missões, podem não ser expostas pela API Classic. Elas permanecem em curadoria explícita, com fonte, URL, versão e data de verificação; não são inferidas pela LLM.

## Requisitos

- Python 3.11+
- Docker com Docker Compose
- credenciais OAuth Blizzard opcionais para sincronizar snapshots
- chave Gemini opcional; sem ela, a aplicação usa fallback determinístico

## Configuração

```powershell
Copy-Item .env.example .env
```

Para sincronizar a API, crie uma aplicação no portal Battle.net e preencha somente o arquivo `.env` local:

```env
BLIZZARD_CLIENT_ID=
BLIZZARD_CLIENT_SECRET=
BLIZZARD_REGION=us
BLIZZARD_LOCALE=en_US
BLIZZARD_NAMESPACE=static-classic1x-us
```

`static-classic1x-us` identifica **Classic Era**. Não troque o namespace sem documentar a versão do jogo e revisar o dataset. Segredos não devem ser versionados nem impressos.

## Execução

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Opcional: baixa os recursos declarados em data/api_resources.json.
python scripts/sync_blizzard.py

docker compose up -d
python scripts/normalize_data.py
python scripts/load_graph.py
python scripts/validate_graph.py
python -m app.main
```

`data/api_resources.json` declara os dez itens Classic Era usados pelo recorte, incluindo objetivos e recompensas de Kobold Candles, Cloth and Leather Armor, Report to Thomas e Shipment to Stormwind. Adicione apenas endpoints confirmados na documentação Classic e associados a fatos que serão auditados. Os arquivos obtidos são gravados em `data/api_snapshots/` com um manifesto de namespace, locale e data.

Para promover um snapshot a dado do grafo, associe-o explicitamente a um nó existente:

```json
{
  "path": "/data/wow/item/ID_CONFIRMADO",
  "node_id": "id-do-item-no-seed",
  "filename": "item_id_confirmado"
}
```

Na normalização, apenas recursos com `node_id` atualizam a proveniência do nó para `blizzard_api`; snapshots sem mapeamento permanecem somente como evidência auditável.

O seed curado em `data/raw/wow_elwynn.json` mantém a demonstração funcional enquanto a cobertura da API para cada relação é validada.

## Perguntas de demonstração

- Quem entrega a missão "Further Concerns"?
- Qual é a sequência de missões até "Report to Thomas"?
- Onde devo ir depois de completar "Find the Lost Guards"?
- Em qual região fica "Northshire Abbey"?
- Como consigo "Patched Pants"?
- Qual é a relação com uma entidade que não existe no grafo?

## Garantias de segurança e explicabilidade

- Gemini recebe somente pergunta e fatos recuperados pelo grafo.
- A aplicação seleciona consultas Cypher parametrizadas de um catálogo somente leitura.
- A rota de perguntas rejeita Cypher mutável.
- Respostas exibem fundamentação e URLs recuperadas.
- Quando não há fatos, o sistema declara falta de conhecimento.

## Testes

```powershell
python scripts/normalize_data.py
python -m compileall -q app scripts tests
python -m pytest -q
```

Os testes da API usam transporte simulado e não requerem credenciais. A validação de integração exige Memgraph em execução.

World of Warcraft e os nomes associados pertencem à Blizzard Entertainment. Este projeto é acadêmico e não afiliado à Blizzard.
