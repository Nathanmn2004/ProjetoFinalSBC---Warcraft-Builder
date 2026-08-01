import json

from app.config import Settings
from app.llm.prompts import SYSTEM_RULES


class ResponseGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _fallback(entity: str, facts: list[dict]) -> str:
        if not facts:
            return (
                f'O grafo nao possui informacao suficiente sobre "{entity}".\n\n'
                "Fundamentacao:\n- Nenhum fato correspondente foi recuperado."
            )
        lines = [f"- {json.dumps(fact, ensure_ascii=False, default=str)}" for fact in facts]
        return "Fatos recuperados para responder a pergunta:\n" + "\n".join(lines) + "\n\nFundamentacao:\n" + "\n".join(lines)

    def generate(self, question: str, entity: str, facts: list[dict]) -> str:
        if not self.settings.gemini_api_key:
            return self._fallback(entity, facts)

        from google import genai

        prompt = (
            f"{SYSTEM_RULES}\nPergunta: {question}\nEntidade resolvida: {entity}\n"
            f"Fatos recuperados: {json.dumps(facts, ensure_ascii=False, default=str)}"
        )
        try:
            client = genai.Client(api_key=self.settings.gemini_api_key)
            interaction = client.interactions.create(
                model=self.settings.gemini_model,
                input=prompt,
            )
            return interaction.output_text
        except Exception as exc:
            fallback = self._fallback(entity, facts)
            return f"{fallback}\n\n[Gemini indisponivel: {type(exc).__name__}]"

