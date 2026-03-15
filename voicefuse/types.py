"""Core types for VoiceFuse."""

from __future__ import annotations

import base64
from dataclasses import dataclass


@dataclass
class AudioResponse:
    """Response from a TTS provider."""

    data: bytes
    provider: str
    format: str
    duration_ms: float
    cost: float | None
    latency_ms: float
    voice: str
    fallback_used: bool

    def save(self, path: str) -> None:
        """Save audio data to a file."""
        with open(path, "wb") as f:
            f.write(self.data)

    def to_bytes(self) -> bytes:
        """Return raw audio bytes."""
        return self.data

    def to_base64(self) -> str:
        """Return audio data as base64-encoded string."""
        return base64.b64encode(self.data).decode("utf-8")


@dataclass
class VoiceInfo:
    """Information about an available voice."""

    voice_id: str
    name: str
    provider: str
    language: str | None = None
    gender: str | None = None


@dataclass
class PricingInfo:
    """Pricing information for a provider."""

    provider: str
    cost_per_1k_chars: float
    currency: str = "USD"


@dataclass
class CompareResult:
    """Result from comparing TTS across providers."""

    provider: str
    audio: AudioResponse
    latency_ms: float
    cost: float | None
    audio_size: int
