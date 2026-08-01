from contextlib import contextmanager

from neo4j import GraphDatabase

from app.config import Settings


class GraphClient:
    def __init__(self, settings: Settings):
        auth = None
        if settings.memgraph_user or settings.memgraph_password:
            auth = (settings.memgraph_user, settings.memgraph_password)
        self._driver = GraphDatabase.driver(
            f"bolt://{settings.memgraph_host}:{settings.memgraph_port}", auth=auth
        )

    def close(self) -> None:
        self._driver.close()

    @contextmanager
    def session(self):
        with self._driver.session() as session:
            yield session

    def query(self, cypher: str, **params) -> list[dict]:
        with self.session() as session:
            result = session.run(cypher, **params)
            return [record.data() for record in result]

