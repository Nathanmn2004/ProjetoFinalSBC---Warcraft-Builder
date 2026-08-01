from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.blizzard.auth import BlizzardOAuth
from app.config import Settings


class BlizzardApiError(RuntimeError):
    """Raised for a failed Game Data API request."""


@dataclass
class BlizzardClassicClient:
    """Small, explicit client for Blizzard Classic Game Data API requests."""

    settings: Settings
    http_client: httpx.Client

    @classmethod
    def from_settings(cls, settings: Settings) -> "BlizzardClassicClient":
        return cls(settings=settings, http_client=httpx.Client(timeout=30.0))

    def close(self) -> None:
        self.http_client.close()

    def get_json(self, path: str, *, namespace: str | None = None) -> dict[str, Any]:
        if not path.startswith("/data/wow/"):
            raise ValueError("Apenas endpoints Game Data /data/wow/ sao permitidos.")
        token = BlizzardOAuth(self.settings, self.http_client).access_token()
        response = self.http_client.get(
            f"https://{self.settings.blizzard_region}.api.blizzard.com{path}",
            params={
                "namespace": namespace or self.settings.blizzard_namespace,
                "locale": self.settings.blizzard_locale,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise BlizzardApiError(f"Falha ao consultar o endpoint Blizzard {path}.") from exc
        if not isinstance(payload, dict):
            raise BlizzardApiError(f"Resposta invalida da Blizzard para {path}.")
        return payload
