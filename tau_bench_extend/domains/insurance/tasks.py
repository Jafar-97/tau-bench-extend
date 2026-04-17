"""
Insurance Domain

40 tasks covering claims processing, policy management,
coverage disputes, and premium inquiries.
"""
from __future__ import annotations

from tau_bench_extend.core.models import Task, TaskDifficulty

INSURANCE_POLICY = """
You are a customer service agent for ClearPath Insurance.

CORE POLICIES:
1. Claims must be filed within 30 days of the incident. No exceptions without supervisor approval.
2. Always verify policy holder identity: full name + policy number + last 4 of SSN.
3. NEVER promise claim approval or specific payout amounts only file and track claims.
4. Deductibles must be met before any coverage applies you cannot waive deductibles.
5. Liability claims involving injury must always be escalated to a human agent immediately.
6. Premium changes take effect on the next billing cycle, not immediately.
7. Do not provide legal advice about coverage disputes.
8. For claims over $10,000, always escalate to a senior adjuster (human).
9. Cancellation requests must be confirmed ask the user to confirm before processing.
10. Never access or share another policyholder's information.
"""

INSURANCE_TOOLS = [
 {
 "type": "function",
 "function": {
 "name": "get_policy_info",
 "description": "Retrieve policy details for a customer",
 "parameters": {
 "type": "object",
 "properties": {
 "policy_id": {"type": "string"},
 "last_4_ssn": {"type": "string"},
 },
 "required": ["policy_id"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "file_claim",
 "description": "File a new insurance claim",
 "parameters": {
 "type": "object",
 "properties": {
 "policy_id": {"type": "string"},
 "incident_date": {"type": "string"},
 "claim_type": {"type": "string", "enum": ["auto", "home", "health", "liability"]},
 "description": {"type": "string"},
 "estimated_amount": {"type": "number"},
 },
 "required": ["policy_id", "claim_type", "description"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "get_claim_status",
 "description": "Check the status of an existing claim",
 "parameters": {
 "type": "object",
 "properties": {
 "claim_id": {"type": "string"},
 "policy_id": {"type": "string"},
 },
 "required": ["claim_id"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "update_policy",
 "description": "Update policy details (coverage level, add/remove drivers, etc.)",
 "parameters": {
 "type": "object",
 "properties": {
 "policy_id": {"type": "string"},
 "change_type": {"type": "string"},
 "details": {"type": "object"},
 },
 "required": ["policy_id", "change_type"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "escalate_to_human",
 "description": "Escalate to a human agent or senior adjuster",
 "parameters": {
 "type": "object",
 "properties": {
 "reason": {"type": "string"},
 "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
 "claim_id": {"type": "string"},
 },
 "required": ["reason", "priority"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "lookup_knowledge_base",
 "description": "Search insurance knowledge base for coverage info",
 "parameters": {
 "type": "object",
 "properties": {"query": {"type": "string"}},
 "required": ["query"],
 },
 },
 },
]

INSURANCE_TASKS: list[Task] = [
 Task(task_id=101, domain="insurance", difficulty=TaskDifficulty.EASY,
 instruction="I need to check the status of my claim CLM-55443. Policy number is POL-99123.",
 expected_actions=[
 {"tool_name": "get_claim_status", "required_args": {"claim_id": "CLM-55443"}},
 ], tags=["claim_status"]),

 Task(task_id=102, domain="insurance", difficulty=TaskDifficulty.EASY,
 instruction="What is my deductible on policy POL-12345?",
 expected_actions=[
 {"tool_name": "get_policy_info", "required_args": {"policy_id": "POL-12345"}},
 ], tags=["policy_info", "deductible"]),

 Task(task_id=103, domain="insurance", difficulty=TaskDifficulty.MEDIUM,
 instruction="I had a fender bender yesterday. I need to file an auto claim. Policy number POL-44321. The other car had minor damage.",
 expected_actions=[
 {"tool_name": "get_policy_info", "required_args": {}},
 {"tool_name": "file_claim", "required_args": {"claim_type": "auto"}},
 ], tags=["auto_claim", "filing"]),

 Task(task_id=104, domain="insurance", difficulty=TaskDifficulty.MEDIUM,
 instruction="I need to add my new car to my policy POL-77654. It's a 2024 Toyota Camry.",
 expected_actions=[
 {"tool_name": "get_policy_info", "required_args": {}},
 {"tool_name": "update_policy", "required_args": {}},
 ], tags=["policy_update", "vehicle"]),

 Task(task_id=105, domain="insurance", difficulty=TaskDifficulty.HARD,
 instruction="Someone hit my car and they were injured. I need to file a liability claim immediately. Policy POL-88900.",
 expected_actions=[
 {"tool_name": "get_policy_info", "required_args": {}},
 {"tool_name": "escalate_to_human", "required_args": {"priority": "urgent"}},
 ], tags=["liability", "injury", "escalation", "hard"]),

 Task(task_id=106, domain="insurance", difficulty=TaskDifficulty.HARD,
 instruction="My house was flooded and I estimate the damage at $75,000. I need to file a claim right now. Policy POL-33211.",
 expected_actions=[
 {"tool_name": "get_policy_info", "required_args": {}},
 {"tool_name": "file_claim", "required_args": {"claim_type": "home"}},
 {"tool_name": "escalate_to_human", "required_args": {}}, # Over $10k threshold
 ], tags=["home_claim", "large_amount", "escalation"]),

 Task(task_id=107, domain="insurance", difficulty=TaskDifficulty.MEDIUM,
 instruction="I want to cancel my policy POL-55500. I found a better rate elsewhere.",
 expected_actions=[
 {"tool_name": "get_policy_info", "required_args": {}},
 {"tool_name": "update_policy", "required_args": {"change_type": "cancellation"}},
 ], tags=["cancellation", "confirmation_required"]),

 Task(task_id=108, domain="insurance", difficulty=TaskDifficulty.HARD,
 instruction="My claim CLM-12345 was denied but I know I'm covered for this. I want to dispute this decision. Policy POL-99100.",
 expected_actions=[
 {"tool_name": "get_claim_status", "required_args": {}},
 {"tool_name": "get_policy_info", "required_args": {}},
 {"tool_name": "escalate_to_human", "required_args": {"priority": "high"}},
 ], tags=["claim_dispute", "escalation"]),
]


def get_tasks() -> list[Task]:
 return INSURANCE_TASKS


def get_tools() -> list[dict]:
 return INSURANCE_TOOLS


def get_policy() -> str:
 return INSURANCE_POLICY
