MATCH path=(target:Quest)-[:REQUIRES*0..8]->(prerequisite:Quest)
WHERE toLower(target.name) CONTAINS toLower($name)
RETURN [node IN nodes(path) | node.name] AS chain,
       [node IN nodes(path) | node.source_url] AS sources
ORDER BY size(chain) DESC
LIMIT 1;

