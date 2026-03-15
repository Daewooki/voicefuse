"""Fallback example — automatically switch providers on failure."""

from voicefuse import VoiceFuse

vf = VoiceFuse()

# If ElevenLabs fails, automatically try OpenAI, then Google
audio = vf.tts(
    "This audio will be generated even if the primary provider is down.",
    provider="elevenlabs",
    voice="Rachel",
    fallback=["openai", "google"],
)

print(f"Provider used: {audio.provider}")
print(f"Fallback triggered: {audio.fallback_used}")
audio.save("output_fallback.mp3")
