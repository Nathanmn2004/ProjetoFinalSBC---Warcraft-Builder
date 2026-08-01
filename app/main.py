from app.config import Settings
from app.graph.client import GraphClient
from app.graph.retriever import GraphRetriever
from app.llm.response_generator import ResponseGenerator
from app.pipeline.graph_rag import GraphRAG


def main() -> None:
    settings = Settings.from_env()
    client = GraphClient(settings)
    oracle = GraphRAG(GraphRetriever(client), ResponseGenerator(settings))
    print("Azeroth's Oracle - digite 'sair' para encerrar.")
    try:
        while True:
            question = input("\nPergunta> ").strip()
            if question.lower() in {"sair", "exit", "quit"}:
                break
            if not question:
                continue
            answer = oracle.answer(question)
            print(f"\n{answer.text}")
            if answer.sources:
                print("\nFontes recuperadas:")
                for source in answer.sources:
                    print(f"- {source}")
    finally:
        client.close()


if __name__ == "__main__":
    main()

