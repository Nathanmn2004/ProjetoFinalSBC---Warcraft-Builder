import pytest

from app.graph.query_builder import Intent, assert_read_only, parse_question, query_for


@pytest.mark.parametrize(
    ("question", "intent"),
    [
        ('Quem entrega a missao "Further Concerns"?', Intent.QUEST_GIVER),
        ('Qual e a sequencia ate "Report to Thomas"?', Intent.QUEST_CHAIN),
        ('Onde devo ir depois de "Find the Lost Guards"?', Intent.NEXT_QUEST),
        ('Em qual regiao fica "Northshire Abbey"?', Intent.LOCATION),
        ('Como consigo "Kobold Candle"?', Intent.ITEM_SOURCE),
    ],
)
def test_intents(question, intent):
    assert parse_question(question).intent == intent


def test_all_built_in_queries_are_read_only():
    for intent in Intent:
        assert_read_only(query_for(parse_question({
            Intent.QUEST_GIVER: 'quem entrega "x"',
            Intent.QUEST_CHAIN: 'sequencia "x"',
            Intent.NEXT_QUEST: 'depois de "x"',
            Intent.ITEM_SOURCE: 'como consigo "x"',
            Intent.LOCATION: 'onde fica "x"',
            Intent.NEIGHBORHOOD: 'relacao "x"',
        }[intent])))


def test_mutating_query_is_rejected():
    with pytest.raises(ValueError):
        assert_read_only("MATCH (n) DETACH DELETE n")

