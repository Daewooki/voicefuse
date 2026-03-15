import pytest

from voicefuse.client import VoiceFuse
from voicefuse.exceptions import VoiceFuseError, ProviderError
from voicefuse.providers.base import BaseProvider
from voicefuse.types import AudioResponse, VoiceInfo, PricingInfo


class MockProvider(BaseProvider):
    name = "mock"

    def __init__(self, api_key="mock-key", fail=False, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self._fail = fail

    def tts(self, text, voice, output_format="mp3", **kwargs):
        if self._fail:
            raise ProviderError("Mock failure", provider=self.name, status_code=500)
        return AudioResponse(
            data=f"audio-from-{self.name}".encode(),
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
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.01)


class MockProvider2(MockProvider):
    name = "mock2"


def test_client_tts_basic():
    vf = VoiceFuse(providers={"mock": MockProvider()})
    audio = vf.tts("Hello", provider="mock", voice="v1")
    assert audio.provider == "mock"
    assert audio.data == b"audio-from-mock"


def test_client_tts_with_fallback():
    fail_provider = MockProvider(fail=True)
    success_provider = MockProvider2()
    vf = VoiceFuse(providers={"mock": fail_provider, "mock2": success_provider})
    audio = vf.tts("Hello", provider="mock", voice="v1", fallback=["mock2"])
    assert audio.provider == "mock2"
    assert audio.fallback_used is True


def test_client_provider_and_strategy_raises():
    vf = VoiceFuse(providers={"mock": MockProvider()})
    with pytest.raises(VoiceFuseError, match="Cannot specify both"):
        vf.tts("Hello", provider="mock", voice="v1", strategy="cheapest")


def test_client_compare_tts():
    p1 = MockProvider()
    p2 = MockProvider2()
    vf = VoiceFuse(providers={"mock": p1, "mock2": p2})
    results = vf.compare_tts("Hello", providers=["mock", "mock2"], voice="v1")
    assert len(results) == 2
    providers_returned = {r.provider for r in results}
    assert providers_returned == {"mock", "mock2"}


def test_client_no_provider_specified_uses_default():
    vf = VoiceFuse(providers={"mock": MockProvider()}, default_provider="mock")
    audio = vf.tts("Hello", voice="v1")
    assert audio.provider == "mock"


def test_client_no_provider_no_default_raises():
    vf = VoiceFuse(providers={"mock": MockProvider()})
    with pytest.raises(VoiceFuseError, match="No provider specified"):
        vf.tts("Hello", voice="v1")


def test_client_strategy_cheapest():
    p1 = MockProvider()
    p2 = MockProvider2()
    vf = VoiceFuse(providers={"mock": p1, "mock2": p2})
    audio = vf.tts("Hello", voice="v1", strategy="cheapest")
    assert audio.provider in ("mock", "mock2")


def test_client_compare_tts_partial_failure():
    """When one provider fails, compare_tts returns results from the others."""
    p_ok = MockProvider()
    p_fail = MockProvider2(fail=True)
    vf = VoiceFuse(providers={"mock": p_ok, "mock2": p_fail})
    results = vf.compare_tts("Hello", providers=["mock", "mock2"], voice="v1")
    assert len(results) == 1
    assert results[0].provider == "mock"
