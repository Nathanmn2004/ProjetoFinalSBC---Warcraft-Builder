from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    memgraph_host: str
    memgraph_port: int
    memgraph_user: str
    memgraph_password: str
    gemini_api_key: str | None
    gemini_model: str
    blizzard_client_id: str | None = None
    blizzard_client_secret: str | None = None
    blizzard_region: str = "us"
    blizzard_locale: str = "en_US"
    blizzard_namespace: str = "static-classic1x-us"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            memgraph_host=os.getenv("MEMGRAPH_HOST", "localhost"),
            memgraph_port=int(os.getenv("MEMGRAPH_PORT", "7687")),
            memgraph_user=os.getenv("MEMGRAPH_USER", ""),
            memgraph_password=os.getenv("MEMGRAPH_PASSWORD", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            blizzard_client_id=os.getenv("BLIZZARD_CLIENT_ID") or None,
            blizzard_client_secret=os.getenv("BLIZZARD_CLIENT_SECRET") or None,
            blizzard_region=os.getenv("BLIZZARD_REGION", "us"),
            blizzard_locale=os.getenv("BLIZZARD_LOCALE", "en_US"),
            blizzard_namespace=os.getenv(
                "BLIZZARD_NAMESPACE", "static-classic1x-us"
            ),
        )

    @property
    def blizzard_api_configured(self) -> bool:
        return bool(self.blizzard_client_id and self.blizzard_client_secret)
