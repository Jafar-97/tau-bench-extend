"""
Consistency Scorer

Sierra's research found agents succeed on <25% of tasks when
the same task is run 8 times. This module measures that:

- pass@1: does the agent succeed at least once?
- consistency@N: does the agent give the same outcome every time?
- failure pattern analysis: where does it break?
"""
from __future__ import annotations

import asyncio
import concurrent.futures
from collections import Counter
from typing import Callable

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from tau_bench_extend.core.models import (
    ConsistencyResult,
    DomainReport,
    EvalResult,
    FailureMode,
    Task,
)

console = Console()


def score_consistency(results: list[EvalResult]) -> float:
    """
    Compute consistency score for a set of trials on the same task.

    Consistency = fraction of trials that agree with the majority outcome.
    E.g. if 6/8 trials pass and 2 fail → consistency = 6/8 = 0.75
    """
    if not results:
        return 0.0
    outcomes = [r.passed for r in results]
    majority = Counter(outcomes).most_common(1)[0][1]
    return majority / len(results)


def run_consistency_eval(
    tasks: list[Task],
    run_fn: Callable[[Task, int], EvalResult],
    num_trials: int = 5,
    model: str = "",
    domain: str = "",
) -> list[ConsistencyResult]:
    """
    Run each task num_trials times and compute consistency scores.

    Args:
        tasks: List of Task objects to evaluate
        run_fn: Function(task, trial_num) -> EvalResult
        num_trials: How many times to repeat each task
        model: Model name (for reporting)
        domain: Domain name (for reporting)

    Returns:
        List of ConsistencyResult, one per task
    """
    consistency_results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        eval_task = progress.add_task(
            f"[cyan]Running {len(tasks)} tasks × {num_trials} trials...",
            total=len(tasks) * num_trials
        )

        for task in tasks:
            trial_results: list[EvalResult] = []

            for trial in range(num_trials):
                result = run_fn(task, trial)
                trial_results.append(result)
                progress.advance(eval_task)

            # Compute stats
            num_passed = sum(1 for r in trial_results if r.passed)
            pass_rate = num_passed / num_trials
            consistency = score_consistency(trial_results)

            failure_modes = [
                r.failure_mode for r in trial_results if not r.passed
            ]

            failure_turns = [
                r.failure_turn for r in trial_results
                if r.failure_turn is not None and not r.passed
            ]
            avg_failure_turn = (
                sum(failure_turns) / len(failure_turns) if failure_turns else None
            )

            consistency_results.append(ConsistencyResult(
                task_id=task.task_id,
                domain=task.domain,
                model=model,
                num_trials=num_trials,
                num_passed=num_passed,
                pass_rate=pass_rate,
                consistency_score=consistency,
                failure_modes=failure_modes,
                avg_failure_turn=avg_failure_turn,
                results=trial_results,
            ))

    return consistency_results


def build_domain_report(
    consistency_results: list[ConsistencyResult],
    domain: str,
    model: str,
    num_trials: int,
) -> DomainReport:
    """Aggregate per-task results into a domain-level report."""

    total_tasks = len(consistency_results)
    if total_tasks == 0:
        raise ValueError("No results to aggregate")

    # pass@1: fraction of tasks where agent succeeded at least once
    pass_at_1 = sum(1 for r in consistency_results if r.num_passed > 0) / total_tasks

    # consistency@N: average consistency score across all tasks
    consistency_at_n = sum(r.consistency_score for r in consistency_results) / total_tasks

    # Failure breakdown
    all_failures = [fm for r in consistency_results for fm in r.failure_modes]
    failure_breakdown = dict(Counter(f.value for f in all_failures))

    # Average failure turn
    all_failure_turns = [
        r.avg_failure_turn for r in consistency_results
        if r.avg_failure_turn is not None
    ]
    avg_failure_turn = (
        sum(all_failure_turns) / len(all_failure_turns) if all_failure_turns else 0.0
    )

    return DomainReport(
        domain=domain,
        model=model,
        total_tasks=total_tasks,
        pass_at_1=pass_at_1,
        consistency_at_n=consistency_at_n,
        num_trials=num_trials,
        failure_breakdown=failure_breakdown,
        avg_failure_turn=avg_failure_turn,
        results=consistency_results,
    )


def print_summary(report: DomainReport) -> None:
    """Pretty-print a domain report to console."""
    console.print(f"\n[bold green]━━━ Results: {report.domain.upper()} / {report.model} ━━━[/bold green]")
    console.print(f"  Tasks evaluated:     {report.total_tasks}")
    console.print(f"  Trials per task:     {report.num_trials}")
    console.print(f"  Pass@1:              [bold]{report.pass_at_1:.1%}[/bold]")
    console.print(f"  Consistency@{report.num_trials}:       [bold]{report.consistency_at_n:.1%}[/bold]")
    console.print(f"  Avg failure turn:    {report.avg_failure_turn:.1f}")

    if report.failure_breakdown:
        console.print("\n  [bold]Failure modes:[/bold]")
        total_failures = sum(report.failure_breakdown.values())
        for mode, count in sorted(report.failure_breakdown.items(), key=lambda x: -x[1]):
            pct = count / total_failures * 100
            console.print(f"    {mode:<25} {count:>4}  ({pct:.0f}%)")

    # Highlight worst tasks
    worst = sorted(report.results, key=lambda r: r.consistency_score)[:3]
    if worst:
        console.print("\n  [bold red]Least consistent tasks:[/bold red]")
        for r in worst:
            console.print(f"    Task {r.task_id:>3}: consistency={r.consistency_score:.0%}, pass_rate={r.pass_rate:.0%}")
