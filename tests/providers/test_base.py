import pytest

from voicefuse.providers.base import BaseProvider
from voicefuse.types import AudioResponse, VoiceInfo, PricingInfo


def test_cannot_instantiate_base_provider():
    with pytest.raises(TypeError):
        BaseProvider(api_key="test")


class FakeProvider(BaseProvider):
    name = "fake"

    def tts(self, text, voice, output_format="mp3", **kwargs):
        return AudioResponse(
            data=b"audio",
            provider=self.name,
            format=output_format,
            duration_ms=100.0,
            cost=0.001,
            latency_ms=50.0,
            voice=voice,
            fallback_used=False,
        )

    def get_voices(self):
        return [VoiceInfo(voice_id="v1", name="Voice1", provider=self.name)]

    def get_pricing(self):
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.015)


def test_concrete_provider_works():
    provider = FakeProvider(api_key="test-key")
    audio = provider.tts("hello", voice="v1")
    assert audio.provider == "fake"
    assert audio.data == b"audio"


def test_provider_has_api_key():
    provider = FakeProvider(api_key="test-key")
    assert provider.api_key == "test-key"
