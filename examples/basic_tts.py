"""Basic TTS example — generate speech with OpenAI."""

from voicefuse import VoiceFuse

vf = VoiceFuse()

# Generate speech using OpenAI
audio = vf.tts("Hello! This is VoiceFuse, a universal voice AI gateway.", provider="openai", voice="alloy")
audio.save("output_openai.mp3")
print(f"Saved output_openai.mp3 ({len(audio.data)} bytes, {audio.latency_ms:.0f}ms)")

# Same text, different provider — just change one parameter
audio = vf.tts("Hello! This is VoiceFuse, a universal voice AI gateway.", provider="elevenlabs", voice="Rachel")
audio.save("output_elevenlabs.mp3")
print(f"Saved output_elevenlabs.mp3 ({len(audio.data)} bytes, {audio.latency_ms:.0f}ms)")
