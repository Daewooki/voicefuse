"""Configuration loading for VoiceFuse."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


ENV_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "elevenlabs": "ELEVENLABS_API_KEY",
    "google": "GOOGLE_APPLICATION_CREDENTIALS",
    "deepgram": "DEEPGRAM_API_KEY",
}


@dataclass
class VoiceFuseConfig:
    """Parsed VoiceFuse configuration."""

    providers: dict[str, dict] = field(default_factory=dict)
    default_provider: str | None = None
    default_format: str = "mp3"
    default_fallback: list[str] = field(default_factory=list)
    routing_strategy: str | None = None


def _expand_env_vars(value: str) -> str:
    """Expand ${VAR_NAME} patterns in a string."""
    def replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))
    return re.sub(r"\$\{(\w+)\}", replacer, value)


def _expand_env_recursive(obj):
    """Recursively expand environment variables in a config dict."""
    if isinstance(obj, str):
        return _expand_env_vars(obj)
    if isinstance(obj, dict):
        return {k: _expand_env_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_recursive(item) for item in obj]
    return obj


def load_config(config_path: str | None) -> VoiceFuseConfig:
    """Load VoiceFuse configuration from YAML file and/or environment variables."""
    raw: dict = {}

    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}
        raw = _expand_env_recursive(raw)

    providers = raw.get("providers", {})

    # Fill in API keys from environment if not set in YAML
    for provider_name, env_var in ENV_KEY_MAP.items():
        env_value = os.environ.get(env_var)
        if env_value:
            if provider_name not in providers:
                providers[provider_name] = {}
            if "api_key" not in providers[provider_name]:
                providers[provider_name]["api_key"] = env_value

    defaults = raw.get("defaults", {})
    routing = raw.get("routing", {})

    return VoiceFuseConfig(
        providers=providers,
        default_provider=defaults.get("provider"),
        default_format=defaults.get("output_format", "mp3"),
        default_fallback=defaults.get("fallback", []),
        routing_strategy=routing.get("strategy"),
    )
