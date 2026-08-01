"""Download reproducible snapshots from Blizzard Classic Game Data API.

The resource list is deliberately explicit: no scraping, guessing endpoints or
bulk harvesting. Add only documented resources to data/api_resources.json.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.blizzard.client import BlizzardClassicClient
from app.config import Settings


RESOURCE_FILE = ROOT / "data" / "api_resources.json"
SNAPSHOT_DIR = ROOT / "data" / "api_snapshots"


def main() -> None:
    resources = json.loads(RESOURCE_FILE.read_text(encoding="utf-8")).get("resources", [])
    if not isinstance(resources, list):
        raise ValueError("data/api_resources.json deve conter uma lista resources.")
    if not resources:
        print("Nenhum recurso configurado em data/api_resources.json; nada para sincronizar.")
        return

    settings = Settings.from_env()
    client = BlizzardClassicClient.from_settings(settings)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str]] = []
    try:
        for resource in resources:
            if not isinstance(resource, dict) or not isinstance(resource.get("path"), str):
                raise ValueError("Cada recurso deve possuir um campo path textual.")
            path = resource["path"]
            payload = client.get_json(path, namespace=resource.get("namespace"))
            filename = resource.get("filename") or path.strip("/").replace("/", "_")
            target = SNAPSHOT_DIR / f"{filename}.json"
            target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            manifest.append(
                {
                    "path": path,
                    "file": target.name,
                    "node_id": resource.get("node_id", ""),
                    "region": settings.blizzard_region,
                    "namespace": resource.get("namespace") or settings.blizzard_namespace,
                    "locale": settings.blizzard_locale,
                    "retrieved_at": datetime.now(UTC).isoformat(),
                }
            )
            print(f"Sincronizado {path} -> {target.relative_to(ROOT)}")
    finally:
        client.close()
    (SNAPSHOT_DIR / "manifest.json").write_text(
        json.dumps({"resources": manifest}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
