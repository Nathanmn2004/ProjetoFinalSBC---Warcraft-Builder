from app.config import Settings
from app.llm.response_generator import ResponseGenerator


def settings_without_key():
    return Settings("localhost", 7687, "", "", None, "gemini-3.5-flash")


def test_unknown_answer_admits_missing_knowledge():
    answer = ResponseGenerator(settings_without_key()).generate("x", "Unknown", [])
    assert "nao possui informacao suficiente" in answer
    assert "Fundamentacao" in answer


def test_fallback_contains_retrieved_fact():
    answer = ResponseGenerator(settings_without_key()).generate("x", "Quest", [{"giver": "NPC"}])
    assert "NPC" in answer

