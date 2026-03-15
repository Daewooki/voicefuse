"""Tests for voicefuse providers CLI command."""

import json

from click.testing import CliRunner

from voicefuse.cli.main import cli


def test_providers_shows_status(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["providers"])
    assert result.exit_code == 0
    assert "openai" in result.output
    assert "elevenlabs" in result.output
    assert "google" in result.output


def test_providers_json_output(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["providers", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    openai_entry = next(p for p in data if p["name"] == "openai")
    assert openai_entry["configured"] is True
