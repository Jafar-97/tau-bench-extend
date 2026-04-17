"""
Core data models for tau-bench-extend.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADVERSARIAL = "adversarial"


class FailureMode(str, Enum):
    POLICY_VIOLATION = "policy_violation"
    HALLUCINATION = "hallucination"
    CONTEXT_LOSS = "context_loss"
    WRONG_TOOL_CALL = "wrong_tool_call"
    INCOMPLETE_ACTION = "incomplete_action"
    BRAND_SAFETY = "brand_safety"
    CORRECT = "correct"


@dataclass
class Task:
    """A single evaluation task."""
    task_id: int
    domain: str
    instruction: str                   # What the user wants to accomplish
    expected_actions: list[dict]       # Ground-truth tool calls / state changes
    difficulty: TaskDifficulty = TaskDifficulty.MEDIUM
    tags: list[str] = field(default_factory=list)
    adversarial_type: Optional[str] = None   # e.g. "policy_boundary", "hallucination_bait"


@dataclass
class Turn:
    """A single conversation turn."""
    role: str   # "user" | "agent" | "tool"
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)


@dataclass
class EvalResult:
    """Result of running one task once."""
    task_id: int
    domain: str
    trial: int
    passed: bool
    turns: list[Turn]
    failure_mode: FailureMode = FailureMode.CORRECT
    failure_turn: Optional[int] = None   # Which turn did it fail on?
    model: str = ""
    latency_ms: float = 0.0
    total_tokens: int = 0
    raw_response: Any = None


@dataclass
class ConsistencyResult:
    """Consistency result for a single task across N trials."""
    task_id: int
    domain: str
    model: str
    num_trials: int
    num_passed: int
    pass_rate: float               # pass@1 equivalent
    consistency_score: float       # % of trials that agree (pass OR fail)
    failure_modes: list[FailureMode]
    avg_failure_turn: Optional[float]
    results: list[EvalResult]

    @property
    def is_consistent(self) -> bool:
        """True if agent always gives same outcome (always pass or always fail)."""
        return self.consistency_score >= 0.875   # 7/8 threshold


@dataclass
class DomainReport:
    """Aggregate report for a full domain evaluation run."""
    domain: str
    model: str
    total_tasks: int
    pass_at_1: float
    consistency_at_n: float
    num_trials: int
    failure_breakdown: dict[str, int]
    avg_failure_turn: float
    results: list[ConsistencyResult]
    adversarial_pass_rate: Optional[float] = None
