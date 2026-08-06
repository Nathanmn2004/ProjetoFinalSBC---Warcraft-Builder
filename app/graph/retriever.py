from difflib import SequenceMatcher

from app.graph.client import GraphClient
from app.graph.query_builder import ParsedQuestion, assert_read_only, query_for


class GraphRetriever:
    def __init__(self, client: GraphClient):
        self.client = client

    def _resolve_name(self, hint: str) -> str:
        quoted_or_tail = hint.strip()
        candidates = self.client.query(
            "MATCH (n) RETURN n.name AS name ORDER BY n.name LIMIT 500"
        )
        names = [row["name"] for row in candidates if row.get("name")]
        contained = [name for name in names if name.lower() in quoted_or_tail.lower()]
        if contained:
            return max(contained, key=len)
        scored = sorted(
            names,
            key=lambda name: SequenceMatcher(None, name.lower(), quoted_or_tail.lower()).ratio(),
            reverse=True,
        )
        return scored[0] if scored else quoted_or_tail

    def retrieve(self, parsed: ParsedQuestion) -> tuple[str, list[dict]]:
        cypher = query_for(parsed)
        assert_read_only(cypher)
        resolved = self._resolve_name(parsed.entity_hint)
        data = self.client.query(cypher, name=resolved)

        if parsed.intent.name == "QUEST_CHAIN":
            for row in data:
                if "ordered_chain" in row:
                    row["ordered_chain"] = list(reversed(row["ordered_chain"]))

        return resolved, data