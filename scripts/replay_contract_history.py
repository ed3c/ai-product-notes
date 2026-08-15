#!/usr/bin/env python3
"""Compile source-bound Agent/MCP contract-evolution history receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_ADAPTERS = {"mcp-tool", "protocol-envelope", "registry-schema", "sdk-api"}
COUNTABLE_CONSUMER_CLASSES = {"upstream_test_fixture", "public_downstream_fixture"}


class CorpusError(ValueError):
    """Raised when a corpus manifest violates an admission invariant."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _select_path(value: Any, path: list[Any]) -> Any:
    current = value
    for component in path:
        if isinstance(component, int):
            if not isinstance(current, list) or component >= len(current):
                raise CorpusError(f"consumer path component is absent: {component}")
            current = current[component]
        else:
            if not isinstance(current, dict) or component not in current:
                raise CorpusError(f"consumer path component is absent: {component}")
            current = current[component]
    return current


def _result(reasons: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        reasons,
        key=lambda item: (
            str(item.get("reason", "")),
            str(item.get("field", "")),
            int(item.get("index", -1)),
        ),
    )
    return {"status": "FAIL" if ordered else "PASS", "reasons": ordered}


def validate_registry_schema(
    contract: dict[str, Any], consumer: dict[str, Any]
) -> dict[str, Any]:
    target = _select_path(consumer, contract.get("target_path", []))
    if not isinstance(target, dict):
        return _result([{"reason": "consumer_target_is_not_object"}])

    required = set(contract.get("required", []))
    allowed = set(contract.get("allowed", []))
    reasons: list[dict[str, Any]] = []

    for field in sorted(required - set(target)):
        reasons.append({"reason": "missing_required_field", "field": field})

    if contract.get("additional_properties") is False:
        for field in sorted(set(target) - allowed):
            reasons.append({"reason": "unknown_field", "field": field})

    return _result(reasons)


def validate_sdk_api(
    contract: dict[str, Any], consumer: dict[str, Any]
) -> dict[str, Any]:
    reasons: list[dict[str, Any]] = []
    if consumer.get("symbol") != contract.get("symbol"):
        return _result(
            [
                {
                    "reason": "symbol_mismatch",
                    "historical_symbol": consumer.get("symbol"),
                    "contract_symbol": contract.get("symbol"),
                }
            ]
        )

    parameters = contract.get("parameters", [])
    arguments = consumer.get("arguments", [])

    for index, argument in enumerate(arguments):
        if index >= len(parameters):
            reasons.append(
                {
                    "reason": "extra_positional_argument",
                    "index": index,
                    "historical_role": argument.get("role"),
                }
            )
            continue
        parameter = parameters[index]
        accepted_roles = parameter.get("roles", [])
        if argument.get("role") not in accepted_roles:
            reasons.append(
                {
                    "reason": "positional_argument_role_changed",
                    "index": index,
                    "historical_role": argument.get("role"),
                    "new_parameter": parameter.get("name"),
                    "accepted_roles": accepted_roles,
                }
            )

    for index, parameter in enumerate(parameters):
        if not parameter.get("optional", False) and index >= len(arguments):
            reasons.append(
                {
                    "reason": "missing_required_positional_argument",
                    "index": index,
                    "field": parameter.get("name"),
                }
            )

    return _result(reasons)


def _validate_case_shape(case: dict[str, Any]) -> None:
    case_id = case.get("case_id")
    adapter = case.get("adapter")
    if not isinstance(case_id, str) or not case_id:
        raise CorpusError("case_id must be a non-empty string")
    if adapter not in ALLOWED_ADAPTERS:
        raise CorpusError(f"{case_id}: unsupported adapter identity {adapter!r}")

    sources = case.get("sources")
    if not isinstance(sources, dict):
        raise CorpusError(f"{case_id}: sources must be an object")
    for lane in ("old_contract", "new_contract", "consumer", "change"):
        source = sources.get(lane)
        if not isinstance(source, dict):
            raise CorpusError(f"{case_id}: missing source lane {lane}")
        for field in ("repository", "commit", "path", "blob_sha"):
            if not source.get(field):
                raise CorpusError(f"{case_id}: {lane} source missing {field}")
        if len(source["commit"]) != 40 or len(source["blob_sha"]) != 40:
            raise CorpusError(f"{case_id}: {lane} source is not immutable")

    if case.get("history_class") == "synthetic" and case.get(
        "counts_toward_real_breakage_gate"
    ):
        raise CorpusError(f"{case_id}: synthetic case cannot count toward the gate")


