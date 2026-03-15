import json

import httpx
import pytest
import respx

from voicefuse.providers.elevenlabs import ElevenLabsProvider
from voicefuse.exceptions import ProviderError, AuthenticationError


@respx.mock
def test_elevenlabs_tts_success():
    respx.post("https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM").mock(
        return_value=httpx.Response(200, content=b"fake-elevenlabs-audio")
    )
    provider = ElevenLabsProvider(api_key="el-test")
    audio = provider.tts("Hello world", voice="Rachel")
    assert audio.data == b"fake-elevenlabs-audio"
    assert audio.provider == "elevenlabs"
    assert audio.voice == "Rachel"
    assert audio.format == "mp3"


@respx.mock
def test_elevenlabs_tts_with_model():
    route = respx.post("https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM").mock(
        return_value=httpx.Response(200, content=b"audio")
    )
    provider = ElevenLabsProvider(api_key="el-test")
    provider.tts("Hello", voice="Rachel", model="eleven_turbo_v2")
    body = json.loads(route.calls[0].request.content)
    assert body["model_id"] == "eleven_turbo_v2"


@respx.mock
def test_elevenlabs_tts_auth_error():
    respx.post("https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM").mock(
        return_value=httpx.Response(401, json={"detail": {"message": "Unauthorized"}})
    )
    provider = ElevenLabsProvider(api_key="bad-key")
    with pytest.raises(AuthenticationError, match="elevenlabs"):
        provider.tts("Hello", voice="Rachel")


@respx.mock
def test_elevenlabs_tts_server_error():
    respx.post("https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM").mock(
        return_value=httpx.Response(500, text="Internal server error")
    )
    provider = ElevenLabsProvider(api_key="el-test")
    with pytest.raises(ProviderError, match="elevenlabs"):
        provider.tts("Hello", voice="Rachel")


def test_elevenlabs_get_pricing():
    provider = ElevenLabsProvider(api_key="el-test")
    pricing = provider.get_pricing()
    assert pricing.provider == "elevenlabs"
    assert pricing.cost_per_1k_chars > 0
