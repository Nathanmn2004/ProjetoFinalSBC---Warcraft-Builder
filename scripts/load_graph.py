import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.graph.client import GraphClient


DATA = ROOT / "data" / "normalized" / "graph.json"
SAFE_NAME = re.compile(r"^[A-Z][A-Z_]*$", re.IGNORECASE)


def main() -> None:
    if not DATA.exists():
        raise SystemExit("Run python scripts/normalize_data.py first")
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    client = GraphClient(Settings.from_env())
    try:
        client.query("MATCH (n) DETACH DELETE n")
        for node in payload["nodes"]:
            label = node["label"]
            if not SAFE_NAME.fullmatch(label):
                raise ValueError(f"Invalid label: {label}")
            properties = {key: value for key, value in node.items() if key != "label"}
            client.query(f"CREATE (n:{label}) SET n = $properties", properties=properties)
        for rel in payload["relationships"]:
            rel_type = rel["type"]
            if not SAFE_NAME.fullmatch(rel_type):
                raise ValueError(f"Invalid relationship type: {rel_type}")
            client.query(
                f"MATCH (a {{id: $from_id}}), (b {{id: $to_id}}) CREATE (a)-[:{rel_type}]->(b)",
                from_id=rel["from"],
                to_id=rel["to"],
            )
        print(f"Loaded {len(payload['nodes'])} nodes and {len(payload['relationships'])} relationships")
    finally:
        client.close()


if __name__ == "__main__":
    main()