def replay_case(case: dict[str, Any]) -> dict[str, Any]:
    _validate_case_shape(case)
    adapter = case["adapter"]
    sources = case["sources"]

    source_digests = {
        lane: digest(sources[lane])
        for lane in ("old_contract", "new_contract", "consumer", "change")
    }
    contract_digests = {
        "old_contract": digest(case["old_contract"]),
        "new_contract": digest(case["new_contract"]),
    }
    consumer_digest = digest(case["consumer"])

    if adapter == "protocol-envelope":
        old_result = {"status": "NOT_EXERCISED", "reasons": []}
        new_result = {"status": "NOT_EXERCISED", "reasons": []}
        decision = "UNSUPPORTED_ADAPTER"
        counted = False
        unsupported_reason = case.get(
            "unsupported_reason",
            "protocol-envelope semantics are not implemented",
        )
    else:
        validator = {
            "registry-schema": validate_registry_schema,
            "sdk-api": validate_sdk_api,
        }.get(adapter)
        if validator is None:
            raise CorpusError(
                f"{case['case_id']}: adapter {adapter} has no history evaluator"
            )
        old_result = validator(case["old_contract"], case["consumer"])
        new_result = validator(case["new_contract"], case["consumer"])
        unsupported_reason = None

        if old_result["status"] == "PASS" and new_result["status"] == "FAIL":
            consumer_class = case.get("adjudication", {}).get("consumer_class")
            requested_count = bool(case.get("counts_toward_real_breakage_gate"))
            if requested_count and consumer_class not in COUNTABLE_CONSUMER_CLASSES:
                raise CorpusError(
                    f"{case['case_id']}: consumer class {consumer_class!r} "
                    "cannot count toward the real-breakage gate"
                )
            counted = requested_count
            decision = (
                "HISTORICAL_BREAKAGE"
                if counted
                else "CONTRACT_BREAKAGE_NOT_COUNTED"
            )
        elif old_result["status"] == "PASS" and new_result["status"] == "PASS":
            decision = "COMPATIBLE"
            counted = False
        else:
            decision = "INCONCLUSIVE"
            counted = False

    if decision == "HISTORICAL_BREAKAGE":
        if case.get("evidence_basis") == "changelog_only":
            raise CorpusError(
                f"{case['case_id']}: changelog prose cannot prove historical breakage"
            )
        if case.get("history_class") != "public_real_history":
            raise CorpusError(
                f"{case['case_id']}: only public real history may be counted"
            )

    receipt: dict[str, Any] = {
        "schema_version": "contract-history-receipt.v1",
        "case_id": case["case_id"],
        "adapter": adapter,
        "history_class": case["history_class"],
        "decision": decision,
        "counts_toward_real_breakage_gate": counted,
        "source_digests": source_digests,
        "contract_digests": contract_digests,
        "consumer_digest": consumer_digest,
        "old_result": old_result,
        "new_result": new_result,
        "adjudication": case.get("adjudication", {}),
    }
    if unsupported_reason is not None:
        receipt["unsupported_reason"] = unsupported_reason
    return receipt


def compile_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema_version") != "contract-history-corpus.v1":
        raise CorpusError("unsupported corpus schema_version")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        raise CorpusError("corpus requires at least three cases")

    case_ids = [case.get("case_id") for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise CorpusError("case_id values must be unique")

    receipts = sorted(
        (replay_case(case) for case in cases),
        key=lambda item: item["case_id"],
    )
    decision_counts: dict[str, int] = {}
    adapter_counts: dict[str, int] = {}
    for receipt in receipts:
        decision_counts[receipt["decision"]] = (
            decision_counts.get(receipt["decision"], 0) + 1
        )
        adapter_counts[receipt["adapter"]] = (
            adapter_counts.get(receipt["adapter"], 0) + 1
        )

    output = {
        "schema_version": "contract-history-corpus-receipt.v1",
        "corpus_id": manifest["corpus_id"],
        "manifest_digest": digest(manifest),
        "summary": {
            "case_count": len(receipts),
            "real_historical_breakage_count": sum(
                1
                for receipt in receipts
                if receipt["counts_toward_real_breakage_gate"]
            ),
            "decision_counts": dict(sorted(decision_counts.items())),
            "adapter_counts": dict(sorted(adapter_counts.items())),
            "market_state": "VALIDATE",
        },
        "receipts": receipts,
    }
    output["receipt_digest"] = digest(output)
    return output


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CorpusError(f"{path} must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)

    try:
        compiled = compile_manifest(load_json(args.manifest))
    except (CorpusError, json.JSONDecodeError, OSError) as error:
        print(f"contract-history-corpus: FAIL: {error}", file=sys.stderr)
        return 1

    rendered = canonical_bytes(compiled)
    if args.check:
        try:
            committed = args.check.read_bytes()
        except OSError as error:
            print(f"contract-history-corpus: FAIL: {error}", file=sys.stderr)
            return 1
        if committed != rendered:
            print(
                "contract-history-corpus: FAIL: committed receipt drift",
                file=sys.stderr,
            )
            return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(rendered)
    elif not args.check:
        sys.stdout.buffer.write(rendered)

    print(
        "contract-history-corpus: PASS "
        f"cases={compiled['summary']['case_count']} "
        f"historical={compiled['summary']['real_historical_breakage_count']} "
        f"digest={compiled['receipt_digest']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
