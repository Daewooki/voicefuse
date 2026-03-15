"""CLI utility functions - tables, audio playback, formatting."""

from __future__ import annotations

import os
import sys
import tempfile

from rich.console import Console
from rich.table import Table

# Force UTF-8 on Windows to avoid cp949 encoding errors
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)
error_console = Console(stderr=True, force_terminal=True)


def play_audio(audio_data: bytes, fmt: str = "mp3") -> bool:
    """Play audio data. Returns True if playback succeeded."""
    try:
        from playsound3 import playsound
    except ImportError:
        error_console.print(
            "[yellow]Audio playback requires 'playsound3'.[/yellow]\n"
            "Install with: [bold]pip install voicefuse\\[play][/bold]"
        )
        return False

    with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as f:
        f.write(audio_data)
        tmp_path = f.name

    try:
        playsound(tmp_path)
        return True
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def format_cost(cost: float | None) -> str:
    """Format cost as dollar string."""
    if cost is None:
        return "N/A"
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    return f"{size_bytes / 1024:.1f} KB"


def mask_api_key(key: str) -> str:
    """Mask API key for display: sk-...4f2a"""
    if len(key) <= 8:
        return "***"
    return f"{key[:3]}...{key[-4:]}"


def print_tts_result(provider: str, voice: str, latency_ms: float, cost: float | None, size_bytes: int, file_path: str | None = None):
    """Print TTS result summary."""
    parts = [
        "[bold green][OK][/bold green]",
        f"[bold]{provider}[/bold]/{voice}",
        f"{latency_ms:.0f}ms",
        format_cost(cost),
        format_size(size_bytes),
    ]
    if file_path:
        parts.append(f"-> [cyan]{file_path}[/cyan]")
    console.print("  ".join(parts))


def print_compare_table(results: list[dict]):
    """Print a rich comparison table."""
    table = Table(title="Provider Comparison", show_lines=True)
    table.add_column("Provider", style="bold")
    table.add_column("Voice")
    table.add_column("Latency", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Size", justify="right")

    for r in results:
        table.add_row(
            r["provider"],
            r["voice"],
            f"{r['latency_ms']:.0f}ms",
            format_cost(r.get("cost")),
            format_size(r["size_bytes"]),
        )

    console.print(table)


def print_voices_table(voices: list[dict]):
    """Print voices table."""
    table = Table(title="Available Voices", show_lines=True)
    table.add_column("Voice ID", style="bold")
    table.add_column("Name")
    table.add_column("Provider")
    table.add_column("Language")
    table.add_column("Gender")

    for v in voices:
        table.add_row(
            v.get("voice_id", ""),
            v.get("name", ""),
            v.get("provider", ""),
            v.get("language") or "-",
            v.get("gender") or "-",
        )

    console.print(table)


def print_providers_table(providers: list[dict]):
    """Print providers status table."""
    table = Table(title="Configured Providers", show_lines=True)
    table.add_column("Provider", style="bold")
    table.add_column("Status")
    table.add_column("API Key")

    for p in providers:
        status = "[green]OK[/green]" if p["configured"] else "[red]None[/red]"
        key_display = mask_api_key(p["api_key"]) if p["api_key"] else "-"
        table.add_row(p["name"], status, key_display)

    console.print(table)


def print_error(message: str):
    """Print error message."""
    error_console.print(f"[bold red]Error:[/bold red] {message}")
