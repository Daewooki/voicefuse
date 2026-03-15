"""Tests for voicefuse compare CLI command."""

import json

import httpx
import respx
from click.testing import CliRunner

from voicefuse.cli.main import cli


@respx.mock
def test_compare_displays_table(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"openai-audio")
    )
    respx.post("https://api.elevenlabs.io/v1/text-to-speech/").mock(
        return_value=httpx.Response(200, content=b"elevenlabs-audio")
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "Hello", "-p", "openai,elevenlabs", "-v", "alloy"])
    assert result.exit_code == 0
    assert "Provider" in result.output


@respx.mock
def test_compare_json_output(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"audio")
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "Hello", "-p", "openai", "-v", "alloy", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["provider"] == "openai"


def test_compare_all_fail(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "Hello", "-p", "openai,elevenlabs"])
    assert result.exit_code == 1
