"""Cross-provider voice matching.

Maps voice names across providers so users can use any voice name with any provider.
For example, using OpenAI's "alloy" with ElevenLabs will automatically map to the
most similar ElevenLabs voice.
"""

from __future__ import annotations

from dataclasses import dataclass

# Unified voice categories — provider-agnostic voice descriptors
# Users can use these instead of provider-specific voice names.
UNIFIED_VOICES: dict[str, dict[str, str]] = {
    # Female voices
    "female-warm": {
        "openai": "nova",
        "elevenlabs": "Rachel",
        "google": "en-US-Neural2-C",
    },
    "female-bright": {
        "openai": "shimmer",
        "elevenlabs": "Bella",
        "google": "en-US-Neural2-A",
    },
    "female-calm": {
        "openai": "alloy",
        "elevenlabs": "Elli",
        "google": "en-US-Standard-C",
    },
    # Male voices
    "male-deep": {
        "openai": "onyx",
        "elevenlabs": "Adam",
        "google": "en-US-Neural2-D",
    },
    "male-warm": {
        "openai": "echo",
        "elevenlabs": "Josh",
        "google": "en-US-Standard-B",
    },
    "male-narrative": {
        "openai": "fable",
        "elevenlabs": "Antoni",
        "google": "en-US-Standard-D",
    },
}

# Cross-provider voice similarity mapping.
# Key: (source_provider, voice_id) → {target_provider: best_match_voice_id}
VOICE_SIMILARITY: dict[tuple[str, str], dict[str, str]] = {
    # OpenAI voices → other providers
    ("openai", "alloy"): {"elevenlabs": "Rachel", "google": "en-US-Neural2-C"},
    ("openai", "echo"): {"elevenlabs": "Josh", "google": "en-US-Standard-B"},
    ("openai", "fable"): {"elevenlabs": "Antoni", "google": "en-US-Standard-D"},
    ("openai", "onyx"): {"elevenlabs": "Adam", "google": "en-US-Neural2-D"},
    ("openai", "nova"): {"elevenlabs": "Bella", "google": "en-US-Neural2-A"},
    ("openai", "shimmer"): {"elevenlabs": "Elli", "google": "en-US-Standard-C"},
    # ElevenLabs voices → other providers
    ("elevenlabs", "Rachel"): {"openai": "alloy", "google": "en-US-Neural2-C"},
    ("elevenlabs", "Domi"): {"openai": "nova", "google": "en-US-Neural2-A"},
    ("elevenlabs", "Bella"): {"openai": "shimmer", "google": "en-US-Standard-C"},
    ("elevenlabs", "Antoni"): {"openai": "fable", "google": "en-US-Standard-D"},
    ("elevenlabs", "Elli"): {"openai": "shimmer", "google": "en-US-Standard-A"},
    ("elevenlabs", "Josh"): {"openai": "echo", "google": "en-US-Standard-B"},
    ("elevenlabs", "Arnold"): {"openai": "onyx", "google": "en-US-Neural2-D"},
    ("elevenlabs", "Adam"): {"openai": "onyx", "google": "en-US-Standard-D"},
    ("elevenlabs", "Sam"): {"openai": "echo", "google": "en-US-Standard-B"},
    # Google voices → other providers
    ("google", "en-US-Standard-A"): {"openai": "shimmer", "elevenlabs": "Elli"},
    ("google", "en-US-Standard-B"): {"openai": "echo", "elevenlabs": "Josh"},
    ("google", "en-US-Standard-C"): {"openai": "shimmer", "elevenlabs": "Bella"},
    ("google", "en-US-Standard-D"): {"openai": "fable", "elevenlabs": "Antoni"},
    ("google", "en-US-Neural2-A"): {"openai": "nova", "elevenlabs": "Bella"},
    ("google", "en-US-Neural2-C"): {"openai": "alloy", "elevenlabs": "Rachel"},
    ("google", "en-US-Neural2-D"): {"openai": "onyx", "elevenlabs": "Adam"},
}


@dataclass
class VoiceMatch:
    """Result of voice matching."""

    voice: str
    provider: str
    match_type: str  # "exact", "mapped", "unified", "passthrough"
    original_voice: str | None = None


def resolve_voice(voice: str, target_provider: str, available_providers: list[str] | None = None) -> VoiceMatch:
    """Resolve a voice name to the best match for the target provider.

    Resolution order:
    1. Check if it's a unified voice name (e.g., "female-warm")
    2. Check if it belongs to the target provider already (exact match)
    3. Check cross-provider similarity map
    4. Passthrough (use as-is, let the provider handle it)
    """
    # 1. Unified voice name
    if voice in UNIFIED_VOICES:
        unified = UNIFIED_VOICES[voice]
        if target_provider in unified:
            return VoiceMatch(
                voice=unified[target_provider],
                provider=target_provider,
                match_type="unified",
                original_voice=voice,
            )

    # 2. Check if voice belongs to target provider (exact match)
    if (target_provider, voice) in VOICE_SIMILARITY:
        return VoiceMatch(
            voice=voice,
            provider=target_provider,
            match_type="exact",
        )

    # 3. Check cross-provider mapping
    for (src_provider, src_voice), mappings in VOICE_SIMILARITY.items():
        if src_voice == voice and src_provider != target_provider:
            if target_provider in mappings:
                return VoiceMatch(
                    voice=mappings[target_provider],
                    provider=target_provider,
                    match_type="mapped",
                    original_voice=voice,
                )

    # 4. Passthrough
    return VoiceMatch(
        voice=voice,
        provider=target_provider,
        match_type="passthrough",
    )


def get_voice_matches(voice: str) -> list[VoiceMatch]:
    """Get all provider matches for a given voice name."""
    matches: list[VoiceMatch] = []

    # Check unified voices
    if voice in UNIFIED_VOICES:
        for provider, mapped_voice in UNIFIED_VOICES[voice].items():
            matches.append(VoiceMatch(
                voice=mapped_voice,
                provider=provider,
                match_type="unified",
                original_voice=voice,
            ))
        return matches

    # Find the source provider for this voice
    for (src_provider, src_voice), mappings in VOICE_SIMILARITY.items():
        if src_voice == voice:
            # Add exact match
            matches.append(VoiceMatch(
                voice=src_voice,
                provider=src_provider,
                match_type="exact",
            ))
            # Add mapped matches
            for target_provider, target_voice in mappings.items():
                matches.append(VoiceMatch(
                    voice=target_voice,
                    provider=target_provider,
                    match_type="mapped",
                    original_voice=voice,
                ))
            return matches

    return matches
