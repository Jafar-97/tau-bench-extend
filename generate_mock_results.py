#!/usr/bin/env python3
"""
generate_mock_results.py - Generates realistic mock eval results without needing an API key.
Run: python generate_mock_results.py
"""
import json
import random
from pathlib import Path

from tau_bench_extend.core.models import (
    ConsistencyResult, DomainReport, EvalResult, FailureMode, TaskDifficulty, Turn,
)
from tau_bench_extend.core.reporter import generate_report
from tau_bench_extend.core.consistency_scorer import print_summary
from tau_bench_extend.domains.healthcare.tasks import HEALTHCARE_TASKS
from tau_bench_extend.domains.insurance.tasks import INSURANCE_TASKS
from tau_bench_extend.domains.ecommerce.tasks import ECOMMERCE_TASKS

random.seed(42)

PASS_RATES = {
    TaskDifficulty.EASY: 0.82,
    TaskDifficulty.MEDIUM: 0.61,
    TaskDifficulty.HARD: 0.38,
    TaskDifficulty.ADVERSARIAL: 0.44,
}

FAILURE_DIST = {
    TaskDifficulty.EASY: [FailureMode.INCOMPLETE_ACTION, FailureMode.WRONG_TOOL_CALL],
    TaskDifficulty.MEDIUM: [FailureMode.WRONG_TOOL_CALL, FailureMode.POLICY_VIOLATION, FailureMode.INCOMPLETE_ACTION],
    TaskDifficulty.HARD: [FailureMode.CONTEXT_LOSS, FailureMode.HALLUCINATION, FailureMode.POLICY_VIOLATION, FailureMode.WRONG_TOOL_CALL],
    TaskDifficulty.ADVERSARIAL: [FailureMode.HALLUCINATION, FailureMode.BRAND_SAFETY, FailureMode.POLICY_VIOLATION],
}

CONSISTENCY_PENALTY = 0.15


def mock_eval_result(task, trial: int, passed: bool) -> EvalResult:
    num_turns = random.randint(2, 10) if not passed else random.randint(3, 7)
    failure_mode = FailureMode.CORRECT
    failure_turn = None

    if not passed:
        failure_mode = random.choice(FAILURE_DIST.get(task.difficulty, [FailureMode.INCOMPLETE_ACTION]))
        failure_turn = random.randint(1, max(1, num_turns - 1))

    turns = [Turn(role="user", content=task.instruction)]
    for i in range(num_turns - 1):
        turns.append(Turn(role="agent", content=f"[Mock turn {i+1}]"))

    return EvalResult(
        task_id=task.task_id,
        domain=task.domain,
        trial=trial,
        passed=passed,
        turns=turns,
        failure_mode=failure_mode,
        failure_turn=failure_turn,
        model="gpt-4o",
        latency_ms=random.uniform(800, 3200),
        total_tokens=random.randint(400, 2000),
    )


def mock_consistency_result(task, num_trials: int = 5) -> ConsistencyResult:
    base_pass_rate = PASS_RATES[task.difficulty]
    task_pass_rate = min(1.0, max(0.0, base_pass_rate + random.gauss(0, 0.12)))

    trial_results = []
    for trial in range(num_trials):
        passed = random.random() < task_pass_rate
        trial_results.append(mock_eval_result(task, trial, passed))

    num_passed = sum(1 for r in trial_results if r.passed)
    pass_rate = num_passed / num_trials
    consistency_score = min(1.0, max(0.0, pass_rate - random.uniform(0, CONSISTENCY_PENALTY)))
    failure_modes = [r.failure_mode for r in trial_results if not r.passed]
    failure_turns = [r.failure_turn for r in trial_results if r.failure_turn is not None and not r.passed]
    avg_failure_turn = sum(failure_turns) / len(failure_turns) if failure_turns else None

    return ConsistencyResult(
        task_id=task.task_id,
        domain=task.domain,
        model="gpt-4o",
        num_trials=num_trials,
        num_passed=num_passed,
        pass_rate=pass_rate,
        consistency_score=consistency_score,
        failure_modes=failure_modes,
        avg_failure_turn=avg_failure_turn,
        results=trial_results,
    )


def generate_domain_report(tasks, domain: str, num_trials: int = 5) -> DomainReport:
    from collections import Counter
    results = [mock_consistency_result(t, num_trials) for t in tasks]
    total_tasks = len(results)
    pass_at_1 = sum(1 for r in results if r.num_passed > 0) / total_tasks
    consistency_at_n = sum(r.consistency_score for r in results) / total_tasks
    all_failures = [fm for r in results for fm in r.failure_modes]
    failure_breakdown = dict(Counter(f.value for f in all_failures))
    all_failure_turns = [r.avg_failure_turn for r in results if r.avg_failure_turn is not None]
    avg_failure_turn = sum(all_failure_turns) / len(all_failure_turns) if all_failure_turns else 0.0
    return DomainReport(
        domain=domain, model="gpt-4o", total_tasks=total_tasks,
        pass_at_1=pass_at_1, consistency_at_n=consistency_at_n,
        num_trials=num_trials, failure_breakdown=failure_breakdown,
        avg_failure_turn=avg_failure_turn, results=results,
    )


if __name__ == "__main__":
    Path("results").mkdir(exist_ok=True)
    domains = [
        ("healthcare", HEALTHCARE_TASKS),
        ("insurance", INSURANCE_TASKS),
        ("ecommerce", ECOMMERCE_TASKS),
    ]
    for domain_name, tasks in domains:
        print(f"\nGenerating: {domain_name} ({len(tasks)} tasks)...")
        report = generate_domain_report(tasks, domain_name, num_trials=5)
        print_summary(report)
        with open(f"results/{domain_name}_gpt-4o_results.json", "w") as f:
            json.dump({
                "domain": report.domain, "model": report.model,
                "total_tasks": report.total_tasks, "num_trials": report.num_trials,
                "pass_at_1": round(report.pass_at_1, 4),
                "consistency_at_n": round(report.consistency_at_n, 4),
                "avg_failure_turn": round(report.avg_failure_turn, 2),
                "failure_breakdown": report.failure_breakdown,
            }, f, indent=2)
        generate_report(report, f"results/{domain_name}_gpt-4o_report.html")
    print("\nAll results saved to ./results/")
