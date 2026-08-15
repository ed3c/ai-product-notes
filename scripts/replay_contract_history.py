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
REQUIRED_SDK_CI_JOBS = ("TypeScript Typecheck", "Typecheck & Build", "Test & Build")


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


def _validate_source_binding(case_id: str, lane: str, source: Any) -> None:
    if not isinstance(source, dict):
        raise CorpusError(f"{case_id}: missing source lane {lane}")
    for field in ("repository", "commit", "path", "blob_sha"):
        if not source.get(field):
            raise CorpusError(f"{case_id}: {lane} source missing {field}")
    if len(source["commit"]) != 40 or len(source["blob_sha"]) != 40:
        raise CorpusError(f"{case_id}: {lane} source is not immutable")


def _validate_sdk_downstream_provenance(case: dict[str, Any]) -> None:
    case_id = case["case_id"]
    sources = case["sources"]
    validation = case.get("validation")
    if not isinstance(validation, dict):
        raise CorpusError(f"{case_id}: countable sdk-api case requires validation")

    consumer_source = sources["consumer"]
    dependency_lock = validation.get("dependency_lock")
    workflow = validation.get("workflow")
    old_ci = validation.get("old_ci")
    old_package_manifest = validation.get("old_package_manifest")
    new_package_manifest = validation.get("new_package_manifest")

    for lane, source in (
        ("validation.dependency_lock", dependency_lock),
        ("validation.workflow", workflow),
        ("validation.old_package_manifest", old_package_manifest),
        ("validation.new_package_manifest", new_package_manifest),
    ):
        _validate_source_binding(case_id, lane, source)

    for lane, source in (
        ("dependency lock", dependency_lock),
        ("workflow", workflow),
    ):
        if source["repository"] != consumer_source["repository"]:
            raise CorpusError(
                f"{case_id}: {lane} repository must match downstream consumer"
            )
        if source["commit"] != consumer_source["commit"]:
            raise CorpusError(
                f"{case_id}: {lane} commit must match downstream consumer"
            )

    if not isinstance(old_ci, dict):
        raise CorpusError(f"{case_id}: countable sdk-api case requires old_ci")
    if not isinstance(old_ci.get("run_id"), int) or old_ci["run_id"] <= 0:
        raise CorpusError(f"{case_id}: old_ci run_id must be positive")
    if old_ci.get("head_sha") != consumer_source["commit"]:
        raise CorpusError(
            f"{case_id}: old_ci head must equal downstream consumer commit"
        )
    if old_ci.get("workflow_path") != workflow["path"]:
        raise CorpusError(f"{case_id}: old_ci workflow path drift")
    if old_ci.get("conclusion") != "success":
        raise CorpusError(f"{case_id}: old_ci must conclude success")

    jobs = old_ci.get("jobs")
    if not isinstance(jobs, dict):
        raise CorpusError(f"{case_id}: old_ci jobs must be an object")
    for job_name in REQUIRED_SDK_CI_JOBS:
        if jobs.get(job_name) != "success":
            raise CorpusError(
                f"{case_id}: required old_ci job is not successful: {job_name}"
            )

    old_contract = case["old_contract"]
    new_contract = case["new_contract"]
    if old_contract.get("migration_kind") != "sdk-major-package-migration":
        raise CorpusError(f"{case_id}: sdk package migration kind must be explicit")
    if new_contract.get("migration_kind") != "sdk-major-package-migration":
        raise CorpusError(f"{case_id}: sdk package migration kind must be explicit")

    old_package = old_contract.get("package_identity")
    old_version = old_contract.get("validated_package_version")
    new_package = new_contract.get("package_identity")
    new_version = new_contract.get("validated_package_version")

    if dependency_lock.get("package") != old_package:
        raise CorpusError(f"{case_id}: dependency lock package does not match old contract")
    if dependency_lock.get("version") != old_version:
        raise CorpusError(f"{case_id}: dependency lock version does not match old contract")
    if not str(dependency_lock.get("integrity", "")).startswith("sha512-"):
        raise CorpusError(f"{case_id}: dependency lock integrity is absent")

    if old_package_manifest.get("package") != old_package:
        raise CorpusError(f"{case_id}: old package manifest identity drift")
    if old_package_manifest.get("version") != old_version:
        raise CorpusError(f"{case_id}: old package manifest version drift")
    if new_package_manifest.get("package") != new_package:
        raise CorpusError(f"{case_id}: new package manifest identity drift")
    if new_package_manifest.get("version") != new_version:
        raise CorpusError(f"{case_id}: new package manifest version drift")

    if old_package == new_package:
        raise CorpusError(
            f"{case_id}: major package migration must not be rendered as a same-package patch"
        )

    adjudication = case.get("adjudication", {})
    if adjudication.get("consumer_class") != "public_downstream_fixture":
        raise CorpusError(
            f"{case_id}: countable sdk-api case requires public_downstream_fixture"
        )


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
        _validate_source_binding(case_id, lane, sources.get(lane))

    if case.get("history_class") == "synthetic" and case.get(
        "counts_toward_real_breakage_gate"
    ):
        raise CorpusError(f"{case_id}: synthetic case cannot count toward the gate")

    if adapter == "sdk-api" and case.get("counts_toward_real_breakage_gate"):
        _validate_sdk_downstream_provenance(case)


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
    validation = case.get("validation")
    validation_digest = digest(validation) if validation is not None else None

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
        "schema_version": "contract-history-receipt.v2",
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
    if validation_digest is not None:
        receipt["validation_digest"] = validation_digest
        receipt["validation_summary"] = {
            "old_ci_run_id": validation["old_ci"]["run_id"],
            "old_ci_head_sha": validation["old_ci"]["head_sha"],
            "old_ci_conclusion": validation["old_ci"]["conclusion"],
            "locked_package": validation["dependency_lock"]["package"],
            "locked_version": validation["dependency_lock"]["version"],
            "required_jobs": dict(sorted(validation["old_ci"]["jobs"].items())),
        }
    if unsupported_reason is not None:
        receipt["unsupported_reason"] = unsupported_reason
    return receipt


def compile_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema_version") != "contract-history-corpus.v2":
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
        "schema_version": "contract-history-corpus-receipt.v2",
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
