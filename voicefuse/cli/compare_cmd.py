"""voicefuse compare command."""

from __future__ import annotations

import json
import sys

import click

from voicefuse.cli.utils import console, play_audio, print_compare_table, print_error


@click.command()
@click.argument("text")
@click.option("--providers", "-p", required=True, help="Comma-separated list of providers to compare.")
@click.option("--voice", "-v", default="", help="Voice name/ID.")
@click.option("--format", "-f", "output_format", default="mp3", help="Audio format.")
@click.option("--play", "play_after", is_flag=True, default=False, help="Play a selected result after comparison.")
@click.option("--json-output", "--json", "use_json", is_flag=True, default=False, help="Output as JSON.")
@click.pass_context
def compare(ctx, text, providers, voice, output_format, play_after, use_json):
    """Compare TTS output from multiple providers."""
    from voicefuse import VoiceFuse
    from voicefuse.exceptions import VoiceFuseError

    config_path = ctx.obj.get("config_path")
    provider_list = [p.strip() for p in providers.split(",")]

    try:
        vf = VoiceFuse(config_path=config_path)
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

    try:
        results = vf.compare_tts(
            text,
            providers=provider_list,
            voice=voice,
            output_format=output_format,
        )
    except VoiceFuseError as e:
        print_error(str(e))
        sys.exit(1)

    if not results:
        print_error("All providers failed. Check your API keys and configuration.")
        sys.exit(1)

    if use_json:
        json_results = [
            {
                "provider": r.provider,
                "latency_ms": round(r.latency_ms),
                "cost": r.cost,
                "audio_size": r.audio_size,
            }
            for r in results
        ]
        click.echo(json.dumps(json_results, ensure_ascii=False))
        return

    table_data = [
        {
            "provider": r.provider,
            "voice": r.audio.voice,
            "latency_ms": r.latency_ms,
            "cost": r.cost,
            "size_bytes": r.audio_size,
        }
        for r in results
    ]
    print_compare_table(table_data)

    if play_after and results:
        console.print()
        for i, r in enumerate(results):
            console.print(f"  [{i + 1}] {r.provider}")
        console.print()

        choice = click.prompt("Play which provider?", type=int, default=1)
        if 1 <= choice <= len(results):
            selected = results[choice - 1]
            console.print(f"[dim]▶ Playing {selected.provider}...[/dim]")
            play_audio(selected.audio.data, selected.audio.format)
        else:
            print_error(f"Invalid choice: {choice}")
