#!/usr/bin/env python3
"""Compile a source-bound MCP Registry publisher schema-revision receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_CI_JOBS = ("Build, Lint, and Validate", "Tests")
REQUIRED_SOURCE_LANES = (
    "old_publisher",
    "new_publisher",
    "old_test",
    "new_test",
    "old_schema",
    "new_schema",
    "workflow",
    "change",
)
COUNTED_REASON = "schema_revision_not_admitted"
STATUS_FINDING_ID = "publisher-status-removal"


class PublisherHistoryError(ValueError):
    """Raised when the publisher-history evidence violates an invariant."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _require_immutable_binding(case_id: str, lane: str, source: Any) -> None:
    if not isinstance(source, dict):
        raise PublisherHistoryError(f"{case_id}: missing source lane {lane}")
    for field in ("repository", "commit", "path", "blob_sha"):
        if not source.get(field):
            raise PublisherHistoryError(f"{case_id}: {lane} source missing {field}")
    if len(str(source["commit"])) != 40 or len(str(source["blob_sha"])) != 40:
        raise PublisherHistoryError(f"{case_id}: {lane} source is not immutable")


def _evaluate_revision(contract: dict[str, Any], schema_uri: str) -> dict[str, Any]:
    revision = contract.get("admitted_revision")
    if not isinstance(revision, str) or not revision:
        raise PublisherHistoryError("publisher contract admitted_revision is absent")
    if schema_uri == "" or revision in schema_uri:
        return {"status": "PASS", "reasons": []}
    return {
        "status": "FAIL",
        "reasons": [
            {
                "reason": COUNTED_REASON,
                "expected_revision": revision,
                "observed_schema": schema_uri,
            }
        ],
    }


def _validate_ci(
    case_id: str,
    lane: str,
    ci: Any,
    expected_head: str,
    workflow: dict[str, Any],
) -> None:
    if not isinstance(ci, dict):
        raise PublisherHistoryError(f"{case_id}: missing {lane}")
    if not isinstance(ci.get("run_id"), int) or ci["run_id"] <= 0:
        raise PublisherHistoryError(f"{case_id}: {lane} run_id must be positive")
    if ci.get("head_sha") != expected_head:
        raise PublisherHistoryError(f"{case_id}: {lane} head does not bind contract")
    if ci.get("workflow_path") != workflow["path"]:
        raise PublisherHistoryError(f"{case_id}: {lane} workflow path drift")
    if ci.get("workflow_blob_sha") != workflow["blob_sha"]:
        raise PublisherHistoryError(f"{case_id}: {lane} workflow blob drift")
    if ci.get("conclusion") != "success":
        raise PublisherHistoryError(f"{case_id}: {lane} must conclude success")
    jobs = ci.get("jobs")
    if not isinstance(jobs, dict):
        raise PublisherHistoryError(f"{case_id}: {lane} jobs must be an object")
    for job_name in REQUIRED_CI_JOBS:
        if jobs.get(job_name) != "success":
            raise PublisherHistoryError(
                f"{case_id}: required {lane} job is not successful: {job_name}"
            )


def _validate_negative_findings(case: dict[str, Any]) -> None:
    case_id = case["case_id"]
    findings = case.get("negative_findings")
    if not isinstance(findings, list):
        raise PublisherHistoryError(f"{case_id}: negative_findings must be a list")
    status = next(
        (item for item in findings if item.get("finding_id") == STATUS_FINDING_ID),
        None,
    )
    if not isinstance(status, dict):
        raise PublisherHistoryError(f"{case_id}: status-removal negative finding absent")
    if status.get("disposition") != "NOT_COUNTED":
        raise PublisherHistoryError(f"{case_id}: status removal must remain NOT_COUNTED")
    if status.get("reason") != "go_json_unmarshal_does_not_prove_unknown_field_rejection":
        raise PublisherHistoryError(f"{case_id}: status-removal reason drift")


