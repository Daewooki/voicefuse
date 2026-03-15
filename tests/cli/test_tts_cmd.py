"""Tests for voicefuse tts CLI command."""

import json

import httpx
import respx
from click.testing import CliRunner

from voicefuse.cli.main import cli


@respx.mock
def test_tts_saves_to_file(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"fake-audio-data")
    )
    output_path = str(tmp_path / "output.mp3")
    runner = CliRunner()
    result = runner.invoke(cli, ["tts", "Hello", "-p", "openai", "-v", "alloy", "-o", output_path])
    assert result.exit_code == 0
    assert (tmp_path / "output.mp3").read_bytes() == b"fake-audio-data"


@respx.mock
def test_tts_json_output(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"fake-audio")
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["tts", "Hello", "-p", "openai", "-v", "alloy", "--json", "--no-play"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["provider"] == "openai"
    assert data["voice"] == "alloy"
    assert "latency_ms" in data


@respx.mock
def test_tts_no_play_saves_to_temp(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"audio")
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["tts", "Hello", "-p", "openai", "-v", "alloy", "--no-play"])
    assert result.exit_code == 0
    assert "openai" in result.output


def test_tts_no_provider_no_config(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["tts", "Hello"])
    assert result.exit_code == 1


@respx.mock
def test_tts_with_strategy(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"audio")
    )
    respx.post("https://api.elevenlabs.io/v1/text-to-speech/Rachel").mock(
        return_value=httpx.Response(200, content=b"audio")
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["tts", "Hello", "--strategy", "cheapest", "-v", "alloy", "--no-play"])
    assert result.exit_code == 0
