MATCH (n)
WHERE toLower(n.name) CONTAINS toLower($name)
RETURN labels(n)[0] AS label, properties(n) AS entity
ORDER BY n.name
LIMIT 10;

