# Fontes e política de curadoria

## Fonte primária

A [Blizzard World of Warcraft Classic Game Data API](https://community.developer.battle.net/documentation/world-of-warcraft-classic/game-data-apis) é a fonte primária de dados estruturados. As respostas brutas são mantidas em `data/api_snapshots/` e o manifesto registra endpoint, namespace, locale e instante de coleta.

O projeto usa **Classic Era**, identificado por `static-classic1x-us`. Não é permitido usar dados de outro namespace na mesma cadeia sem declarar a versão.

## Curadoria complementar

Quando a API não fornecer relações necessárias — por exemplo, giver, turn-in ou pré-requisito de uma missão — a equipe registra o fato como curado, com URL específica, versão e data de verificação. Wowhead Classic e Warcraft Wiki podem complementar essa curadoria. Descrições devem ser parafraseadas; não copiar texto extenso.

## Política

Todo nó registra fonte, URL e data. Dados da API devem registrar `api_id`, namespace, locale, instante de coleta e `source_type: blizzard_api` quando aplicável. Relações curadas precisam ser distinguíveis de dados oficiais. O seed de 01/08 é infraestrutura de transição e deve ser auditado antes da apresentação.
