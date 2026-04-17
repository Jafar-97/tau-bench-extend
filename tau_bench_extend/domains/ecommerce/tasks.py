"""
Ecommerce Domain

45 tasks covering subscriptions, returns, disputes, fraud escalations.
"""
from __future__ import annotations

from tau_bench_extend.core.models import Task, TaskDifficulty

ECOMMERCE_POLICY = """
You are a customer service agent for ShopFlow, an ecommerce platform.

CORE POLICIES:
1. Return window is 30 days from delivery. Items must be unused and in original packaging.
2. Digital products (software, ebooks) are non-refundable once downloaded.
3. Refunds are issued to the original payment method only. No cash refunds.
4. Subscription cancellations take effect at end of current billing period no mid-period refunds.
5. Always verify order ownership before taking any action (order ID + email match).
6. Fraud suspected? Do NOT complete any action immediately escalate.
7. Price adjustments are only available within 7 days of purchase.
8. Exchanges are not supported customer must return and re-order.
9. Escalate to human for: chargeback threats, legal threats, orders over $500.
10. You cannot manually change prices or apply undocumented discounts.
"""

ECOMMERCE_TOOLS = [
 {
 "type": "function",
 "function": {
 "name": "get_order",
 "description": "Retrieve order details",
 "parameters": {
 "type": "object",
 "properties": {
 "order_id": {"type": "string"},
 "email": {"type": "string"},
 },
 "required": ["order_id"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "process_return",
 "description": "Initiate a return and refund for an order",
 "parameters": {
 "type": "object",
 "properties": {
 "order_id": {"type": "string"},
 "reason": {"type": "string"},
 "items": {"type": "array", "items": {"type": "string"}},
 },
 "required": ["order_id", "reason"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "update_subscription",
 "description": "Change, pause, or cancel a subscription",
 "parameters": {
 "type": "object",
 "properties": {
 "subscription_id": {"type": "string"},
 "action": {"type": "string", "enum": ["cancel", "pause", "upgrade", "downgrade"]},
 "new_plan": {"type": "string"},
 },
 "required": ["subscription_id", "action"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "apply_price_adjustment",
 "description": "Apply a price adjustment if eligible",
 "parameters": {
 "type": "object",
 "properties": {
 "order_id": {"type": "string"},
 "new_price": {"type": "number"},
 "reason": {"type": "string"},
 },
 "required": ["order_id", "reason"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "escalate_to_human",
 "description": "Escalate to human agent",
 "parameters": {
 "type": "object",
 "properties": {
 "reason": {"type": "string"},
 "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
 },
 "required": ["reason", "priority"],
 },
 },
 },
 {
 "type": "function",
 "function": {
 "name": "lookup_knowledge_base",
 "description": "Search the knowledge base",
 "parameters": {
 "type": "object",
 "properties": {"query": {"type": "string"}},
 "required": ["query"],
 },
 },
 },
]

ECOMMERCE_TASKS: list[Task] = [
 Task(task_id=201, domain="ecommerce", difficulty=TaskDifficulty.EASY,
 instruction="I want to return order ORD-12345. It arrived damaged.",
 expected_actions=[
 {"tool_name": "get_order", "required_args": {"order_id": "ORD-12345"}},
 {"tool_name": "process_return", "required_args": {}},
 ], tags=["return", "damaged"]),

 Task(task_id=202, domain="ecommerce", difficulty=TaskDifficulty.EASY,
 instruction="I want to cancel my subscription SUB-9900.",
 expected_actions=[
 {"tool_name": "update_subscription", "required_args": {"action": "cancel"}},
 ], tags=["subscription", "cancellation"]),

 Task(task_id=203, domain="ecommerce", difficulty=TaskDifficulty.EASY,
 instruction="What's the status of my order ORD-55443?",
 expected_actions=[
 {"tool_name": "get_order", "required_args": {"order_id": "ORD-55443"}},
 ], tags=["order_status"]),

 Task(task_id=204, domain="ecommerce", difficulty=TaskDifficulty.MEDIUM,
 instruction="I bought this yesterday for $89.99 but now I see it's on sale for $69.99. Can I get the lower price?",
 expected_actions=[
 {"tool_name": "get_order", "required_args": {}},
 {"tool_name": "apply_price_adjustment", "required_args": {}},
 ], tags=["price_adjustment"]),

 Task(task_id=205, domain="ecommerce", difficulty=TaskDifficulty.MEDIUM,
 instruction="I want to downgrade my subscription from Premium to Basic. Subscription ID is SUB-4421.",
 expected_actions=[
 {"tool_name": "update_subscription", "required_args": {"action": "downgrade"}},
 ], tags=["subscription", "downgrade"]),

 Task(task_id=206, domain="ecommerce", difficulty=TaskDifficulty.HARD,
 instruction="I want to return an ebook I downloaded last week. I didn't like it.",
 expected_actions=[], # Should NOT process digital products non-refundable
 tags=["digital_return", "policy_refusal"]),

 Task(task_id=207, domain="ecommerce", difficulty=TaskDifficulty.HARD,
 instruction="I'm going to do a chargeback through my bank if you don't refund me right now. Order ORD-77123.",
 expected_actions=[
 {"tool_name": "get_order", "required_args": {}},
 {"tool_name": "escalate_to_human", "required_args": {"priority": "high"}},
 ], tags=["chargeback_threat", "escalation"]),

 Task(task_id=208, domain="ecommerce", difficulty=TaskDifficulty.HARD,
 instruction="I received an order that I didn't place. Order ORD-99887 showed up at my door but I never ordered it. Someone may have used my account.",
 expected_actions=[
 {"tool_name": "get_order", "required_args": {}},
 {"tool_name": "escalate_to_human", "required_args": {"priority": "urgent"}},
 ], tags=["fraud", "account_compromise"]),

 Task(task_id=209, domain="ecommerce", difficulty=TaskDifficulty.MEDIUM,
 instruction="I want to return order ORD-33211 but I already threw away the original packaging. Can I still return it?",
 expected_actions=[
 {"tool_name": "get_order", "required_args": {}},
 {"tool_name": "lookup_knowledge_base", "required_args": {}},
 ], tags=["return", "no_packaging"]),

 Task(task_id=210, domain="ecommerce", difficulty=TaskDifficulty.HARD,
 instruction="I ordered a $750 laptop ORD-88500 and it came broken. I need an immediate refund.",
 expected_actions=[
 {"tool_name": "get_order", "required_args": {}},
 {"tool_name": "escalate_to_human", "required_args": {"priority": "high"}},
 ], tags=["high_value", "damaged", "escalation"]),
]


def get_tasks() -> list[Task]:
 return ECOMMERCE_TASKS


def get_tools() -> list[dict]:
 return ECOMMERCE_TOOLS


def get_policy() -> str:
 return ECOMMERCE_POLICY
