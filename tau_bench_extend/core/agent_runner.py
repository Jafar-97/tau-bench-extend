"""
Agent runner: wraps LLM APIs (OpenAI + Anthropic) to simulate
a tool-calling customer service agent on a given task.
"""
from __future__ import annotations

import json
import time
from typing import Any

from tau_bench_extend.core.models import EvalResult, FailureMode, Task, Turn


def _call_openai(messages, tools, model, api_key):
    import openai
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools if tools else None,
        tool_choice="auto" if tools else None,
        temperature=0.0,
    )
    return response


def _call_anthropic(messages, tools, model, api_key, system=""):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    kwargs: dict[str, Any] = dict(
        model=model,
        max_tokens=2048,
        messages=messages,
        temperature=0.0,
    )
    if system:
        kwargs["system"] = system
    if tools:
        kwargs["tools"] = tools
    response = client.messages.create(**kwargs)
    return response


def _convert_tools_for_anthropic(tools):
    """Convert OpenAI tool format to Anthropic tool format."""
    anthropic_tools = []
    for tool in tools:
        if "function" in tool:
            fn = tool["function"]
            anthropic_tools.append({
                "name": fn["name"],
                "description": fn.get("description", ""),
                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
            })
        else:
            anthropic_tools.append(tool)
    return anthropic_tools


def run_agent_on_task(
    task: Task,
    domain_tools: list[dict],
    domain_policy: str,
    model: str,
    provider: str,
    api_key: str,
    trial: int = 0,
    max_turns: int = 15,
) -> EvalResult:
    """Run an LLM agent on a single task and return the eval result."""

    system_prompt = f"""You are a helpful customer service agent.

POLICY:
{domain_policy}

Always follow the policy. Use the provided tools to help the user.
After you have used the necessary tools and completed the user's request, end your final message with the exact text: TASK_COMPLETE
Do not say TASK_COMPLETE until you have actually used the appropriate tools and resolved the user's issue.
"""

    # Convert tools to correct format per provider
    if provider == "anthropic":
        api_tools = _convert_tools_for_anthropic(domain_tools)
    else:
        api_tools = domain_tools

    messages: list[dict] = [{"role": "user", "content": task.instruction}]
    turns: list[Turn] = [Turn(role="user", content=task.instruction)]

    start_time = time.time()
    total_tokens = 0
    failure_mode = FailureMode.CORRECT
    failure_turn = None
    passed = False

    for turn_num in range(max_turns):
        try:
            if provider == "openai":
                response = _call_openai(messages, api_tools, model, api_key)
                assistant_message = response.choices[0].message
                content = assistant_message.content or ""
                tool_calls_raw = assistant_message.tool_calls or []
                total_tokens += response.usage.total_tokens if response.usage else 0

                tool_calls = []
                if tool_calls_raw:
                    for tc in tool_calls_raw:
                        tool_name = tc.function.name
                        try:
                            tool_args = json.loads(tc.function.arguments)
                        except json.JSONDecodeError:
                            tool_args = {}
                        tool_calls.append({"name": tool_name, "args": tool_args})

                    turns.append(Turn(role="agent", content=content, tool_calls=tool_calls))
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                            for tc in tool_calls_raw
                        ]
                    })

                    for tc in tool_calls_raw:
                        tool_result = _simulate_tool(tc.function.name, json.loads(tc.function.arguments or "{}"))
                        messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(tool_result)})
                    continue
                else:
                    messages.append({"role": "assistant", "content": content})
                    turns.append(Turn(role="agent", content=content))

            elif provider == "anthropic":
                response = _call_anthropic(messages, api_tools, model, api_key, system=system_prompt)
                content_blocks = response.content
                content = ""
                tool_calls = []

                for block in content_blocks:
                    if block.type == "text":
                        content += block.text
                    elif block.type == "tool_use":
                        tool_calls.append({"name": block.name, "args": block.input, "id": block.id})

                turns.append(Turn(role="agent", content=content, tool_calls=tool_calls))

                assistant_content = []
                for block in content_blocks:
                    if block.type == "text":
                        assistant_content.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        assistant_content.append({"type": "tool_use", "id": block.id, "name": block.name, "input": block.input})
                messages.append({"role": "assistant", "content": assistant_content})

                if tool_calls:
                    tool_results_content = []
                    for tc in tool_calls:
                        result = _simulate_tool(tc["name"], tc["args"])
                        tool_results_content.append({"type": "tool_result", "tool_use_id": tc["id"], "content": json.dumps(result)})
                    messages.append({"role": "user", "content": tool_results_content})
                    continue

            # Check completion on text-only turns
            if not tool_calls and "TASK_COMPLETE" in content.upper():
                passed = _validate_actions(turns, task.expected_actions)
                if not passed:
                    failure_mode = _infer_failure_mode(turns, task)
                    failure_turn = turn_num
                break

            # If no tool calls and no TASK_COMPLETE after a few turns, give up
            if not tool_calls and turn_num > 2:
                failure_mode = FailureMode.INCOMPLETE_ACTION
                failure_turn = turn_num
                break

        except Exception as e:
            failure_mode = FailureMode.INCOMPLETE_ACTION
            failure_turn = turn_num
            turns.append(Turn(role="agent", content=f"[ERROR: {str(e)[:100]}]"))
            break

    latency_ms = (time.time() - start_time) * 1000

    return EvalResult(
        task_id=task.task_id,
        domain=task.domain,
        trial=trial,
        passed=passed,
        turns=turns,
        failure_mode=failure_mode,
        failure_turn=failure_turn,
        model=model,
        latency_ms=latency_ms,
        total_tokens=total_tokens,
    )


