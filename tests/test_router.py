import pytest

from voicefuse.exceptions import AllProvidersFailedError, AuthenticationError, ProviderError
from voicefuse.providers.base import BaseProvider
from voicefuse.router import Router
from voicefuse.types import AudioResponse, PricingInfo, VoiceInfo


class SuccessProvider(BaseProvider):
    name = "success"

    def tts(self, text, voice, output_format="mp3", **kwargs):
        return AudioResponse(
            data=b"audio-from-success",
            provider=self.name,
            format=output_format,
            duration_ms=100.0,
            cost=0.001,
            latency_ms=50.0,
            voice=voice,
            fallback_used=False,
        )

    def get_voices(self):
        return []

    def get_pricing(self):
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.01)


class FailProvider(BaseProvider):
    name = "fail"

    def tts(self, text, voice, output_format="mp3", **kwargs):
        raise ProviderError("Server error", provider=self.name, status_code=500)

    def get_voices(self):
        return []

    def get_pricing(self):
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.01)


class AuthFailProvider(BaseProvider):
    name = "authfail"

    def tts(self, text, voice, output_format="mp3", **kwargs):
        raise AuthenticationError("Bad key", provider=self.name)

    def get_voices(self):
        return []

    def get_pricing(self):
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.01)


def test_router_primary_succeeds():
    providers = {"success": SuccessProvider(api_key="k")}
    router = Router(providers)
    audio = router.tts_with_fallback(
        text="Hello",
        voice="v1",
        primary="success",
        fallback_chain=[],
    )
    assert audio.provider == "success"
    assert audio.fallback_used is False


def test_router_falls_back_on_failure():
    providers = {
        "fail": FailProvider(api_key="k"),
        "success": SuccessProvider(api_key="k"),
    }
    router = Router(providers)
    audio = router.tts_with_fallback(
        text="Hello",
        voice="v1",
        primary="fail",
        fallback_chain=["success"],
    )
    assert audio.provider == "success"
    assert audio.fallback_used is True


def test_router_all_providers_fail():
    providers = {
        "fail1": FailProvider(api_key="k"),
        "fail2": FailProvider(api_key="k"),
    }
    providers["fail1"].name = "fail1"
    providers["fail2"].name = "fail2"
    router = Router(providers)
    with pytest.raises(AllProvidersFailedError) as exc_info:
        router.tts_with_fallback(
            text="Hello",
            voice="v1",
            primary="fail1",
            fallback_chain=["fail2"],
        )
    assert len(exc_info.value.errors) == 2


def test_router_no_fallback_raises_provider_error():
    providers = {"fail": FailProvider(api_key="k")}
    router = Router(providers)
    with pytest.raises(ProviderError):
        router.tts_with_fallback(
            text="Hello",
            voice="v1",
            primary="fail",
            fallback_chain=[],
        )


def test_router_does_not_fallback_on_4xx():
    """4xx errors (auth, validation) should NOT trigger fallback per spec."""
    providers = {
        "authfail": AuthFailProvider(api_key="k"),
        "success": SuccessProvider(api_key="k"),
    }
    router = Router(providers)
    with pytest.raises(AuthenticationError):
        router.tts_with_fallback(
            text="Hello",
            voice="v1",
            primary="authfail",
            fallback_chain=["success"],
        )
