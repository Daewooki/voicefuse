import json

import httpx
import pytest
import respx

from voicefuse.providers.openai import OpenAIProvider
from voicefuse.exceptions import ProviderError, AuthenticationError


@respx.mock
def test_openai_tts_success():
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"fake-mp3-audio")
    )
    provider = OpenAIProvider(api_key="sk-test")
    audio = provider.tts("Hello world", voice="alloy")
    assert audio.data == b"fake-mp3-audio"
    assert audio.provider == "openai"
    assert audio.voice == "alloy"
    assert audio.format == "mp3"
    assert audio.fallback_used is False
    assert audio.latency_ms >= 0


@respx.mock
def test_openai_tts_with_model():
    route = respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"audio")
    )
    provider = OpenAIProvider(api_key="sk-test")
    provider.tts("Hello", voice="alloy", model="tts-1-hd")
    request = route.calls[0].request
    body = json.loads(request.content)
    assert body["model"] == "tts-1-hd"


@respx.mock
def test_openai_tts_auth_error():
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(401, json={"error": {"message": "Invalid API key"}})
    )
    provider = OpenAIProvider(api_key="bad-key")
    with pytest.raises(AuthenticationError, match="openai"):
        provider.tts("Hello", voice="alloy")


@respx.mock
def test_openai_tts_server_error():
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(500, json={"error": {"message": "Server error"}})
    )
    provider = OpenAIProvider(api_key="sk-test")
    with pytest.raises(ProviderError, match="openai"):
        provider.tts("Hello", voice="alloy")


def test_openai_get_voices():
    provider = OpenAIProvider(api_key="sk-test")
    voices = provider.get_voices()
    assert len(voices) > 0
    assert any(v.voice_id == "alloy" for v in voices)


def test_openai_get_pricing():
    provider = OpenAIProvider(api_key="sk-test")
    pricing = provider.get_pricing()
    assert pricing.provider == "openai"
    assert pricing.cost_per_1k_chars > 0
