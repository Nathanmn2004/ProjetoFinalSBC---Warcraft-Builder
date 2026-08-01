from dataclasses import dataclass

from app.graph.query_builder import parse_question
from app.graph.retriever import GraphRetriever
from app.llm.response_generator import ResponseGenerator


@dataclass(frozen=True)
class Answer:
    text: str
    intent: str
    entity: str
    sources: tuple[str, ...]


class GraphRAG:
    def __init__(self, retriever: GraphRetriever, generator: ResponseGenerator):
        self.retriever = retriever
        self.generator = generator

    def answer(self, question: str) -> Answer:
        parsed = parse_question(question)
        entity, facts = self.retriever.retrieve(parsed)
        source_set: set[str] = set()
        for fact in facts:
            raw_sources = fact.get("sources") or []
            source_set.update(str(source) for source in raw_sources if source)
        text = self.generator.generate(question, entity, facts)
        return Answer(text, parsed.intent.value, entity, tuple(sorted(source_set)))

