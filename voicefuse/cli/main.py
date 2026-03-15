"""VoiceFuse CLI — main entry point."""

from __future__ import annotations

import click

from voicefuse import __version__
from voicefuse.cli.tts_cmd import tts
from voicefuse.cli.compare_cmd import compare
from voicefuse.cli.voices_cmd import voices
from voicefuse.cli.providers_cmd import providers
from voicefuse.cli.benchmark_cmd import benchmark


@click.group()
@click.version_option(version=__version__, prog_name="voicefuse")
@click.option("--config", "-c", default=None, help="Path to voicefuse.yaml config file.")
@click.option("--no-color", is_flag=True, default=False, help="Disable colored output.")
@click.pass_context
def cli(ctx, config, no_color):
    """VoiceFuse - LiteLLM for Voice. One API for every Voice AI provider."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["no_color"] = no_color


cli.add_command(tts)
cli.add_command(compare)
cli.add_command(voices)
cli.add_command(providers)
cli.add_command(benchmark)


if __name__ == "__main__":
    cli()
