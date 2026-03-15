<div align="center">

# VoiceFuse

**LiteLLM for Voice -- One API for every Voice AI provider.**

[![CI](https://github.com/daewook/voicefuse/actions/workflows/ci.yml/badge.svg)](https://github.com/daewook/voicefuse/actions)
[![PyPI](https://img.shields.io/pypi/v/voicefuse)](https://pypi.org/project/voicefuse/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | [Korean](README.ko.md)

Switch between **OpenAI**, **ElevenLabs**, **Google Cloud TTS**, and more --<br/>
by changing **one parameter**. No vendor lock-in. Automatic fallback. Built-in benchmarks.

</div>

---

## Why VoiceFuse?

Every voice AI provider has a different API, different SDKs, different audio formats. Switching providers means rewriting code. Comparing them means maintaining parallel integrations.

VoiceFuse fixes this:

```python
from voicefuse import VoiceFuse
vf = VoiceFuse()

audio = vf.tts("Hello world!", provider="openai", voice="alloy")

# Switch provider -- change one parameter. Voice is auto-mapped.
audio = vf.tts("Hello world!", provider="elevenlabs", voice="alloy")
# alloy (OpenAI) -> automatically mapped to Rachel (ElevenLabs)
```

## Install

```bash
pip install voicefuse

# With audio playback support:
pip install voicefuse[play]
```

## Quick Start

### Python SDK

```python
from voicefuse import VoiceFuse

vf = VoiceFuse()

# Basic TTS
audio = vf.tts("Hello!", provider="openai", voice="alloy")
audio.save("output.mp3")

# Auto fallback -- if primary fails, tries next
audio = vf.tts("Hello!", provider="elevenlabs", fallback=["openai", "google"])

# Cost-optimized -- picks cheapest provider
audio = vf.tts("Hello!", strategy="cheapest")

# Cross-provider voice -- use unified names
audio = vf.tts("Hello!", provider="openai", voice="female-warm")
audio = vf.tts("Hello!", provider="google", voice="female-warm")
# Both map to the best matching voice for each provider
```

### CLI

```bash
# Generate and play speech
voicefuse tts "Hello world" -p openai -v alloy

# Save to file
voicefuse tts "Hello world" -p openai -v alloy -o output.mp3

# Compare providers side-by-side
voicefuse compare "Hello world" -p openai,elevenlabs,google

# Find matching voices across providers
voicefuse voices --match alloy

# Run full benchmark
voicefuse benchmark

# Check provider status
voicefuse providers
```

### Provider Comparison

```bash
$ voicefuse compare "Hello world" -p openai,elevenlabs,google

  Provider Comparison
+------------+-------+---------+--------+--------+
| Provider   | Voice | Latency | Cost   | Size   |
+------------+-------+---------+--------+--------+
| google     | ...   | 180ms   | $0.0001| 9.8 KB |
| openai     | alloy | 340ms   | $0.0002| 12.4KB |
| elevenlabs | Rachel| 520ms   | $0.0003| 15.1KB |
+------------+-------+---------+--------+--------+
```

## Cross-Provider Voice Matching

Use any voice name with any provider. VoiceFuse automatically maps to the closest match:

```python
# "alloy" is an OpenAI voice, but works with any provider
audio = vf.tts("Hello", provider="elevenlabs", voice="alloy")
# -> maps to ElevenLabs "Rachel" (most similar)

# Or use universal voice names
audio = vf.tts("Hello", provider="openai", voice="female-warm")   # -> nova
audio = vf.tts("Hello", provider="elevenlabs", voice="female-warm") # -> Rachel
audio = vf.tts("Hello", provider="google", voice="female-warm")    # -> en-US-Neural2-C
```

Available unified voices: `female-warm`, `female-bright`, `female-calm`, `male-deep`, `male-warm`, `male-narrative`

## Configuration

Set API keys via environment variables:

```bash
export OPENAI_API_KEY=sk-...
export ELEVENLABS_API_KEY=...
export GOOGLE_API_KEY=...
```

Or use `voicefuse.yaml`:

```yaml
providers:
  openai:
    api_key: ${OPENAI_API_KEY}
  elevenlabs:
    api_key: ${ELEVENLABS_API_KEY}

defaults:
  provider: openai
  fallback: [elevenlabs, google]
```

## Supported Providers

| Provider | TTS | STT | Voice Cloning | Status |
|----------|-----|-----|---------------|--------|
| OpenAI | Yes | Soon | -- | Available |
| ElevenLabs | Yes | -- | Soon | Available |
| Google Cloud | Yes | Soon | -- | Available |
| Deepgram | -- | Soon | -- | Coming Soon |
| Azure | Soon | Soon | -- | Coming Soon |
| AWS Polly | Soon | -- | -- | Coming Soon |

## Contributing

Adding a provider is easy. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
git clone https://github.com/daewook/voicefuse.git
cd voicefuse
pip install -e ".[dev]"
pytest -v  # 70+ tests
```

## License

Apache 2.0 -- see [LICENSE](LICENSE)
