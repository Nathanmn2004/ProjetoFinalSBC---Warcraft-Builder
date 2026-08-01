import json

from scripts import normalize_data


def test_api_snapshot_enriches_only_explicitly_mapped_node(tmp_path, monkeypatch):
    snapshot_dir = tmp_path / "api_snapshots"
    snapshot_dir.mkdir()
    (snapshot_dir / "item.json").write_text(json.dumps({"id": 42}), encoding="utf-8")
    (snapshot_dir / "manifest.json").write_text(
        json.dumps(
            {
                "resources": [
                    {
                        "node_id": "item-1",
                        "file": "item.json",
                        "region": "us",
                        "path": "/data/wow/item/42",
                        "namespace": "static-classic1x-us",
                        "locale": "en_US",
                        "retrieved_at": "2026-08-01T00:00:00+00:00",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(normalize_data, "SNAPSHOT_DIR", snapshot_dir)
    nodes = [{"id": "item-1", "source": "old"}, {"id": "other", "source": "old"}]

    normalize_data.enrich_with_api_snapshots(nodes)

    assert nodes[0]["api_id"] == 42
    assert nodes[0]["source_type"] == "blizzard_api"
    assert nodes[0]["source_url"] == "https://us.api.blizzard.com/data/wow/item/42"
    assert nodes[1] == {"id": "other", "source": "old"}
