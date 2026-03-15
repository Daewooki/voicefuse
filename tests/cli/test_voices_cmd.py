"""Tests for voicefuse voices CLI command."""

import json

from click.testing import CliRunner

from voicefuse.cli.main import cli


def test_voices_for_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    runner = CliRunner()
    result = runner.invoke(cli, ["voices", "-p", "openai"])
    assert result.exit_code == 0
    assert "alloy" in result.output
    assert "Alloy" in result.output


def test_voices_json_output(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    runner = CliRunner()
    result = runner.invoke(cli, ["voices", "-p", "openai", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert any(v["voice_id"] == "alloy" for v in data)


def test_voices_unknown_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    runner = CliRunner()
    result = runner.invoke(cli, ["voices", "-p", "nonexistent"])
    assert result.exit_code == 1
    assert "Unknown provider" in result.output
