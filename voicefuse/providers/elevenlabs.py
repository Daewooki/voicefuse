"""ElevenLabs TTS provider adapter."""

from __future__ import annotations

import time

import httpx

from voicefuse.exceptions import AuthenticationError, ProviderError, RateLimitError
from voicefuse.providers.base import BaseProvider
from voicefuse.types import AudioResponse, PricingInfo, VoiceInfo

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

# Map display names to actual ElevenLabs voice IDs
VOICE_NAME_TO_ID = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
}


class ElevenLabsProvider(BaseProvider):
    """ElevenLabs TTS provider."""

    name = "elevenlabs"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self._default_model = kwargs.get("default_model", "eleven_monolingual_v1")
        self._timeout = kwargs.get("timeout", 30.0)

    def tts(
        self,
        text: str,
        voice: str,
        output_format: str = "mp3",
        **kwargs,
    ) -> AudioResponse:
        model = kwargs.get("model", self._default_model)
        # Resolve display name to actual voice ID
        voice_id = VOICE_NAME_TO_ID.get(voice, voice)
        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"

        start = time.monotonic()
        response = httpx.post(
            url,
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": f"audio/{output_format}",
            },
            json={
                "text": text,
                "model_id": model,
            },
            timeout=self._timeout,
        )
        latency_ms = (time.monotonic() - start) * 1000

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key", provider=self.name)
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", provider=self.name)
        if response.status_code >= 400:
            raise ProviderError(response.text, provider=self.name, status_code=response.status_code)

        char_count = len(text)
        cost = (char_count / 1000) * 0.030

        return AudioResponse(
            data=response.content,
            provider=self.name,
            format=output_format,
            duration_ms=0.0,
            cost=cost,
            latency_ms=latency_ms,
            voice=voice,
            fallback_used=False,
        )

    def get_voices(self) -> list[VoiceInfo]:
        return [
            VoiceInfo(voice_id="Rachel", name="Rachel", provider=self.name),
            VoiceInfo(voice_id="Domi", name="Domi", provider=self.name),
            VoiceInfo(voice_id="Bella", name="Bella", provider=self.name),
            VoiceInfo(voice_id="Antoni", name="Antoni", provider=self.name),
            VoiceInfo(voice_id="Elli", name="Elli", provider=self.name),
            VoiceInfo(voice_id="Josh", name="Josh", provider=self.name),
            VoiceInfo(voice_id="Arnold", name="Arnold", provider=self.name),
            VoiceInfo(voice_id="Adam", name="Adam", provider=self.name),
            VoiceInfo(voice_id="Sam", name="Sam", provider=self.name),
        ]

    def get_pricing(self) -> PricingInfo:
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.030)
