"""VoiceFuse — LiteLLM for Voice. One API for every Voice AI provider."""

from voicefuse.client import VoiceFuse
from voicefuse.types import AudioResponse
from voicefuse.exceptions import (
    VoiceFuseError,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    UnsupportedFeatureError,
    AllProvidersFailedError,
)

__version__ = "0.1.0"

__all__ = [
    "VoiceFuse",
    "AudioResponse",
    "VoiceFuseError",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "UnsupportedFeatureError",
    "AllProvidersFailedError",
]
