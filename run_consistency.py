#!/usr/bin/env python3
"""
run_consistency.py: Run consistency scoring on a single task.

Usage:
    python run_consistency.py --domain healthcare --task-id 11 --model gpt-4o --trials 8
"""
import argparse
import os
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from tau_bench_extend.core.agent_runner import run_agent_on_task
from tau_bench_extend.core.consistency_scorer import score_consistency
from tau_bench_extend.domains import get_domain

load_dotenv()
console = Console()


def parse_args():
    parser = argparse.ArgumentParser(description="Consistency scoring for a single task")
    parser.add_argument("--domain", required=True, choices=["healthcare", "insurance", "ecommerce"])
    parser.add_argument("--task-id", type=int, required=True)
    parser.add_argument("--model", default="gpt-4o")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic"])
    parser.add_argument("--trials", type=int, default=8)
    return parser.parse_args()


def main():
    args = parse_args()

    api_key = os.environ.get(
        "OPENAI_API_KEY" if args.provider == "openai" else "ANTHROPIC_API_KEY", ""
    )
    if not api_key:
        console.print("[red]API key not set.[/red]")
        sys.exit(1)

    domain_config = get_domain(args.domain)
    tasks = domain_config["get_tasks"]()
    tools = domain_config["get_tools"]()
    policy = domain_config["get_policy"]()

    task = next((t for t in tasks if t.task_id == args.task_id), None)
    if not task:
        console.print(f"[red]Task {args.task_id} not found in domain {args.domain}[/red]")
        sys.exit(1)

    console.print(f"\n[bold cyan]Consistency Eval[/bold cyan]")
    console.print(f"  Task {args.task_id}: [italic]{task.instruction[:80]}...[/italic]")
    console.print(f"  Model: {args.model}  |  Trials: {args.trials}\n")

    results = []
    for trial in range(args.trials):
        console.print(f"  Running trial {trial + 1}/{args.trials}...", end=" ")
        result = run_agent_on_task(
            task=task, domain_tools=tools, domain_policy=policy,
            model=args.model, provider=args.provider, api_key=api_key, trial=trial,
        )
        results.append(result)
        status = "[green]PASS[/green]" if result.passed else f"[red]FAIL ({result.failure_mode.value})[/red]"
        console.print(status)

    consistency = score_consistency(results)
    pass_rate = sum(1 for r in results if r.passed) / len(results)

    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"  Pass rate:        {pass_rate:.0%} ({sum(r.passed for r in results)}/{args.trials})")
    console.print(f"  Consistency@{args.trials}:   {consistency:.0%}")

    table = Table(title="Trial Breakdown", show_header=True)
    table.add_column("Trial", style="dim")
    table.add_column("Outcome")
    table.add_column("Failure Mode")
    table.add_column("Turns")
    table.add_column("Latency")

    for i, r in enumerate(results):
        outcome = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        failure = r.failure_mode.value if not r.passed else "none"
        table.add_row(str(i + 1), outcome, failure, str(len(r.turns)), f"{r.latency_ms:.0f}ms")

    console.print(table)

    if consistency < 0.5:
        console.print(f"\n[bold red]Low consistency ({consistency:.0%}) - this task is highly unreliable.[/bold red]")
    elif consistency < 0.75:
        console.print(f"\n[bold yellow]Moderate consistency ({consistency:.0%}) - needs improvement.[/bold yellow]")
    else:
        console.print(f"\n[bold green]Good consistency ({consistency:.0%})[/bold green]")


if __name__ == "__main__":
    main()
