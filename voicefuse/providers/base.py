"""Base provider abstract class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from voicefuse.types import AudioResponse, VoiceInfo, PricingInfo


class BaseProvider(ABC):
    """Abstract base class for all voice AI providers."""

    name: str

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self._extra_config = kwargs

    @abstractmethod
    def tts(
        self,
        text: str,
        voice: str,
        output_format: str = "mp3",
        **kwargs,
    ) -> AudioResponse:
        """Generate speech from text."""
        ...

    @abstractmethod
    def get_voices(self) -> list[VoiceInfo]:
        """List available voices for this provider."""
        ...

    @abstractmethod
    def get_pricing(self) -> PricingInfo:
        """Return pricing info for this provider."""
        ...
