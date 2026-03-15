"""Google Cloud TTS provider adapter."""

from __future__ import annotations

import base64
import time

import httpx

from voicefuse.exceptions import AuthenticationError, ProviderError, RateLimitError
from voicefuse.providers.base import BaseProvider
from voicefuse.types import AudioResponse, PricingInfo, VoiceInfo

GOOGLE_TTS_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"

FORMAT_MAP = {
    "mp3": "MP3",
    "wav": "LINEAR16",
    "ogg": "OGG_OPUS",
}


class GoogleProvider(BaseProvider):
    """Google Cloud TTS provider."""

    name = "google"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self._timeout = kwargs.get("timeout", 30.0)

    def tts(
        self,
        text: str,
        voice: str,
        output_format: str = "mp3",
        **kwargs,
    ) -> AudioResponse:
        language_code = kwargs.get("language_code", voice.rsplit("-", 1)[0] if "-" in voice else "en-US")
        audio_encoding = FORMAT_MAP.get(output_format, "MP3")

        start = time.monotonic()
        response = httpx.post(
            GOOGLE_TTS_URL,
            headers={"Content-Type": "application/json"},
            params={"key": self.api_key},
            json={
                "input": {"text": text},
                "voice": {
                    "languageCode": language_code,
                    "name": voice,
                },
                "audioConfig": {
                    "audioEncoding": audio_encoding,
                },
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

        data = response.json()
        audio_bytes = base64.b64decode(data["audioContent"])

        char_count = len(text)
        cost = (char_count / 1000) * 0.004

        return AudioResponse(
            data=audio_bytes,
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
            VoiceInfo(voice_id="en-US-Standard-A", name="Standard A", provider=self.name, language="en-US", gender="female"),
            VoiceInfo(voice_id="en-US-Standard-B", name="Standard B", provider=self.name, language="en-US", gender="male"),
            VoiceInfo(voice_id="en-US-Standard-C", name="Standard C", provider=self.name, language="en-US", gender="female"),
            VoiceInfo(voice_id="en-US-Standard-D", name="Standard D", provider=self.name, language="en-US", gender="male"),
            VoiceInfo(voice_id="en-US-Neural2-A", name="Neural2 A", provider=self.name, language="en-US", gender="female"),
            VoiceInfo(voice_id="en-US-Neural2-C", name="Neural2 C", provider=self.name, language="en-US", gender="female"),
        ]

    def get_pricing(self) -> PricingInfo:
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.004)
