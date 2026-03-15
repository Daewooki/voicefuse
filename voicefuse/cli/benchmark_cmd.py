"""voicefuse benchmark command - generate provider comparison report."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime

import click

from voicefuse.cli.utils import console, print_error
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


BENCHMARK_TEXTS = {
    "short": "Hello, how are you today?",
    "medium": "The quick brown fox jumps over the lazy dog. This is a sample sentence to test text-to-speech quality across different providers.",
    "long": "Artificial intelligence is transforming the way we interact with technology. Voice synthesis has made remarkable progress in recent years, with multiple providers offering near-human quality speech generation. This benchmark compares the leading providers across latency, cost, and audio quality metrics to help developers make informed decisions.",
}


@click.command()
@click.option("--output-dir", "-o", default="benchmark_results", help="Directory to save results.")
@click.option("--text", "-t", default=None, help="Custom text to benchmark (overrides default texts).")
@click.option("--json-output", "--json", "use_json", is_flag=True, default=False, help="Output as JSON only.")
@click.option("--save-audio", is_flag=True, default=False, help="Save generated audio files.")
@click.pass_context
def benchmark(ctx, output_dir, text, use_json, save_audio):
    """Run TTS benchmark across all configured providers."""
    from voicefuse import VoiceFuse
    from voicefuse.voice_map import UNIFIED_VOICES

    config_path = ctx.obj.get("config_path")

    try:
        vf = VoiceFuse(config_path=config_path)
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

    if not vf._providers:
        print_error("No providers configured. Set API keys via environment variables or voicefuse.yaml")
        sys.exit(1)

    provider_names = list(vf._providers.keys())

    if not use_json:
        console.print(Panel(
            f"[bold]VoiceFuse TTS Benchmark[/bold]\n"
            f"Providers: {', '.join(provider_names)}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            title="Benchmark",
        ))
        console.print()

    # Determine texts to benchmark
    if text:
        texts = {"custom": text}
    else:
        texts = BENCHMARK_TEXTS

    all_results = []

    for text_label, test_text in texts.items():
        if not use_json:
            console.print(f"[bold]Testing: {text_label}[/bold] ({len(test_text)} chars)")
            console.print(f"[dim]\"{test_text[:80]}{'...' if len(test_text) > 80 else ''}\"[/dim]")
            console.print()

        # Use unified voice "female-warm" for fair comparison
        results = vf.compare_tts(
            test_text,
            providers=provider_names,
            voice="female-warm",
        )

        if not results and not use_json:
            console.print("[red]All providers failed for this text.[/red]")
            console.print()
            continue

        # Build result data
        text_results = []
        for r in results:
            entry = {
                "text_label": text_label,
                "text_length": len(test_text),
                "provider": r.provider,
                "voice": r.audio.voice,
                "latency_ms": round(r.latency_ms),
                "cost": r.cost,
                "audio_size_bytes": r.audio_size,
                "format": r.audio.format,
            }
            text_results.append(entry)
            all_results.append(entry)

            # Save audio if requested
            if save_audio:
                os.makedirs(output_dir, exist_ok=True)
                audio_path = os.path.join(output_dir, f"{text_label}_{r.provider}.{r.audio.format}")
                r.audio.save(audio_path)

        if not use_json:
            _print_benchmark_table(text_results)
            console.print()

    if not all_results:
        print_error("No benchmark results. Check your API keys.")
        sys.exit(1)

    if use_json:
        report = {
            "benchmark_date": datetime.now().isoformat(),
            "providers": provider_names,
            "results": all_results,
        }
        click.echo(json.dumps(report, indent=2, ensure_ascii=False))
        return

    # Print summary
    _print_summary(all_results, provider_names)

    # Save report
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "benchmark_report.json")
    report = {
        "benchmark_date": datetime.now().isoformat(),
        "providers": provider_names,
        "results": all_results,
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Generate markdown report
    md_path = os.path.join(output_dir, "BENCHMARK.md")
    _generate_markdown_report(report, md_path)

    console.print(f"\n[bold green]Reports saved:[/bold green]")
    console.print(f"  JSON: [cyan]{report_path}[/cyan]")
    console.print(f"  Markdown: [cyan]{md_path}[/cyan]")
    if save_audio:
        console.print(f"  Audio files: [cyan]{output_dir}/[/cyan]")


def _print_benchmark_table(results: list[dict]):
    """Print benchmark results as a table."""
    table = Table(show_lines=True)
    table.add_column("Provider", style="bold")
    table.add_column("Voice")
    table.add_column("Latency", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Size", justify="right")

    # Sort by latency
    sorted_results = sorted(results, key=lambda r: r["latency_ms"])

    for i, r in enumerate(sorted_results):
        latency_style = "green" if i == 0 else ""
        cost = r.get("cost")
        cost_str = f"${cost:.4f}" if cost else "N/A"
        size = r["audio_size_bytes"]
        size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"

        table.add_row(
            r["provider"],
            r["voice"],
            f"[{latency_style}]{r['latency_ms']}ms[/{latency_style}]" if latency_style else f"{r['latency_ms']}ms",
            cost_str,
            size_str,
        )

    console.print(table)


def _print_summary(results: list[dict], providers: list[str]):
    """Print benchmark summary with winners."""
    console.print(Panel("[bold]Summary[/bold]", title="Results"))

    # Average latency per provider
    provider_stats: dict[str, dict] = {}
    for r in results:
        name = r["provider"]
        if name not in provider_stats:
            provider_stats[name] = {"latencies": [], "costs": [], "sizes": []}
        provider_stats[name]["latencies"].append(r["latency_ms"])
        if r.get("cost") is not None:
            provider_stats[name]["costs"].append(r["cost"])
        provider_stats[name]["sizes"].append(r["audio_size_bytes"])

    table = Table(title="Average Across All Tests", show_lines=True)
    table.add_column("Provider", style="bold")
    table.add_column("Avg Latency", justify="right")
    table.add_column("Avg Cost", justify="right")
    table.add_column("Avg Size", justify="right")

    for name, stats in provider_stats.items():
        avg_lat = sum(stats["latencies"]) / len(stats["latencies"])
        avg_cost = sum(stats["costs"]) / len(stats["costs"]) if stats["costs"] else None
        avg_size = sum(stats["sizes"]) / len(stats["sizes"])

        cost_str = f"${avg_cost:.4f}" if avg_cost else "N/A"
        size_str = f"{avg_size / 1024:.1f} KB"

        table.add_row(name, f"{avg_lat:.0f}ms", cost_str, size_str)

    console.print(table)

    # Winners
    if provider_stats:
        fastest = min(provider_stats, key=lambda n: sum(provider_stats[n]["latencies"]) / len(provider_stats[n]["latencies"]))
        cheapest_candidates = {n: s for n, s in provider_stats.items() if s["costs"]}
        cheapest = min(cheapest_candidates, key=lambda n: sum(cheapest_candidates[n]["costs"]) / len(cheapest_candidates[n]["costs"])) if cheapest_candidates else None

        console.print(f"\n  Fastest: [bold green]{fastest}[/bold green]")
        if cheapest:
            console.print(f"  Cheapest: [bold green]{cheapest}[/bold green]")


def _generate_markdown_report(report: dict, path: str):
    """Generate a markdown benchmark report."""
    lines = [
        "# VoiceFuse TTS Benchmark Report",
        "",
        f"**Date:** {report['benchmark_date'][:10]}",
        f"**Providers tested:** {', '.join(report['providers'])}",
        f"**Generated by:** [VoiceFuse](https://github.com/Daewooki/voicefuse) `voicefuse benchmark`",
        "",
        "---",
        "",
        "## Results",
        "",
        "| Text | Provider | Voice | Latency | Cost | Size |",
        "|------|----------|-------|---------|------|------|",
    ]

    for r in report["results"]:
        cost = f"${r['cost']:.4f}" if r.get("cost") else "N/A"
        size = f"{r['audio_size_bytes'] / 1024:.1f} KB" if r["audio_size_bytes"] >= 1024 else f"{r['audio_size_bytes']} B"
        lines.append(f"| {r['text_label']} | {r['provider']} | {r['voice']} | {r['latency_ms']}ms | {cost} | {size} |")

    # Summary
    provider_stats: dict[str, dict] = {}
    for r in report["results"]:
        name = r["provider"]
        if name not in provider_stats:
            provider_stats[name] = {"latencies": [], "costs": []}
        provider_stats[name]["latencies"].append(r["latency_ms"])
        if r.get("cost") is not None:
            provider_stats[name]["costs"].append(r["cost"])

    lines.extend([
        "",
        "## Summary",
        "",
        "| Provider | Avg Latency | Avg Cost/request |",
        "|----------|------------|------------------|",
    ])

    for name, stats in provider_stats.items():
        avg_lat = sum(stats["latencies"]) / len(stats["latencies"])
        avg_cost = sum(stats["costs"]) / len(stats["costs"]) if stats["costs"] else None
        cost_str = f"${avg_cost:.4f}" if avg_cost else "N/A"
        lines.append(f"| {name} | {avg_lat:.0f}ms | {cost_str} |")

    lines.extend([
        "",
        "---",
        "",
        "*Generated with [VoiceFuse](https://github.com/Daewooki/voicefuse) - LiteLLM for Voice*",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
