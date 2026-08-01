from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.graph.client import GraphClient


CHECKS = {
    "nodes_without_required_properties": """
        MATCH (n) WHERE n.id IS NULL OR n.name IS NULL OR n.description IS NULL
          OR n.source IS NULL OR n.source_url IS NULL OR n.last_updated IS NULL
        RETURN count(n) AS count
    """,
    "duplicate_ids": """
        MATCH (n) WITH n.id AS id, count(*) AS amount WHERE amount > 1
        RETURN count(id) AS count
    """,
    "quests_without_location": """
        MATCH (q:Quest) WHERE NOT (q)-[:LOCATED_IN]->(:Region)
        RETURN count(q) AS count
    """,
}


def main() -> None:
    client = GraphClient(Settings.from_env())
    failures = []
    try:
        for name, query in CHECKS.items():
            count = client.query(query)[0]["count"]
            print(f"{name}: {count}")
            if count:
                failures.append(name)
        counts = client.query("MATCH (n) OPTIONAL MATCH ()-[r]->() RETURN count(DISTINCT n) AS nodes, count(DISTINCT r) AS relationships")[0]
        print(f"nodes: {counts['nodes']}; relationships: {counts['relationships']}")
    finally:
        client.close()
    if failures:
        raise SystemExit("Validation failed: " + ", ".join(failures))


if __name__ == "__main__":
    main()

