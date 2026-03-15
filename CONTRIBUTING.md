# Contributing to VoiceFuse

Thanks for your interest in contributing! VoiceFuse is designed to make adding new providers easy.

## Adding a New Provider

This is the most impactful contribution you can make.

### 1. Create the adapter

Create `voicefuse/providers/yourprovider.py`:

```python
from voicefuse.providers.base import BaseProvider
from voicefuse.types import AudioResponse, PricingInfo, VoiceInfo

class YourProvider(BaseProvider):
    name = "yourprovider"

    def tts(self, text, voice, output_format="mp3", **kwargs):
        # Call the provider API and return AudioResponse
        ...

    def get_voices(self):
        return [VoiceInfo(voice_id="...", name="...", provider=self.name)]

    def get_pricing(self):
        return PricingInfo(provider=self.name, cost_per_1k_chars=0.01)
```

### 2. Register it

Add to `voicefuse/providers/__init__.py`:

```python
from voicefuse.providers.yourprovider import YourProvider

PROVIDER_REGISTRY["yourprovider"] = YourProvider
```

### 3. Add voice mappings

Add entries to `voicefuse/voice_map.py` for cross-provider matching.

### 4. Add tests

Create `tests/providers/test_yourprovider.py` with mock HTTP tests using `respx`.

### 5. Update config

Add the env variable mapping to `voicefuse/config.py` `ENV_KEY_MAP`.

## Development Setup

```bash
git clone https://github.com/daewook/voicefuse.git
cd voicefuse
pip install -e ".[dev]"
pytest -v
```

## Pull Request Guidelines

- All tests must pass
- Follow existing code patterns
- One provider per PR
- Include tests with mock HTTP responses (no real API calls in tests)
