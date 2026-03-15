<div align="center">

# VoiceFuse

**음성 AI를 위한 LiteLLM — 하나의 API로 모든 음성 AI 프로바이더를 사용하세요.**

[![PyPI](https://img.shields.io/pypi/v/voicefuse)](https://pypi.org/project/voicefuse/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | [한국어](README.ko.md)

</div>

---

**OpenAI**, **ElevenLabs**, **Google Cloud TTS** 등 — 파라미터 하나만 바꾸면 프로바이더를 교체할 수 있습니다. 벤더 종속 없이, 자동 폴백과 프로바이더 비교 기능이 내장되어 있습니다.

## 빠른 시작

```bash
pip install voicefuse
```

```python
from voicefuse import VoiceFuse

vf = VoiceFuse()

# OpenAI로 음성 생성
audio = vf.tts("안녕하세요!", provider="openai", voice="alloy")
audio.save("output.mp3")

# ElevenLabs로 변경 — 파라미터 하나만 수정
audio = vf.tts("안녕하세요!", provider="elevenlabs", voice="Rachel")
```

## 주요 기능

### 자동 폴백
```python
# ElevenLabs 실패 시 → OpenAI → Google 순으로 자동 전환
audio = vf.tts("안녕", provider="elevenlabs", fallback=["openai", "google"])
```

### 비용 최적화 라우팅
```python
# 가장 저렴한 프로바이더 자동 선택
audio = vf.tts("안녕", strategy="cheapest")
```

### 프로바이더 비교 (A/B 테스트)
```python
results = vf.compare_tts("안녕", providers=["openai", "elevenlabs", "google"])
for r in results:
    print(f"{r.provider}: {r.latency_ms}ms, ${r.cost}, {r.audio_size} bytes")
```

## 설정

환경 변수로 API 키 설정:

```bash
export OPENAI_API_KEY=sk-...
export ELEVENLABS_API_KEY=...
export GOOGLE_API_KEY=...
```

또는 설정 파일 사용 (`voicefuse.yaml`):

```yaml
providers:
  openai:
    api_key: ${OPENAI_API_KEY}
  elevenlabs:
    api_key: ${ELEVENLABS_API_KEY}

defaults:
  provider: openai
  fallback: [elevenlabs, google]
```

## 라이선스

Apache 2.0 — [LICENSE](LICENSE) 참조
