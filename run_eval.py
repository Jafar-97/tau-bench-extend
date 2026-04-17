#!/usr/bin/env python3
"""
run_eval.py: Run tau-bench-extend evaluation on a domain.

Usage:
 python run_eval.py --domain healthcare --model gpt-4o --provider anthropic --num-tasks 10
 python run_eval.py --domain insurance --model gpt-4o --provider openai --num-tasks all
"""
import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from tau_bench_extend.core.agent_runner import run_agent_on_task
from tau_bench_extend.core.consistency_scorer import build_domain_report, print_summary, run_consistency_eval
from tau_bench_extend.core.reporter import generate_report
from tau_bench_extend.domains import get_domain

load_dotenv()
console = Console()


def parse_args():
 parser = argparse.ArgumentParser(description="tau-bench-extend: evaluate LLM agents with consistency scoring")
 parser.add_argument("--domain", required=True, choices=["healthcare", "insurance", "ecommerce"])
 parser.add_argument("--model", default="gpt-4o")
 parser.add_argument("--provider", default="openai", choices=["openai", "anthropic"])
 parser.add_argument("--num-tasks", default="10")
 parser.add_argument("--trials", type=int, default=3)
 parser.add_argument("--output-dir", default="./results")
 parser.add_argument("--no-report", action="store_true")
 return parser.parse_args()


def main():
 args = parse_args()

 if args.provider == "openai":
 api_key = os.environ.get("OPENAI_API_KEY", "")
 if not api_key:
 console.print("[red]OPENAI_API_KEY not set. Add it to .env or environment.[/red]")
 sys.exit(1)
 else:
 api_key = os.environ.get("ANTHROPIC_API_KEY", "")
 if not api_key:
 console.print("[red]ANTHROPIC_API_KEY not set. Add it to .env or environment.[/red]")
 sys.exit(1)

 domain_config = get_domain(args.domain)
 tasks = domain_config["get_tasks"]()
 tools = domain_config["get_tools"]()
 policy = domain_config["get_policy"]()

 if args.num_tasks != "all":
 tasks = tasks[:int(args.num_tasks)]

 console.print(f"\n[bold cyan]tau-bench-extend[/bold cyan]")
 console.print(f" Domain: [bold]{args.domain}[/bold]")
 console.print(f" Model: [bold]{args.model}[/bold]")
 console.print(f" Provider: {args.provider}")
 console.print(f" Tasks: {len(tasks)}")
 console.print(f" Trials: {args.trials} per task")
 console.print(f" Total: {len(tasks) * args.trials} eval runs\n")

 def run_fn(task, trial):
 return run_agent_on_task(
 task=task,
 domain_tools=tools,
 domain_policy=policy,
 model=args.model,
 provider=args.provider,
 api_key=api_key,
 trial=trial,
 )

 results = run_consistency_eval(
 tasks=tasks,
 run_fn=run_fn,
 num_trials=args.trials,
 model=args.model,
 domain=args.domain,
 )

 report = build_domain_report(
 consistency_results=results,
 domain=args.domain,
 model=args.model,
 num_trials=args.trials,
 )

 print_summary(report)

 output_dir = Path(args.output_dir)
 output_dir.mkdir(parents=True, exist_ok=True)

 results_file = output_dir / f"{args.domain}_{args.model.replace('/', '_')}_results.json"
 with open(results_file, "w") as f:
 json.dump({
 "domain": report.domain,
 "model": report.model,
 "total_tasks": report.total_tasks,
 "num_trials": report.num_trials,
 "pass_at_1": report.pass_at_1,
 "consistency_at_n": report.consistency_at_n,
 "avg_failure_turn": report.avg_failure_turn,
 "failure_breakdown": report.failure_breakdown,
 }, f, indent=2)

 console.print(f"\n[green]Results saved to {results_file}[/green]")

 if not args.no_report:
 report_file = output_dir / f"{args.domain}_{args.model.replace('/', '_')}_report.html"
 generate_report(report, str(report_file))


if __name__ == "__main__":
 main()
