"""Tests for voicefuse benchmark CLI command."""

import json
import os

import httpx
import respx
from click.testing import CliRunner

from voicefuse.cli.main import cli


@respx.mock
def test_benchmark_json_output(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"fake-audio-benchmark")
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["benchmark", "--json", "-t", "Hello benchmark"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "results" in data
    assert "benchmark_date" in data
    assert len(data["results"]) >= 1


@respx.mock
def test_benchmark_saves_report(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"audio-data")
    )
    output_dir = str(tmp_path / "bench")
    runner = CliRunner()
    result = runner.invoke(cli, ["benchmark", "-t", "Test text", "-o", output_dir])
    assert result.exit_code == 0
    assert os.path.exists(os.path.join(output_dir, "benchmark_report.json"))
    assert os.path.exists(os.path.join(output_dir, "BENCHMARK.md"))


@respx.mock
def test_benchmark_saves_audio(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    respx.post("https://api.openai.com/v1/audio/speech").mock(
        return_value=httpx.Response(200, content=b"audio-content")
    )
    output_dir = str(tmp_path / "bench")
    runner = CliRunner()
    result = runner.invoke(cli, ["benchmark", "-t", "Hello", "-o", output_dir, "--save-audio"])
    assert result.exit_code == 0
    audio_files = [f for f in os.listdir(output_dir) if f.endswith(".mp3")]
    assert len(audio_files) >= 1


def test_benchmark_no_providers(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["benchmark", "-t", "Hello"])
    assert result.exit_code == 1
