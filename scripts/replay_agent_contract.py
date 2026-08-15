from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _tools(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {tool["name"]: tool for tool in contract["tools"]}


def replay(old_contract: dict[str, Any], new_contract: dict[str, Any], trajectory: dict[str, Any]) -> dict[str, Any]:
    old_tools = _tools(old_contract)
    new_tools = _tools(new_contract)
    impacts: list[dict[str, Any]] = []
    replayed = 0

    for index, step in enumerate(trajectory["steps"]):
        if step.get("type") != "tool_call":
            continue
        replayed += 1
        name = step["name"]
        arguments = step.get("arguments", {})
        old_tool = old_tools.get(name)
        new_tool = new_tools.get(name)

        if old_tool is None:
            impacts.append({"step": index, "tool": name, "reason": "historical_tool_absent_from_old_contract"})
            continue
        if new_tool is None:
            impacts.append({"step": index, "tool": name, "reason": "tool_removed"})
            continue

        old_required = set(old_tool.get("required", []))
        for argument in sorted(set(new_tool.get("required", [])) - old_required):
            if argument not in arguments:
                impacts.append({"step": index, "tool": name, "reason": "new_required_argument_missing", "argument": argument})

        for argument, value in sorted(arguments.items()):
            schema = new_tool.get("properties", {}).get(argument, {})
            enum = schema.get("enum")
            if isinstance(enum, list) and value not in enum:
                impacts.append({"step": index, "tool": name, "reason": "enum_value_no_longer_admitted", "argument": argument, "value": value})

    return {
        "schema_version": "agent-contract-replay-receipt.v1",
        "old_contract_digest": digest(old_contract),
        "new_contract_digest": digest(new_contract),
        "trajectory_digest": digest(trajectory),
        "replayed_tool_calls": replayed,
        "impact_count": len(impacts),
        "decision": "BREAKING" if impacts else "PASS",
        "impacts": impacts,
    }