def _validate_case(case: dict[str, Any]) -> None:
    if case.get("schema_version") != "publisher-schema-revision-case.v1":
        raise PublisherHistoryError("unsupported publisher case schema_version")
    case_id = case.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise PublisherHistoryError("case_id must be a non-empty string")
    if case.get("adapter") != "registry-publisher-schema-revision":
        raise PublisherHistoryError(f"{case_id}: adapter identity drift")
    if case.get("history_class") != "public_real_history":
        raise PublisherHistoryError(f"{case_id}: only public real history may count")
    if case.get("evidence_basis") == "changelog_only":
        raise PublisherHistoryError(f"{case_id}: changelog prose cannot prove breakage")
    if case.get("counts_toward_real_breakage_gate") is not True:
        raise PublisherHistoryError(f"{case_id}: counted extension must request admission")

    sources = case.get("sources")
    if not isinstance(sources, dict):
        raise PublisherHistoryError(f"{case_id}: sources must be an object")
    for lane in REQUIRED_SOURCE_LANES:
        _require_immutable_binding(case_id, lane, sources.get(lane))

    old_publisher = sources["old_publisher"]
    new_publisher = sources["new_publisher"]
    old_test = sources["old_test"]
    new_test = sources["new_test"]
    workflow = sources["workflow"]
    change = sources["change"]

    if old_test["repository"] != old_publisher["repository"] or old_test["commit"] != old_publisher["commit"]:
        raise PublisherHistoryError(f"{case_id}: old test is not bound to old publisher")
    if new_test["repository"] != new_publisher["repository"] or new_test["commit"] != new_publisher["commit"]:
        raise PublisherHistoryError(f"{case_id}: new test is not bound to new publisher")
    if change["repository"] != new_publisher["repository"] or change["commit"] != new_publisher["commit"]:
        raise PublisherHistoryError(f"{case_id}: change source is not bound to new publisher")
    pull_request = change.get("pull_request")
    if not isinstance(pull_request, int) or pull_request <= 0:
        raise PublisherHistoryError(f"{case_id}: change pull_request must be positive")
    expected_event = f"{change['repository']}#{pull_request}"
    if case.get("change_event_id") != expected_event:
        raise PublisherHistoryError(f"{case_id}: change_event_id drift")

    old_contract = case.get("old_contract")
    new_contract = case.get("new_contract")
    consumer = case.get("consumer")
    if not isinstance(old_contract, dict) or not isinstance(new_contract, dict):
        raise PublisherHistoryError(f"{case_id}: publisher contracts are absent")
    if not isinstance(consumer, dict) or not isinstance(consumer.get("schema_uri"), str):
        raise PublisherHistoryError(f"{case_id}: historical consumer schema_uri absent")

    if not sources["old_schema"]["path"].endswith(
        f"/{old_contract.get('admitted_revision')}/server.schema.json"
    ):
        raise PublisherHistoryError(f"{case_id}: old schema path/revision drift")
    if not sources["new_schema"]["path"].endswith(
        f"/{new_contract.get('admitted_revision')}/server.schema.json"
    ):
        raise PublisherHistoryError(f"{case_id}: new schema path/revision drift")
    if consumer["schema_uri"] != old_contract.get("schema_uri"):
        raise PublisherHistoryError(f"{case_id}: consumer must bind old schema URI")

    adjudication = case.get("adjudication")
    if not isinstance(adjudication, dict):
        raise PublisherHistoryError(f"{case_id}: adjudication absent")
    if adjudication.get("consumer_class") != "upstream_test_fixture":
        raise PublisherHistoryError(f"{case_id}: consumer class is not countable")
    if adjudication.get("counted_reason") != COUNTED_REASON:
        raise PublisherHistoryError(f"{case_id}: counted reason must be {COUNTED_REASON}")
    if adjudication.get("expected_old") != "PASS" or adjudication.get("expected_new") != "FAIL":
        raise PublisherHistoryError(f"{case_id}: adjudication expectation drift")

    validation = case.get("validation")
    if not isinstance(validation, dict):
        raise PublisherHistoryError(f"{case_id}: validation bundle absent")
    _validate_ci(
        case_id,
        "old_ci",
        validation.get("old_ci"),
        old_publisher["commit"],
        workflow,
    )
    _validate_ci(
        case_id,
        "new_ci",
        validation.get("new_ci"),
        new_publisher["commit"],
        workflow,
    )
    _validate_negative_findings(case)


