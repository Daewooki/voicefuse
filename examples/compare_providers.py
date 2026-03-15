"""Compare providers — A/B test TTS quality, latency, and cost."""

from voicefuse import VoiceFuse

vf = VoiceFuse()

results = vf.compare_tts(
    "The quick brown fox jumps over the lazy dog.",
    providers=["openai", "elevenlabs", "google"],
    voice="alloy",
)

print(f"{'Provider':<15} {'Latency (ms)':<15} {'Cost ($)':<10} {'Size (bytes)':<15}")
print("-" * 55)
for r in results:
    cost_str = f"${r.cost:.4f}" if r.cost else "N/A"
    print(f"{r.provider:<15} {r.latency_ms:<15.0f} {cost_str:<10} {r.audio_size:<15}")
