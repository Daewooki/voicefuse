import base64

from voicefuse.types import AudioResponse


def test_audio_response_creation():
    audio = AudioResponse(
        data=b"fake-audio-bytes",
        provider="openai",
        format="mp3",
        duration_ms=1500.0,
        cost=0.003,
        latency_ms=250.0,
        voice="alloy",
        fallback_used=False,
    )
    assert audio.provider == "openai"
    assert audio.data == b"fake-audio-bytes"
    assert audio.format == "mp3"
    assert audio.fallback_used is False


def test_audio_response_save(tmp_path):
    audio = AudioResponse(
        data=b"fake-audio-bytes",
        provider="openai",
        format="mp3",
        duration_ms=1000.0,
        cost=None,
        latency_ms=200.0,
        voice="alloy",
        fallback_used=False,
    )
    filepath = tmp_path / "output.mp3"
    audio.save(str(filepath))
    assert filepath.read_bytes() == b"fake-audio-bytes"


def test_audio_response_to_bytes():
    audio = AudioResponse(
        data=b"fake-audio-bytes",
        provider="openai",
        format="mp3",
        duration_ms=1000.0,
        cost=None,
        latency_ms=200.0,
        voice="alloy",
        fallback_used=False,
    )
    assert audio.to_bytes() == b"fake-audio-bytes"


def test_audio_response_to_base64():
    audio = AudioResponse(
        data=b"fake-audio-bytes",
        provider="openai",
        format="mp3",
        duration_ms=1000.0,
        cost=None,
        latency_ms=200.0,
        voice="alloy",
        fallback_used=False,
    )
    expected = base64.b64encode(b"fake-audio-bytes").decode("utf-8")
    assert audio.to_base64() == expected