def compile_case(case: dict[str, Any]) -> dict[str, Any]:
    _validate_case(case)
    consumer_schema = case["consumer"]["schema_uri"]
    old_result = _evaluate_revision(case["old_contract"], consumer_schema)
    new_result = _evaluate_revision(case["new_contract"], consumer_schema)
    if old_result["status"] != "PASS" or new_result["status"] != "FAIL":
        raise PublisherHistoryError(
            f"{case['case_id']}: counted history must be old PASS and new FAIL"
        )
    reasons = [item.get("reason") for item in new_result["reasons"]]
    if reasons != [COUNTED_REASON]:
        raise PublisherHistoryError(f"{case['case_id']}: new failure reason drift")

    controls = {
        "old_empty_schema": _evaluate_revision(case["old_contract"], ""),
        "old_current_schema": _evaluate_revision(
            case["old_contract"], case["old_contract"]["schema_uri"]
        ),
        "new_empty_schema": _evaluate_revision(case["new_contract"], ""),
        "new_current_schema": _evaluate_revision(
            case["new_contract"], case["new_contract"]["schema_uri"]
        ),
    }
    if any(result["status"] != "PASS" for result in controls.values()):
        raise PublisherHistoryError(f"{case['case_id']}: admitted controls must pass")

    validation = case["validation"]
    receipt: dict[str, Any] = {
        "schema_version": "publisher-schema-revision-receipt.v1",
        "case_id": case["case_id"],
        "change_event_id": case["change_event_id"],
        "adapter": case["adapter"],
        "history_class": case["history_class"],
        "decision": "HISTORICAL_BREAKAGE",
        "counts_toward_real_breakage_gate": True,
        "source_digests": {
            lane: digest(case["sources"][lane]) for lane in REQUIRED_SOURCE_LANES
        },
        "contract_digests": {
            "old_contract": digest(case["old_contract"]),
            "new_contract": digest(case["new_contract"]),
        },
        "consumer_digest": digest(case["consumer"]),
        "validation_digest": digest(validation),
        "old_result": old_result,
        "new_result": new_result,
        "controls": controls,
        "validation_summary": {
            "old_ci": {
                "run_id": validation["old_ci"]["run_id"],
                "head_sha": validation["old_ci"]["head_sha"],
                "conclusion": validation["old_ci"]["conclusion"],
                "jobs": dict(sorted(validation["old_ci"]["jobs"].items())),
            },
            "new_ci": {
                "run_id": validation["new_ci"]["run_id"],
                "head_sha": validation["new_ci"]["head_sha"],
                "conclusion": validation["new_ci"]["conclusion"],
                "jobs": dict(sorted(validation["new_ci"]["jobs"].items())),
            },
            "workflow_blob_sha": case["sources"]["workflow"]["blob_sha"],
        },
        "negative_findings": case["negative_findings"],
        "adjudication": case["adjudication"],
    }
    receipt["receipt_digest"] = digest(receipt)
    return receipt


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PublisherHistoryError(f"{path} must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)

    try:
        compiled = compile_case(load_json(args.case))
    except (PublisherHistoryError, json.JSONDecodeError, OSError) as error:
        print(f"publisher-schema-history: FAIL: {error}", file=sys.stderr)
        return 1

    rendered = canonical_bytes(compiled)
    if args.check:
        try:
            committed = args.check.read_bytes()
        except OSError as error:
            print(f"publisher-schema-history: FAIL: {error}", file=sys.stderr)
            return 1
        if committed != rendered:
            print("publisher-schema-history: FAIL: committed receipt drift", file=sys.stderr)
            return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(rendered)
    elif not args.check:
        sys.stdout.buffer.write(rendered)

    print(
        "publisher-schema-history: PASS "
        f"case={compiled['case_id']} digest={compiled['receipt_digest']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
