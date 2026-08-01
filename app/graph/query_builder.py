from dataclasses import dataclass
from enum import Enum
import re
import unicodedata


class Intent(str, Enum):
    QUEST_GIVER = "quest_giver"
    QUEST_CHAIN = "quest_chain"
    NEXT_QUEST = "next_quest"
    ITEM_SOURCE = "item_source"
    LOCATION = "location"
    NEIGHBORHOOD = "neighborhood"


@dataclass(frozen=True)
class ParsedQuestion:
    intent: Intent
    entity_hint: str


def _plain(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def parse_question(question: str) -> ParsedQuestion:
    plain = _plain(question)
    quoted = re.findall(r'["“”\']([^"“”\']+)["“”\']', question)
    entity = quoted[-1].strip() if quoted else question.strip(" ?")

    if "quem entrega" in plain or "quem da" in plain:
        intent = Intent.QUEST_GIVER
    elif "sequencia" in plain or "antes de" in plain or "preciso completar" in plain:
        intent = Intent.QUEST_CHAIN
    elif "depois" in plain or "proxima missao" in plain:
        intent = Intent.NEXT_QUEST
    elif "como consigo" in plain or "obter o item" in plain:
        intent = Intent.ITEM_SOURCE
    elif "onde" in plain or "regiao" in plain or "localiz" in plain:
        intent = Intent.LOCATION
    else:
        intent = Intent.NEIGHBORHOOD
    return ParsedQuestion(intent=intent, entity_hint=entity)


READ_ONLY_QUERIES: dict[Intent, str] = {
    Intent.QUEST_GIVER: """
        MATCH (c:Character)-[:GIVES_QUEST]->(q:Quest)
        WHERE toLower(q.name) CONTAINS toLower($name)
        OPTIONAL MATCH (c)-[:LOCATED_IN]->(r:Region)
        RETURN c.name AS giver, q.name AS quest, r.name AS location,
               [c.source_url, q.source_url] AS sources
    """,
    Intent.QUEST_CHAIN: """
        MATCH path=(target:Quest)-[:REQUIRES*0..8]->(pre:Quest)
        WHERE toLower(target.name) CONTAINS toLower($name)
        WITH path ORDER BY length(path) DESC LIMIT 1
        RETURN reverse([n IN nodes(path) | n.name]) AS ordered_chain,
               [n IN nodes(path) | n.source_url] AS sources
    """,
    Intent.NEXT_QUEST: """
        MATCH (next:Quest)-[:REQUIRES]->(current:Quest)
        WHERE toLower(current.name) CONTAINS toLower($name)
        OPTIONAL MATCH (next)-[:LOCATED_IN]->(r:Region)
        RETURN current.name AS current, next.name AS next, r.name AS location,
               [current.source_url, next.source_url] AS sources
    """,
    Intent.ITEM_SOURCE: """
        MATCH (q:Quest)-[:REWARDS]->(i:Item)
        WHERE toLower(i.name) CONTAINS toLower($name)
        OPTIONAL MATCH (q)-[:REQUIRES*0..8]->(pre:Quest)
        RETURN i.name AS item, q.name AS quest,
               collect(DISTINCT pre.name) AS prerequisites,
               [i.source_url, q.source_url] AS sources
    """,
    Intent.LOCATION: """
        MATCH (n)-[:LOCATED_IN|PART_OF*1..3]->(r:Region)
        WHERE toLower(n.name) CONTAINS toLower($name)
        RETURN n.name AS entity, collect(DISTINCT r.name) AS regions,
               collect(DISTINCT r.source_url) + collect(DISTINCT n.source_url) AS sources
    """,
    Intent.NEIGHBORHOOD: """
        MATCH (n)-[rel]-(other)
        WHERE toLower(n.name) CONTAINS toLower($name)
        RETURN n.name AS entity, type(rel) AS relation, other.name AS related,
               [n.source_url, other.source_url] AS sources
        LIMIT 20
    """,
}


def query_for(parsed: ParsedQuestion) -> str:
    return READ_ONLY_QUERIES[parsed.intent]


def assert_read_only(cypher: str) -> None:
    forbidden = {"CREATE", "DELETE", "DETACH", "DROP", "MERGE", "REMOVE", "SET", "CALL"}
    tokens = set(re.findall(r"[A-Z_]+", re.sub(r"//.*", "", cypher.upper())))
    found = forbidden & tokens
    if found:
        raise ValueError(f"Unsafe Cypher operation: {', '.join(sorted(found))}")

