MATCH (n)-[:LOCATED_IN|PART_OF*1..3]->(r:Region)
WHERE toLower(n.name) CONTAINS toLower($name)
RETURN n.name AS entity, collect(DISTINCT r.name) AS regions,
       collect(DISTINCT r.source_url) AS sources;

