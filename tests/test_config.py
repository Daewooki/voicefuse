from voicefuse.config import load_config


def test_load_config_from_yaml(tmp_path):
    config_file = tmp_path / "voicefuse.yaml"
    config_file.write_text("""
providers:
  openai:
    api_key: sk-test-123
    default_voice: alloy
  elevenlabs:
    api_key: el-test-456
    default_voice: Rachel

defaults:
  provider: openai
  output_format: mp3
  fallback:
    - elevenlabs
""")
    config = load_config(str(config_file))
    assert config.default_provider == "openai"
    assert config.default_format == "mp3"
    assert config.default_fallback == ["elevenlabs"]
    assert config.providers["openai"]["api_key"] == "sk-test-123"
    assert config.providers["elevenlabs"]["default_voice"] == "Rachel"


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-env-key")
    config = load_config(None)
    assert config.providers["openai"]["api_key"] == "sk-env-key"
    assert config.providers["elevenlabs"]["api_key"] == "el-env-key"


def test_yaml_env_variable_expansion(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_OPENAI_KEY", "sk-expanded-123")
    config_file = tmp_path / "voicefuse.yaml"
    config_file.write_text("""
providers:
  openai:
    api_key: ${MY_OPENAI_KEY}

defaults:
  provider: openai
  output_format: mp3
""")
    config = load_config(str(config_file))
    assert config.providers["openai"]["api_key"] == "sk-expanded-123"


def test_empty_config_returns_defaults():
    config = load_config(None)
    assert config.default_provider is None
    assert config.default_format == "mp3"
    assert config.default_fallback == []
