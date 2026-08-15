#!/usr/bin/env python3
"""Compile an append-only aggregate ledger for contract-history receipts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from replay_publisher_schema_revision import canonical_bytes, digest

ROOT = Path(__file__).resolve().parents[1]


class LedgerError(ValueError):
    """Raised when the aggregate evidence ledger violates an invariant."""


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LedgerError(f"{path} must contain a JSON object")
    return value


def _repo_path(value: Any) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise LedgerError("ledger paths must be non-empty repository-relative strings")
    resolved = (ROOT / value).resolve()
    if ROOT not in resolved.parents:
        raise LedgerError(f"ledger path escapes repository: {value}")
    return resolved


def _verify_self_digest(receipt: dict[str, Any]) -> None:
    claimed = receipt.get("receipt_digest")
    if not isinstance(claimed, str):
        raise LedgerError("extension receipt_digest is absent")
    unsigned = dict(receipt)
    unsigned.pop("receipt_digest", None)
    if digest(unsigned) != claimed:
        raise LedgerError("extension receipt self-digest mismatch")


def compile_ledger(spec: dict[str, Any]) -> dict[str, Any]:
    if spec.get("schema_version") != "history-evidence-ledger-input.v1":
        raise LedgerError("unsupported ledger input schema_version")
    if spec.get("market_state") != "VALIDATE":
        raise LedgerError("aggregate market state must remain VALIDATE")
    target = spec.get("historical_breakage_gate_target")
    if not isinstance(target, int) or target <= 0:
        raise LedgerError("historical_breakage_gate_target must be positive")

    base_spec = spec.get("base_corpus")
    if not isinstance(base_spec, dict):
        raise LedgerError("base_corpus is absent")
    base = _load_object(_repo_path(base_spec.get("path")))
    if base.get("schema_version") != "contract-history-corpus-receipt.v2":
        raise LedgerError("base corpus receipt schema drift")
    if base.get("receipt_digest") != base_spec.get("expected_receipt_digest"):
        raise LedgerError("base corpus receipt digest drift")
    base_count = base.get("summary", {}).get("real_historical_breakage_count")
    if base_count != base_spec.get("expected_real_historical_breakage_count"):
        raise LedgerError("base corpus historical count drift")
    if base.get("summary", {}).get("market_state") != "VALIDATE":
        raise LedgerError("base corpus market state drift")

    base_receipt_ids = {item.get("case_id") for item in base.get("receipts", [])}
    admitted_base = base_spec.get("admitted_cases")
    if not isinstance(admitted_base, list) or not admitted_base:
        raise LedgerError("base admitted_cases must be a non-empty list")
    if {item.get("case_id") for item in admitted_base} != base_receipt_ids:
        raise LedgerError("base admitted case IDs drift")

    extensions = spec.get("extensions")
    if not isinstance(extensions, list) or not extensions:
        raise LedgerError("extensions must be a non-empty list")

    case_ids: list[str] = []
    event_ids: list[str] = []
    for item in admitted_base:
        case_id = item.get("case_id")
        event_id = item.get("change_event_id")
        if not isinstance(case_id, str) or not isinstance(event_id, str):
            raise LedgerError("base case/event identity is absent")
        case_ids.append(case_id)
        event_ids.append(event_id)

    declared_case_ids = case_ids + [item.get("case_id") for item in extensions if isinstance(item, dict)]
    declared_event_ids = event_ids + [item.get("change_event_id") for item in extensions if isinstance(item, dict)]
    if len(declared_case_ids) != len(set(declared_case_ids)):
        raise LedgerError("duplicate case_id in aggregate ledger")
    if len(declared_event_ids) != len(set(declared_event_ids)):
        raise LedgerError("duplicate change_event_id in aggregate ledger")
    if len(extensions) != 1:
        raise LedgerError("this leaf must add exactly one extension receipt")

    rendered_extensions: list[dict[str, Any]] = []
    for extension_spec in extensions:
        if not isinstance(extension_spec, dict):
            raise LedgerError("extension spec must be an object")
        receipt = _load_object(_repo_path(extension_spec.get("path")))
        _verify_self_digest(receipt)
        if receipt.get("receipt_digest") != extension_spec.get("expected_receipt_digest"):
            raise LedgerError("extension expected receipt digest drift")
        if receipt.get("case_id") != extension_spec.get("case_id"):
            raise LedgerError("extension case_id drift")
        if receipt.get("change_event_id") != extension_spec.get("change_event_id"):
            raise LedgerError("extension change_event_id drift")
        if receipt.get("decision") != "HISTORICAL_BREAKAGE":
            raise LedgerError("extension decision is not HISTORICAL_BREAKAGE")
        if receipt.get("counts_toward_real_breakage_gate") is not True:
            raise LedgerError("extension does not count toward the gate")
        if receipt.get("source_digests") != extension_spec.get("expected_source_digests"):
            raise LedgerError("extension source receipt digests drift")
        case_ids.append(receipt["case_id"])
        event_ids.append(receipt["change_event_id"])
        rendered_extensions.append(
            {
                "case_id": receipt["case_id"],
                "change_event_id": receipt["change_event_id"],
                "path": extension_spec["path"],
                "receipt_digest": receipt["receipt_digest"],
                "source_digests": receipt["source_digests"],
                "decision": receipt["decision"],
                "counts_toward_real_breakage_gate": True,
            }
        )

    if len(case_ids) != len(set(case_ids)):
        raise LedgerError("duplicate case_id in aggregate ledger")
    if len(event_ids) != len(set(event_ids)):
        raise LedgerError("duplicate change_event_id in aggregate ledger")

    current = base_count + len(rendered_extensions)
    if current > target:
        raise LedgerError("aggregate count exceeds gate target")
    output: dict[str, Any] = {
        "schema_version": "history-evidence-ledger.v1",
        "ledger_id": spec.get("ledger_id"),
        "input_digest": digest(spec),
        "market_state": "VALIDATE",
        "base_corpus": {
            "path": base_spec["path"],
            "receipt_digest": base["receipt_digest"],
            "real_historical_breakage_count": base_count,
            "case_ids": sorted(base_receipt_ids),
            "change_event_ids": sorted(item["change_event_id"] for item in admitted_base),
        },
        "extensions": sorted(rendered_extensions, key=lambda item: item["case_id"]),
        "gate": {
            "target": target,
            "current": current,
            "remaining": target - current,
            "build_admitted": False,
        },
        "case_ids": sorted(case_ids),
        "change_event_ids": sorted(event_ids),
    }
    output["ledger_digest"] = digest(output)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)

    try:
        compiled = compile_ledger(_load_object(args.spec))
    except (LedgerError, json.JSONDecodeError, OSError) as error:
        print(f"history-evidence-ledger: FAIL: {error}", file=sys.stderr)
        return 1

    rendered = canonical_bytes(compiled)
    if args.check:
        try:
            committed = args.check.read_bytes()
        except OSError as error:
            print(f"history-evidence-ledger: FAIL: {error}", file=sys.stderr)
            return 1
        if committed != rendered:
            print("history-evidence-ledger: FAIL: committed ledger drift", file=sys.stderr)
            return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(rendered)
    elif not args.check:
        sys.stdout.buffer.write(rendered)

    print(
        "history-evidence-ledger: PASS "
        f"current={compiled['gate']['current']} target={compiled['gate']['target']} "
        f"digest={compiled['ledger_digest']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
