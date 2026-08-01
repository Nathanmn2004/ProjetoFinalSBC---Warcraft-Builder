import httpx
import pytest

from app.blizzard.auth import BlizzardAuthenticationError
from app.blizzard.client import BlizzardClassicClient
from app.config import Settings


def api_settings() -> Settings:
    return Settings(
        "localhost", 7687, "", "", None, "gemini-3.5-flash",
        "client-id", "client-secret", "us", "en_US", "static-classic1x-us",
    )


def test_classic_client_uses_oauth_and_namespace():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/oauth/token":
            return httpx.Response(200, json={"access_token": "temporary-token"})
        return httpx.Response(200, json={"id": 1, "name": "Example"})

    client = BlizzardClassicClient(api_settings(), httpx.Client(transport=httpx.MockTransport(handler)))
    assert client.get_json("/data/wow/item/1") == {"id": 1, "name": "Example"}
    assert requests[1].url.params["namespace"] == "static-classic1x-us"
    assert requests[1].headers["Authorization"] == "Bearer temporary-token"
    client.close()


def test_classic_client_rejects_non_game_data_endpoint():
    client = BlizzardClassicClient(api_settings(), httpx.Client())
    with pytest.raises(ValueError):
        client.get_json("/profile/user/wow")
    client.close()


def test_missing_credentials_fail_before_network_request():
    settings = Settings("localhost", 7687, "", "", None, "gemini-3.5-flash")
    client = BlizzardClassicClient(settings, httpx.Client())
    with pytest.raises(BlizzardAuthenticationError):
        client.get_json("/data/wow/item/1")
    client.close()
