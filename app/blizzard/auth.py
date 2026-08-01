from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import Settings


class BlizzardAuthenticationError(RuntimeError):
    """Raised when the Blizzard OAuth token cannot be obtained."""


@dataclass
class BlizzardOAuth:
    settings: Settings
    http_client: httpx.Client

    def access_token(self) -> str:
        if not self.settings.blizzard_api_configured:
            raise BlizzardAuthenticationError(
                "BLIZZARD_CLIENT_ID e BLIZZARD_CLIENT_SECRET sao obrigatorios para sincronizar a API."
            )
        response = self.http_client.post(
            f"https://{self.settings.blizzard_region}.battle.net/oauth/token",
            data={"grant_type": "client_credentials"},
            auth=(self.settings.blizzard_client_id, self.settings.blizzard_client_secret),
        )
        try:
            response.raise_for_status()
            token = response.json()["access_token"]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise BlizzardAuthenticationError("Nao foi possivel obter um token OAuth da Blizzard.") from exc
        if not isinstance(token, str) or not token:
            raise BlizzardAuthenticationError("A Blizzard nao retornou um access token valido.")
        return token
