from voicefuse.providers.openai import OpenAIProvider
from voicefuse.providers.elevenlabs import ElevenLabsProvider
from voicefuse.providers.google import GoogleProvider

PROVIDER_REGISTRY: dict[str, type] = {
    "openai": OpenAIProvider,
    "elevenlabs": ElevenLabsProvider,
    "google": GoogleProvider,
}
