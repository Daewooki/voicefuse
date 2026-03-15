"""OpenAI TTS provider adapter."""

from __future__ import annotations

import time

import httpx

from voicefuse.exceptions import AuthenticationError, ProviderError, RateLimitError
from voicefuse.providers.base import BaseProvider
from voicefuse.types import AudioResponse, PricingInfo, VoiceInfo

OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"

OPENAI_VOICES = [
    VoiceInfo(voice_id="alloy", name="Alloy", provider="openai"),
    VoiceInfo(voice_id="echo", name="Echo", provider="openai"),
    VoiceInfo(voice_id="fable", name="Fable", provider="openai"),
    VoiceInfo(voice_id="onyx", name="Onyx", provider="openai"),
    VoiceInfo(voice_id="nova", name="Nova", provider="openai"),
    VoiceInfo(voice_id="shimmer", name="Shimmer", provider="openai"),
]


class OpenAIProvider(BaseProvider):
    """OpenAI TTS provider."""

    name = "openai"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self._default_model = kwargs.get("default_model", "tts-1")
        self._timeout = kwargs.get("timeout", 30.0)

    def tts(
        self,
        text: str,
        voice: str,
        output_format: str = "mp3",
        **kwargs,
    ) -> AudioResponse:
        model = kwargs.get("model", self._default_model)
        response_format = output_format if output_format in ("mp3", "opus", "aac", "flac", "wav", "pcm") else "mp3"

        start = time.monotonic()
        response = httpx.post(
            OPENAI_TTS_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": response_format,
            },
            timeout=self._timeout,
        )
        latency_ms = (time.monotonic() - start) * 1000

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key", provider=self.name)
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", provider=self.name)
        if response.status_code >= 400:
            msg = response.text
            raise ProviderError(msg, provider=self.name, status_code=response.status_code)

        char_count = len(text)
        cost = (char_count / 1000) * 0.015  # tts-1 pricing

        return AudioResponse(
            data=response.content,
            provider=self.name,
            format=response_format,
            duration_ms=0.0,
            cost=cost,
            latency_ms=latency_ms,
            voice=voice,
            fallback_used=False,
        )

    def get_voices(self) -> list[VoiceInfo]:
        return OPENAI_VOICES.copy()

    def get_pricing(self) -> PricingInfo:
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.015)
