"""Tests for cross-provider voice matching."""

from voicefuse.voice_map import resolve_voice, get_voice_matches


def test_resolve_unified_voice():
    """Unified voice names map to each provider."""
    result = resolve_voice("female-warm", "openai")
    assert result.voice == "nova"
    assert result.match_type == "unified"

    result = resolve_voice("female-warm", "elevenlabs")
    assert result.voice == "Rachel"
    assert result.match_type == "unified"

    result = resolve_voice("male-deep", "google")
    assert result.voice == "en-US-Neural2-D"
    assert result.match_type == "unified"


def test_resolve_exact_match():
    """Voice belonging to target provider is exact match."""
    result = resolve_voice("alloy", "openai")
    assert result.voice == "alloy"
    assert result.match_type == "exact"


def test_resolve_cross_provider_mapping():
    """OpenAI voice used with ElevenLabs maps to similar voice."""
    result = resolve_voice("alloy", "elevenlabs")
    assert result.voice == "Rachel"
    assert result.match_type == "mapped"
    assert result.original_voice == "alloy"


def test_resolve_elevenlabs_to_openai():
    """ElevenLabs voice used with OpenAI maps correctly."""
    result = resolve_voice("Rachel", "openai")
    assert result.voice == "alloy"
    assert result.match_type == "mapped"
    assert result.original_voice == "Rachel"


def test_resolve_google_to_openai():
    """Google voice used with OpenAI maps correctly."""
    result = resolve_voice("en-US-Neural2-C", "openai")
    assert result.voice == "alloy"
    assert result.match_type == "mapped"


def test_resolve_unknown_voice_passthrough():
    """Unknown voice is passed through as-is."""
    result = resolve_voice("custom-voice-xyz", "openai")
    assert result.voice == "custom-voice-xyz"
    assert result.match_type == "passthrough"


def test_get_voice_matches_openai():
    """Get all matches for an OpenAI voice."""
    matches = get_voice_matches("alloy")
    providers = {m.provider for m in matches}
    assert "openai" in providers
    assert "elevenlabs" in providers
    assert "google" in providers
    assert len(matches) == 3

    exact = next(m for m in matches if m.match_type == "exact")
    assert exact.provider == "openai"
    assert exact.voice == "alloy"


def test_get_voice_matches_unified():
    """Get all matches for a unified voice name."""
    matches = get_voice_matches("female-warm")
    assert len(matches) == 3
    assert all(m.match_type == "unified" for m in matches)

    providers = {m.provider: m.voice for m in matches}
    assert providers["openai"] == "nova"
    assert providers["elevenlabs"] == "Rachel"


def test_get_voice_matches_unknown():
    """Unknown voice returns empty list."""
    matches = get_voice_matches("nonexistent-voice")
    assert matches == []


def test_all_unified_voices_have_all_providers():
    """Every unified voice has mappings for all 3 providers."""
    from voicefuse.voice_map import UNIFIED_VOICES
    for name, mappings in UNIFIED_VOICES.items():
        assert "openai" in mappings, f"{name} missing openai"
        assert "elevenlabs" in mappings, f"{name} missing elevenlabs"
        assert "google" in mappings, f"{name} missing google"
