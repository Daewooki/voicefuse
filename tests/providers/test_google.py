import base64
import json

import httpx
import pytest
import respx

from voicefuse.providers.google import GoogleProvider
from voicefuse.exceptions import ProviderError, AuthenticationError


@respx.mock
def test_google_tts_success():
    audio_b64 = base64.b64encode(b"fake-google-audio").decode()
    respx.post("https://texttospeech.googleapis.com/v1/text:synthesize").mock(
        return_value=httpx.Response(200, json={"audioContent": audio_b64})
    )
    provider = GoogleProvider(api_key="gcp-test-key")
    audio = provider.tts("Hello world", voice="en-US-Standard-A")
    assert audio.data == b"fake-google-audio"
    assert audio.provider == "google"
    assert audio.voice == "en-US-Standard-A"
    assert audio.format == "mp3"


@respx.mock
def test_google_tts_request_body():
    audio_b64 = base64.b64encode(b"audio").decode()
    route = respx.post("https://texttospeech.googleapis.com/v1/text:synthesize").mock(
        return_value=httpx.Response(200, json={"audioContent": audio_b64})
    )
    provider = GoogleProvider(api_key="gcp-key")
    provider.tts("Hello", voice="en-US-Standard-B", output_format="wav")
    body = json.loads(route.calls[0].request.content)
    assert body["input"]["text"] == "Hello"
    assert body["voice"]["name"] == "en-US-Standard-B"


@respx.mock
def test_google_tts_auth_error():
    respx.post("https://texttospeech.googleapis.com/v1/text:synthesize").mock(
        return_value=httpx.Response(401, json={"error": {"message": "Invalid API key"}})
    )
    provider = GoogleProvider(api_key="bad-key")
    with pytest.raises(AuthenticationError, match="google"):
        provider.tts("Hello", voice="en-US-Standard-A")


@respx.mock
def test_google_tts_server_error():
    respx.post("https://texttospeech.googleapis.com/v1/text:synthesize").mock(
        return_value=httpx.Response(500, text="Internal error")
    )
    provider = GoogleProvider(api_key="gcp-key")
    with pytest.raises(ProviderError, match="google"):
        provider.tts("Hello", voice="en-US-Standard-A")


def test_google_get_pricing():
    provider = GoogleProvider(api_key="gcp-key")
    pricing = provider.get_pricing()
    assert pricing.provider == "google"
    assert pricing.cost_per_1k_chars > 0
