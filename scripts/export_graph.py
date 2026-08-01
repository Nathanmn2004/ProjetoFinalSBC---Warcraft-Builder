import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.graph.client import GraphClient


def main() -> None:
    client = GraphClient(Settings.from_env())
    try:
        nodes = client.query("MATCH (n) RETURN labels(n)[0] AS label, properties(n) AS properties")
        relationships = client.query("MATCH (a)-[r]->(b) RETURN a.id AS from_id, type(r) AS type, b.id AS to_id")
    finally:
        client.close()
    target = ROOT / "output" / "graph-export.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({"nodes": nodes, "relationships": relationships}, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()

