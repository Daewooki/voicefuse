"""voicefuse voices command."""

from __future__ import annotations

import json
import sys

import click

from voicefuse.cli.utils import console, print_error, print_voices_table
from rich.table import Table


@click.command()
@click.option("--provider", "-p", default=None, help="Show voices for a specific provider.")
@click.option("--match", "-m", default=None, help="Show cross-provider matches for a voice.")
@click.option("--json-output", "--json", "use_json", is_flag=True, default=False, help="Output as JSON.")
@click.pass_context
def voices(ctx, provider, match, use_json):
    """List available voices or find cross-provider matches."""
    if match:
        _show_voice_matches(match, use_json)
        return

    from voicefuse import VoiceFuse

    config_path = ctx.obj.get("config_path")

    try:
        vf = VoiceFuse(config_path=config_path)
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

    all_voices = []

    if provider:
        if provider not in vf._providers:
            print_error(f"Unknown provider '{provider}'. Available: {', '.join(vf._providers.keys())}")
            sys.exit(1)
        p = vf._providers[provider]
        for v in p.get_voices():
            all_voices.append({
                "voice_id": v.voice_id,
                "name": v.name,
                "provider": v.provider,
                "language": v.language,
                "gender": v.gender,
            })
    else:
        for name, p in vf._providers.items():
            for v in p.get_voices():
                all_voices.append({
                    "voice_id": v.voice_id,
                    "name": v.name,
                    "provider": v.provider,
                    "language": v.language,
                    "gender": v.gender,
                })

    if not all_voices:
        print_error("No voices found. Check your provider configuration.")
        sys.exit(1)

    if use_json:
        click.echo(json.dumps(all_voices, ensure_ascii=False))
        return

    print_voices_table(all_voices)


def _show_voice_matches(voice_name: str, use_json: bool):
    """Show cross-provider matches for a voice."""
    from voicefuse.voice_map import get_voice_matches, UNIFIED_VOICES

    matches = get_voice_matches(voice_name)

    if not matches:
        # Check if it's a known unified voice category
        print_error(f"No matches found for '{voice_name}'.")
        console.print("\n[dim]Available unified voices: " + ", ".join(UNIFIED_VOICES.keys()) + "[/dim]")
        sys.exit(1)

    if use_json:
        data = [
            {
                "provider": m.provider,
                "voice": m.voice,
                "match_type": m.match_type,
            }
            for m in matches
        ]
        click.echo(json.dumps(data, ensure_ascii=False))
        return

    table = Table(title=f"Voice Matches for '{voice_name}'", show_lines=True)
    table.add_column("Provider", style="bold")
    table.add_column("Voice")
    table.add_column("Match Type")

    for m in matches:
        match_style = {
            "exact": "[green]exact[/green]",
            "mapped": "[yellow]similar[/yellow]",
            "unified": "[cyan]unified[/cyan]",
        }.get(m.match_type, m.match_type)
        table.add_row(m.provider, m.voice, match_style)

    console.print(table)