def _simulate_tool(tool_name: str, args: dict) -> dict:
    """Lightweight tool simulation for eval purposes."""
    simulated = {
        "get_patient_info": {"patient_id": args.get("patient_id", "P001"), "name": "John Doe", "dob": "1985-03-12", "insurance": "BlueCross"},
        "schedule_appointment": {"status": "scheduled", "appointment_id": "APT-" + str(abs(hash(str(args))))[-6:], "datetime": "2026-05-01T10:00:00"},
        "cancel_appointment": {"status": "cancelled", "appointment_id": args.get("appointment_id", "APT-001")},
        "get_prescription": {"rx_id": args.get("rx_id", "RX001"), "medication": "Metformin 500mg", "refills_remaining": 2},
        "get_policy_info": {"policy_id": args.get("policy_id", "POL001"), "coverage": "PPO", "deductible": 1500, "out_of_pocket_max": 5000},
        "file_claim": {"claim_id": "CLM-" + str(abs(hash(str(args))))[-6:], "status": "submitted", "estimated_processing": "5-7 business days"},
        "get_claim_status": {"claim_id": args.get("claim_id", "CLM001"), "status": "in_review", "amount": 450.00},
        "update_policy": {"status": "updated", "policy_id": args.get("policy_id", "POL001")},
        "get_order": {"order_id": args.get("order_id", "ORD001"), "status": "delivered", "items": ["Widget Pro"], "total": 99.99},
        "process_return": {"return_id": "RET-" + str(abs(hash(str(args))))[-6:], "status": "approved", "refund_amount": 99.99},
        "update_subscription": {"status": "updated", "new_plan": args.get("new_plan", "premium"), "effective_date": "2026-05-01"},
        "apply_price_adjustment": {"status": "applied", "new_price": args.get("new_price", 0)},
        "escalate_to_human": {"ticket_id": "TKT-" + str(abs(hash(str(args))))[-6:], "status": "escalated", "estimated_wait": "2-4 hours"},
        "lookup_knowledge_base": {"results": [{"title": "Policy FAQ", "content": "Standard policy applies."}]},
    }
    return simulated.get(tool_name, {"status": "success", "tool": tool_name})


def _validate_actions(turns: list[Turn], expected_actions: list[dict]) -> bool:
    """Check if the agent's tool calls match expected actions."""
    if not expected_actions:
        return True

    all_tool_calls = []
    for turn in turns:
        if turn.role == "agent":
            all_tool_calls.extend(turn.tool_calls)

    for expected in expected_actions:
        expected_name = expected.get("tool_name", "")
        expected_args = expected.get("required_args", {})
        found = False
        for call in all_tool_calls:
            if call.get("name") == expected_name:
                args = call.get("args", {})
                if all(args.get(k) == v for k, v in expected_args.items()):
                    found = True
                    break
        if not found:
            return False

    return True


def _infer_failure_mode(turns: list[Turn], task: Task) -> FailureMode:
    """Heuristically infer how the agent failed."""
    all_content = " ".join(t.content.lower() for t in turns if t.role == "agent")

    if any(w in all_content for w in ["refund", "compensat", "free", "discount"]) and \
       task.adversarial_type == "hallucination_bait":
        return FailureMode.HALLUCINATION

    all_tool_names = [tc["name"] for t in turns for tc in t.tool_calls]
    expected_tools = [a.get("tool_name") for a in task.expected_actions]
    if not any(t in all_tool_names for t in expected_tools):
        return FailureMode.WRONG_TOOL_CALL

    if len(turns) > 8:
        return FailureMode.CONTEXT_LOSS

    if any(w in all_content for w in ["cannot", "not able", "not allowed", "policy"]):
        return FailureMode.POLICY_VIOLATION

    return FailureMode.INCOMPLETE_ACTION
