import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "wow_elwynn.json"
TARGET = ROOT / "data" / "normalized" / "graph.json"
SNAPSHOT_DIR = ROOT / "data" / "api_snapshots"
REQUIRED = {"label", "id", "name", "description", "source", "source_url", "last_updated"}


def enrich_with_api_snapshots(nodes: list[dict]) -> None:
    """Apply only explicitly mapped Blizzard snapshots to existing nodes."""
    manifest_file = SNAPSHOT_DIR / "manifest.json"
    if not manifest_file.exists():
        return
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    node_by_id = {node["id"]: node for node in nodes}
    for resource in manifest.get("resources", []):
        node_id = resource.get("node_id")
        filename = resource.get("file")
        if not node_id or not filename or node_id not in node_by_id:
            continue
        snapshot = (SNAPSHOT_DIR / filename).resolve()
        if SNAPSHOT_DIR.resolve() not in snapshot.parents or not snapshot.is_file():
            raise ValueError(f"Invalid API snapshot file in manifest: {filename}")
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
        api_id = payload.get("id")
        if not isinstance(api_id, int):
            raise ValueError(f"API snapshot for {node_id} does not contain an integer id")
        node = node_by_id[node_id]
        node.update(
            {
                "api_id": api_id,
                "source": "Blizzard World of Warcraft Classic Game Data API",
                "source_url": f"https://{resource['region']}.api.blizzard.com{resource['path']}",
                "namespace": resource["namespace"],
                "locale": resource["locale"],
                "retrieved_at": resource["retrieved_at"],
                "source_type": "blizzard_api",
            }
        )


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    game_version = payload.get("metadata", {}).get("game_version")
    if not isinstance(game_version, str) or not game_version:
        raise ValueError("Dataset metadata must declare game_version")
    nodes = payload["nodes"]
    enrich_with_api_snapshots(nodes)
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("Node ids must be unique")
    for node in nodes:
        # The seed predates API ingestion. Preserve that distinction in the
        # generated graph while ensuring every fact has an explicit version.
        node.setdefault("game_version", game_version)
        node.setdefault("source_type", "curated_seed")
        missing = REQUIRED - node.keys()
        if missing:
            raise ValueError(f"Node {node.get('id')} missing: {sorted(missing)}")
    valid_ids = set(ids)
    for rel in payload["relationships"]:
        if rel["from"] not in valid_ids or rel["to"] not in valid_ids:
            raise ValueError(f"Dangling relationship: {rel}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Normalized {len(nodes)} nodes and {len(payload['relationships'])} relationships -> {TARGET}")


if __name__ == "__main__":
    main()
