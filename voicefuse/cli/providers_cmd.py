"""voicefuse providers command."""

from __future__ import annotations

import json
import sys

import click

from voicefuse.cli.utils import print_error, print_providers_table
from voicefuse.config import ENV_KEY_MAP


@click.command()
@click.option("--json-output", "--json", "use_json", is_flag=True, default=False, help="Output as JSON.")
@click.pass_context
def providers(ctx, use_json):
    """Show configured providers and their status."""
    import os

    from voicefuse.providers import PROVIDER_REGISTRY

    config_path = ctx.obj.get("config_path")

    # Try to load config
    from voicefuse.config import load_config
    config = load_config(config_path)

    provider_info = []
    for name in PROVIDER_REGISTRY:
        settings = config.providers.get(name, {})
        api_key = settings.get("api_key", "")

        # Also check environment
        if not api_key:
            env_var = ENV_KEY_MAP.get(name, "")
            api_key = os.environ.get(env_var, "")

        provider_info.append({
            "name": name,
            "configured": bool(api_key),
            "api_key": api_key,
        })

    if use_json:
        safe_info = [
            {"name": p["name"], "configured": p["configured"]}
            for p in provider_info
        ]
        click.echo(json.dumps(safe_info, ensure_ascii=False))
        return

    print_providers_table(provider_info)
