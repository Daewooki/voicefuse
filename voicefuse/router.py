"""Provider routing with fallback support."""

from __future__ import annotations

import logging

from voicefuse.exceptions import AllProvidersFailedError, ProviderError
from voicefuse.providers.base import BaseProvider
from voicefuse.types import AudioResponse

logger = logging.getLogger("voicefuse")


class Router:
    """Routes TTS requests to providers with fallback support."""

    def __init__(self, providers: dict[str, BaseProvider]):
        self._providers = providers

    def tts_with_fallback(
        self,
        text: str,
        voice: str,
        primary: str,
        fallback_chain: list[str],
        output_format: str = "mp3",
        **kwargs,
    ) -> AudioResponse:
        """Try primary provider, fall back to others on failure."""
        chain = [primary] + fallback_chain
        errors: list[Exception] = []

        for i, provider_name in enumerate(chain):
            provider = self._providers.get(provider_name)
            if provider is None:
                logger.warning(f"Provider '{provider_name}' not configured, skipping")
                errors.append(ProviderError(f"Provider '{provider_name}' not configured", provider=provider_name))
                continue

            try:
                audio = provider.tts(text, voice=voice, output_format=output_format, **kwargs)
                if i > 0:
                    audio.fallback_used = True
                return audio
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Provider '{provider_name}' failed: {e}")
                errors.append(e)
                continue
            except ProviderError as e:
                # Only fallback on 5xx errors; 4xx (auth, validation) should not trigger fallback
                if e.status_code and e.status_code < 500:
                    raise
                logger.warning(f"Provider '{provider_name}' failed: {e}")
                errors.append(e)
                continue

        if len(errors) == 1:
            raise errors[0]

        raise AllProvidersFailedError(errors=errors)
