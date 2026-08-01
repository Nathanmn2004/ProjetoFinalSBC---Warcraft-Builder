# Dados

`api_resources.json` declara os endpoints oficiais que podem ser sincronizados. `api_snapshots/` recebe as respostas e o manifesto gerados por `scripts/sync_blizzard.py`; não editar os snapshots manualmente.

`raw/wow_elwynn.json` é o seed curado de transição para relações de campanha que ainda não foram confirmadas ou não são expostas pela API Classic. `normalized/graph.json` é gerado por `scripts/normalize_data.py` e nunca deve ser editado manualmente.

O projeto usa Classic Era. Todo fato deve declarar `game_version`, fonte, URL e data; relações curadas precisam permanecer distinguíveis de dados oficiais.
