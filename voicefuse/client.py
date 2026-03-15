"""VoiceFuse main client."""

from __future__ import annotations

from voicefuse.config import VoiceFuseConfig, load_config
from voicefuse.exceptions import VoiceFuseError
from voicefuse.providers.base import BaseProvider
from voicefuse.router import Router
from voicefuse.types import AudioResponse, CompareResult
from voicefuse.voice_map import resolve_voice


class VoiceFuse:
    """Universal Voice AI gateway client."""

    def __init__(
        self,
        config_path: str | None = None,
        *,
        providers: dict[str, BaseProvider] | None = None,
        default_provider: str | None = None,
        default_fallback: list[str] | None = None,
    ):
        if providers is not None:
            self._providers = providers
            self._default_provider = default_provider
            self._default_fallback = default_fallback or []
        else:
            config = load_config(config_path)
            self._providers = self._init_providers(config)
            self._default_provider = config.default_provider
            self._default_fallback = config.default_fallback

        self._router = Router(self._providers)

    def _init_providers(self, config: VoiceFuseConfig) -> dict[str, BaseProvider]:
        from voicefuse.providers import PROVIDER_REGISTRY

        providers = {}
        for name, settings in config.providers.items():
            provider_cls = PROVIDER_REGISTRY.get(name)
            if provider_cls is None:
                continue
            api_key = settings.get("api_key", "")
            extra = {k: v for k, v in settings.items() if k != "api_key"}
            providers[name] = provider_cls(api_key=api_key, **extra)
        return providers

    def tts(
        self,
        text: str,
        *,
        provider: str | None = None,
        voice: str = "",
        output_format: str = "mp3",
        fallback: list[str] | None = None,
        strategy: str | None = None,
        **kwargs,
    ) -> AudioResponse:
        """Generate speech from text."""
        if provider and strategy:
            raise VoiceFuseError("Cannot specify both 'provider' and 'strategy'")

        if strategy:
            provider = self._select_by_strategy(strategy)

        if not provider:
            provider = self._default_provider

        if not provider:
            raise VoiceFuseError("No provider specified and no default configured")

        fallback_chain = fallback if fallback is not None else self._default_fallback

        # Resolve voice across providers
        if voice:
            match = resolve_voice(voice, provider)
            resolved_voice = match.voice
        else:
            resolved_voice = voice

        return self._router.tts_with_fallback(
            text=text,
            voice=resolved_voice,
            primary=provider,
            fallback_chain=fallback_chain,
            output_format=output_format,
            **kwargs,
        )

    def compare_tts(
        self,
        text: str,
        *,
        providers: list[str],
        voice: str = "",
        output_format: str = "mp3",
        **kwargs,
    ) -> list[CompareResult]:
        """Compare TTS output from multiple providers."""
        results: list[CompareResult] = []

        for provider_name in providers:
            try:
                # Resolve voice for each provider
                if voice:
                    match = resolve_voice(voice, provider_name)
                    resolved_voice = match.voice
                else:
                    resolved_voice = voice

                audio = self._router.tts_with_fallback(
                    text=text,
                    voice=resolved_voice,
                    primary=provider_name,
                    fallback_chain=[],
                    output_format=output_format,
                    **kwargs,
                )
                results.append(CompareResult(
                    provider=provider_name,
                    audio=audio,
                    latency_ms=audio.latency_ms,
                    cost=audio.cost,
                    audio_size=len(audio.data),
                ))
            except Exception:
                continue

        return results

    def _select_by_strategy(self, strategy: str) -> str:
        """Select a provider based on routing strategy."""
        if not self._providers:
            raise VoiceFuseError("No providers configured")

        if strategy == "cheapest":
            return min(
                self._providers,
                key=lambda name: self._providers[name].get_pricing().cost_per_1k_chars,
            )
        if strategy == "best_quality":
            quality_order = ["elevenlabs", "openai", "google"]
            for name in quality_order:
                if name in self._providers:
                    return name
            return next(iter(self._providers))

        raise VoiceFuseError(f"Unknown strategy: '{strategy}'")
