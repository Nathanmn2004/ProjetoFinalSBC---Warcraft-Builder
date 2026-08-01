MATCH (q:Quest)-[:REWARDS]->(i:Item)
WHERE toLower(i.name) CONTAINS toLower($name)
OPTIONAL MATCH path=(q)-[:REQUIRES*0..8]->(pre:Quest)
RETURN i.name AS item, q.name AS quest,
       collect(DISTINCT pre.name) AS prerequisites,
       collect(DISTINCT q.source_url) + collect(DISTINCT i.source_url) AS sources;

