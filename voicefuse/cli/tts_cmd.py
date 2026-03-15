"""voicefuse tts command."""

from __future__ import annotations

import json
import sys

import click

from voicefuse.cli.utils import console, play_audio, print_error, print_tts_result


@click.command()
@click.argument("text")
@click.option("--provider", "-p", default=None, help="Voice AI provider (openai, elevenlabs, google).")
@click.option("--voice", "-v", default="", help="Voice name/ID to use.")
@click.option("--output", "-o", default=None, help="Save audio to file instead of playing.")
@click.option("--format", "-f", "output_format", default="mp3", help="Audio format (mp3, wav, pcm).")
@click.option("--strategy", default=None, help="Routing strategy (cheapest, best_quality).")
@click.option("--fallback", default=None, help="Comma-separated fallback providers.")
@click.option("--no-play", is_flag=True, default=False, help="Don't play audio (save to temp file).")
@click.option("--json-output", "--json", "use_json", is_flag=True, default=False, help="Output as JSON.")
@click.pass_context
def tts(ctx, text, provider, voice, output, output_format, strategy, fallback, no_play, use_json):
    """Generate speech from text."""
    from voicefuse import VoiceFuse
    from voicefuse.exceptions import VoiceFuseError

    config_path = ctx.obj.get("config_path")

    try:
        vf = VoiceFuse(config_path=config_path)
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

    fallback_list = fallback.split(",") if fallback else None

    try:
        audio = vf.tts(
            text,
            provider=provider,
            voice=voice,
            output_format=output_format,
            strategy=strategy,
            fallback=fallback_list,
        )
    except VoiceFuseError as e:
        print_error(str(e))
        sys.exit(1)

    if use_json:
        result = {
            "provider": audio.provider,
            "voice": audio.voice,
            "latency_ms": round(audio.latency_ms),
            "cost": audio.cost,
            "size_bytes": len(audio.data),
            "format": audio.format,
            "fallback_used": audio.fallback_used,
        }
        if output:
            audio.save(output)
            result["file"] = output
        click.echo(json.dumps(result, ensure_ascii=False))
        return

    if output:
        audio.save(output)
        print_tts_result(
            provider=audio.provider,
            voice=audio.voice,
            latency_ms=audio.latency_ms,
            cost=audio.cost,
            size_bytes=len(audio.data),
            file_path=output,
        )
        return

    # Play audio
    if not no_play:
        print_tts_result(
            provider=audio.provider,
            voice=audio.voice,
            latency_ms=audio.latency_ms,
            cost=audio.cost,
            size_bytes=len(audio.data),
        )
        console.print("[dim]▶ Playing audio...[/dim]")
        if not play_audio(audio.data, audio.format):
            # Playback failed — save to temp file
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=f".{audio.format}", delete=False)
            tmp.write(audio.data)
            tmp.close()
            console.print(f"  Audio saved to [cyan]{tmp.name}[/cyan]")
    else:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=f".{audio.format}", delete=False)
        tmp.write(audio.data)
        tmp.close()
        print_tts_result(
            provider=audio.provider,
            voice=audio.voice,
            latency_ms=audio.latency_ms,
            cost=audio.cost,
            size_bytes=len(audio.data),
            file_path=tmp.name,
        )
