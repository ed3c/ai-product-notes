from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


class ClosureError(ValueError):
    """Raised when a closure packet would widen evidence or Shadow authority."""


SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
GIT_SHA_RE = re.compile(r"^[a-f0-9]{40}$")
LEVEL_ORDER = (
    "SOURCE_ANCHORED",
    "MECHANISM_BOUND",
    "IMPLEMENTED",
    "TECH_VERIFIED",
    "LIVE_WORKFLOW_VERIFIED",
    "USER_VALIDATED",
    "PAID_VALIDATED",
)
LEVEL_LANES = {
    "SOURCE_ANCHORED": "SOURCE",
    "MECHANISM_BOUND": "MECHANISM",
    "IMPLEMENTED": "IMPLEMENTATION",
    "TECH_VERIFIED": "IMPLEMENTATION",
    "LIVE_WORKFLOW_VERIFIED": "RUNTIME",
    "USER_VALIDATED": "USER",
    "PAID_VALIDATED": "COMMERCIAL",
}
EVIDENCE_STATES = {
    "PASS",
    "FAIL",
    "ABSENT",
    "NOT_IMPLEMENTED",
    "NOT_EXERCISED",
    "SKIPPED_BY_POLICY",
    "HUMAN_ADMIT_REQUIRED",
}
ANCHOR_KINDS = {
    "SOURCE_DOCUMENT",
    "ISSUE_RECORD",
    "MECHANISM_OBSERVATION",
    "CODE_SUBJECT",
    "DETERMINISTIC_SUITE",
    "CI_RUN",
    "LIVE_WORKFLOW_RUN",
    "USER_REPORT",
    "PAID_CONVERSION",
    "HUMAN_ADMISSION",
    "MODEL_JUDGMENT",
}
ALLOWED_KIND_BY_LEVEL = {
    "SOURCE_ANCHORED": {"SOURCE_DOCUMENT", "ISSUE_RECORD"},
    "MECHANISM_BOUND": {"MECHANISM_OBSERVATION"},
    "IMPLEMENTED": {"CODE_SUBJECT"},
    "TECH_VERIFIED": {"DETERMINISTIC_SUITE", "CI_RUN"},
    "LIVE_WORKFLOW_VERIFIED": {"LIVE_WORKFLOW_RUN"},
    "USER_VALIDATED": {"USER_REPORT"},
    "PAID_VALIDATED": {"PAID_CONVERSION", "HUMAN_ADMISSION"},
}
FORBIDDEN_PUBLIC_KEY_PARTS = {
    "credential",
    "secret",
    "token",
    "private_repository",
    "private_repo",
    "customer_data",
    "raw_session",
    "private_reasoning",
    "chain_of_thought",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest_json(value: Any, *, drop_key: str | None = None) -> str:
    payload = copy.deepcopy(value)
    if drop_key and isinstance(payload, dict):
        payload.pop(drop_key, None)
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("utf-8") + raw).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ClosureError(f"cannot load JSON {path}: {exc}") from exc


def _object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ClosureError(f"{where} must be an object")
    return value


def _array(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise ClosureError(f"{where} must be an array")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ClosureError(f"{where} must be a non-empty string")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], where: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        raise ClosureError(f"{where} missing keys: {', '.join(missing)}")
    if extra:
        raise ClosureError(f"{where} has unknown keys: {', '.join(extra)}")


def _scan_forbidden(value: Any, where: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized not in {"requests_private_reasoning", "contains_private_reasoning"} and any(
                part in normalized for part in FORBIDDEN_PUBLIC_KEY_PARTS
            ):
                raise ClosureError(f"forbidden public field at {where}.{key}")
            _scan_forbidden(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{where}[{index}]")


def validate_skills_binding(raw: Any) -> dict[str, Any]:
    binding = _object(raw, "skills_binding")
    _exact_keys(
        binding,
        {
            "schema_version",
            "repository",
            "commit",
            "tree_sha",
            "problem_matrix_schema",
            "audit_schema",
            "shadow_module",
            "authority_ceiling",
        },
        "skills_binding",
    )
    if binding["schema_version"] != "prel-skill-binding@1":
        raise ClosureError("skills binding schema version mismatch")
    if binding["repository"] != "ed3c/skills-shared":
        raise ClosureError("unexpected skills repository")
    for key in ("commit", "tree_sha"):
        if not GIT_SHA_RE.fullmatch(_text(binding[key], f"skills_binding.{key}")):
            raise ClosureError(f"skills_binding.{key} must be a full Git SHA")
    for key in ("problem_matrix_schema", "audit_schema", "shadow_module"):
        item = _object(binding[key], f"skills_binding.{key}")
        _exact_keys(item, {"path", "blob_sha"}, f"skills_binding.{key}")
        _text(item["path"], f"skills_binding.{key}.path")
        if not GIT_SHA_RE.fullmatch(_text(item["blob_sha"], f"skills_binding.{key}.blob_sha")):
            raise ClosureError(f"skills_binding.{key}.blob_sha must be a full Git SHA")
    if binding["authority_ceiling"] != "PORTABLE_METHOD_ONLY":
        raise ClosureError("skills binding authority widened")
    return binding


def validate_stage5_binding(raw: Any, packet: dict[str, Any], packet_bytes: bytes) -> dict[str, Any]:
    binding = _object(raw, "stage5_binding")
    _exact_keys(
        binding,
        {
            "schema_version",
            "repository",
            "pull_request",
            "head_sha",
            "path",
            "blob_sha",
            "packet_digest",
            "parent_dossier_digest",
            "hosted_run",
            "authority_ceiling",
        },
        "stage5_binding",
    )
    if binding["schema_version"] != "technical-systems-binding@1":
        raise ClosureError("stage5 binding schema version mismatch")
    if binding["repository"] != "ed3c/ai-product-notes":
        raise ClosureError("unexpected Stage 5 repository")
    for key in ("head_sha", "blob_sha"):
        if not GIT_SHA_RE.fullmatch(_text(binding[key], f"stage5_binding.{key}")):
            raise ClosureError(f"stage5_binding.{key} must be a full Git SHA")
    if not isinstance(binding["pull_request"], int) or binding["pull_request"] <= 0:
        raise ClosureError("stage5_binding.pull_request must be positive")
    if not isinstance(binding["hosted_run"], int) or binding["hosted_run"] <= 0:
        raise ClosureError("stage5_binding.hosted_run must be positive")
    if binding["authority_ceiling"] != "TECHNICAL_DESIGN_ONLY":
        raise ClosureError("Stage 5 binding authority widened")
    if git_blob_sha1(packet_bytes) != binding["blob_sha"]:
        raise ClosureError("Stage 5 packet Git blob mismatch")
    if packet.get("packet_digest") != f"sha256:{binding['packet_digest']}":
        raise ClosureError("Stage 5 packet digest mismatch")
    if digest_json(packet, drop_key="packet_digest") != binding["packet_digest"]:
        raise ClosureError("Stage 5 packet canonical digest mismatch")
    source_subject = _object(packet.get("source_subject"), "technical_packet.source_subject")
    if source_subject.get("dossier_digest") != f"sha256:{binding['parent_dossier_digest']}":
        raise ClosureError("Stage 4 dossier digest drift in Stage 5 packet")
    if packet.get("authority_ceiling") != "TECHNICAL_DESIGN_ONLY":
        raise ClosureError("technical packet authority must remain TECHNICAL_DESIGN_ONLY")
    if packet.get("decision") != "VALIDATE":
        raise ClosureError("technical packet decision must remain VALIDATE")
    states = _object(packet.get("evidence_state"), "technical_packet.evidence_state")
    if states.get("design") != "PASS":
        raise ClosureError("Stage 5 design evidence must PASS")
    for lane in ("implementation", "runtime", "user", "paid", "legal"):
        if states.get(lane) == "PASS":
            raise ClosureError(f"Stage 5 design packet cannot promote {lane} to PASS")
    return binding


def validate_plan(raw: Any) -> dict[str, Any]:
    plan = _object(raw, "closure_plan")
    _exact_keys(
        plan,
        {
            "schema_version",
            "subject_id",
            "surface",
            "captured_at",
            "problems",
            "matrix_rows",
            "evidence_ceiling",
            "issue_delta",
        },
        "closure_plan",
    )
    if plan["schema_version"] != "problem-closure-plan@1":
        raise ClosureError("closure plan schema version mismatch")
    _text(plan["subject_id"], "closure_plan.subject_id")
    _text(plan["surface"], "closure_plan.surface")
    _text(plan["captured_at"], "closure_plan.captured_at")
    problems = _array(plan["problems"], "closure_plan.problems")
    if not problems:
        raise ClosureError("closure plan needs at least one problem")
    seen_problem_ids: set[str] = set()
    for index, raw_problem in enumerate(problems):
        problem = _object(raw_problem, f"problem[{index}]")
        _exact_keys(
            problem,
            {
                "id",
                "statement",
                "declared_status",
                "rungs",
                "finding_specs",
            },
            f"problem[{index}]",
        )
        problem_id = _text(problem["id"], f"problem[{index}].id")
        if not re.fullmatch(r"PRB-[0-9]{3}", problem_id):
            raise ClosureError(f"invalid problem id: {problem_id}")
        if problem_id in seen_problem_ids:
            raise ClosureError(f"duplicate problem id: {problem_id}")
        seen_problem_ids.add(problem_id)
        _text(problem["statement"], f"problem[{index}].statement")
        declared = _object(problem["declared_status"], f"problem[{index}].declared_status")
        _exact_keys(declared, {"statement", "claimed_level", "anchor"}, f"problem[{index}].declared_status")
        _text(declared["statement"], "declared_status.statement")
        if declared["claimed_level"] not in LEVEL_ORDER + ("BLOCKED", "FAILED"):
            raise ClosureError("invalid claimed level")
        _validate_anchor(declared["anchor"], "declared_status.anchor")
        rungs = _array(problem["rungs"], f"problem[{index}].rungs")
        if len(rungs) != 7:
            raise ClosureError("each problem must define exactly seven rungs")
        for expected_level, raw_rung in zip(LEVEL_ORDER, rungs, strict=True):
            rung = _object(raw_rung, f"problem[{index}].rung[{expected_level}]")
            _exact_keys(rung, {"level", "state", "anchors", "note"}, f"problem[{index}].rung[{expected_level}]")
            if rung["level"] != expected_level:
                raise ClosureError("rung order mismatch")
            if rung["state"] not in EVIDENCE_STATES:
                raise ClosureError(f"invalid evidence state for {expected_level}")
            for anchor in _array(rung["anchors"], f"rung[{expected_level}].anchors"):
                _validate_anchor(anchor, f"rung[{expected_level}].anchor")
            if rung["state"] == "PASS" and not rung["anchors"]:
                raise ClosureError(f"PASS rung {expected_level} requires an anchor")
            if rung["state"] == "PASS":
                allowed = ALLOWED_KIND_BY_LEVEL[expected_level]
                if not any(anchor["kind"] in allowed for anchor in rung["anchors"]):
                    raise ClosureError(f"evidence lane promotion at {expected_level}")
            if rung["state"] != "PASS" and rung["anchors"]:
                raise ClosureError(f"non-PASS rung {expected_level} must not carry closing anchors")
            if not isinstance(rung["note"], str):
                raise ClosureError("rung.note must be a string")
        for finding in _array(problem["finding_specs"], f"problem[{index}].finding_specs"):
            _validate_finding(finding)
    _validate_matrix_rows(plan["matrix_rows"])
    _validate_issue_delta(plan["issue_delta"], seen_problem_ids)
    _validate_evidence_ceiling(plan["evidence_ceiling"])
    _scan_forbidden(plan)
    return plan


def _validate_anchor(raw: Any, where: str) -> dict[str, Any]:
    anchor = _object(raw, where)
    _exact_keys(anchor, {"kind", "locator", "observed", "exact_subject"}, where)
    if anchor["kind"] not in ANCHOR_KINDS:
        raise ClosureError(f"{where}.kind is invalid")
    _text(anchor["locator"], f"{where}.locator")
    _text(anchor["observed"], f"{where}.observed")
    subject = _object(anchor["exact_subject"], f"{where}.exact_subject")
    _exact_keys(subject, {"artifact", "digest"}, f"{where}.exact_subject")
    _text(subject["artifact"], f"{where}.exact_subject.artifact")
    if not SHA256_RE.fullmatch(_text(subject["digest"], f"{where}.exact_subject.digest")):
        raise ClosureError(f"{where}.exact_subject.digest must be sha256 hex")
    return anchor


def _validate_finding(raw: Any) -> None:
    finding = _object(raw, "finding")
    _exact_keys(finding, {"id", "code", "statement", "anchors", "proposed_repair"}, "finding")
    if not re.fullmatch(r"FND-[0-9]{3}", _text(finding["id"], "finding.id")):
        raise ClosureError("invalid finding id")
    if finding["code"] not in {
        "DECLARED_STATUS_AHEAD_OF_EVIDENCE",
        "LANE_SUBSTITUTION_OFFERED",
        "OBLIGATION_SKIPPED_AT_FIRST_GREEN",
        "SUBJECT_STALE",
        "EVIDENCE_ABSENT",
        "RIGHTS_UNADMITTED",
    }:
        raise ClosureError("invalid finding code")
    _text(finding["statement"], "finding.statement")
    anchors = _array(finding["anchors"], "finding.anchors")
    if not anchors:
        raise ClosureError("finding must have an anchor")
    for anchor in anchors:
        _validate_anchor(anchor, "finding.anchor")
    _text(finding["proposed_repair"], "finding.proposed_repair")


def _validate_matrix_rows(raw: Any) -> None:
    rows = _array(raw, "matrix_rows")
    if not rows:
        raise ClosureError("matrix rows must not be empty")
    seen: set[str] = set()
    for row in rows:
        item = _object(row, "matrix_row")
        _exact_keys(
            item,
            {
                "id",
                "source_id",
                "requirement",
                "lane",
                "oracle_id",
                "oracle_lane",
                "closure_state",
                "evidence_state",
                "owner",
            },
            "matrix_row",
        )
        row_id = _text(item["id"], "matrix_row.id")
        if not re.fullmatch(r"CLR-[0-9]{3}", row_id) or row_id in seen:
            raise ClosureError("invalid or duplicate matrix row id")
        seen.add(row_id)
        if item["lane"] not in {"DETERMINISTIC", "BEHAVIORAL", "USER", "PAID", "HUMAN_ADMIT"}:
            raise ClosureError("invalid matrix lane")
        if item["oracle_lane"] != item["lane"]:
            raise ClosureError("matrix oracle lane mismatch")
        if not isinstance(item["oracle_id"], str) or not re.fullmatch(r"ORC-[0-9]{3}", item["oracle_id"]):
            raise ClosureError("matrix row requires concrete oracle")
        if item["closure_state"] not in {
            "CLOSED_BY_ORACLE",
            "OPEN_WITH_ORACLE",
            "BLOCKED_NO_ORACLE",
            "BLOCKED_NOT_FALSIFIABLE",
            "BLOCKED_LANE_MISMATCH",
            "OUT_OF_SCOPE",
            "HUMAN_ADMIT_REQUIRED",
        }:
            raise ClosureError("invalid matrix closure state")
        if item["evidence_state"] not in EVIDENCE_STATES:
            raise ClosureError("invalid matrix evidence state")
        if item["closure_state"] == "CLOSED_BY_ORACLE" and item["evidence_state"] != "PASS":
            raise ClosureError("closed matrix row requires PASS evidence")
        if item["closure_state"] == "HUMAN_ADMIT_REQUIRED" and item["lane"] != "HUMAN_ADMIT":
            raise ClosureError("Human admit matrix row must use HUMAN_ADMIT lane")


def _validate_issue_delta(raw: Any, problem_ids: set[str]) -> None:
    items = _array(raw, "issue_delta")
    seen: set[str] = set()
    for item_raw in items:
        item = _object(item_raw, "issue_delta_item")
        _exact_keys(item, {"id", "problem_id", "action", "statement"}, "issue_delta_item")
        delta_id = _text(item["id"], "issue_delta.id")
        if not re.fullmatch(r"DLT-[0-9]{3}", delta_id) or delta_id in seen:
            raise ClosureError("invalid or duplicate issue delta id")
        seen.add(delta_id)
        if item["problem_id"] not in problem_ids:
            raise ClosureError("issue delta references unknown problem")
        if item["action"] not in {"PROPOSE_OPEN", "PROPOSE_UPDATE", "PROPOSE_REOPEN", "PROPOSE_BLOCKED_NOTE"}:
            raise ClosureError("invalid issue delta action")
        _text(item["statement"], "issue_delta.statement")


def _validate_evidence_ceiling(raw: Any) -> None:
    ceiling = _object(raw, "evidence_ceiling")
    _exact_keys(
        ceiling,
        {
            "portable_procedure",
            "deterministic_contract",
            "product_market_fit",
            "live_provider_execution",
            "production_readiness",
        },
        "evidence_ceiling",
    )
    for key, value in ceiling.items():
        if value not in EVIDENCE_STATES:
            raise ClosureError(f"invalid evidence ceiling state: {key}")


def highest_earned(rungs: list[dict[str, Any]]) -> str:
    earned: str | None = None
    for expected_level, rung in zip(LEVEL_ORDER, rungs, strict=True):
        if rung["level"] != expected_level:
            raise ClosureError("rung order mismatch")
        if rung["state"] == "FAIL":
            return "FAILED"
        if rung["state"] != "PASS":
            break
        earned = expected_level
    return earned or "BLOCKED"


def compile_outputs(
    plan_raw: Any,
    skills_binding_raw: Any,
    stage5_binding_raw: Any,
    technical_packet_raw: Any,
    technical_packet_bytes: bytes,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    plan = validate_plan(plan_raw)
    skills_binding = validate_skills_binding(skills_binding_raw)
    stage5_binding = validate_stage5_binding(stage5_binding_raw, technical_packet_raw, technical_packet_bytes)

    problems: list[dict[str, Any]] = []
    reopened: list[dict[str, Any]] = []
    finding_count = 0
    for raw_problem in plan["problems"]:
        rungs = []
        for raw_rung in raw_problem["rungs"]:
            rung = {
                "level": raw_rung["level"],
                "lane": LEVEL_LANES[raw_rung["level"]],
                "state": raw_rung["state"],
                "anchors": copy.deepcopy(raw_rung["anchors"]),
            }
            if raw_rung["note"]:
                rung["note"] = raw_rung["note"]
            rungs.append(rung)
            if raw_rung["state"] in {"NOT_IMPLEMENTED", "NOT_EXERCISED", "SKIPPED_BY_POLICY"}:
                reopened.append(
                    {
                        "problem_id": raw_problem["id"],
                        "level": raw_rung["level"],
                        "state": raw_rung["state"],
                        "reason": raw_rung["note"] or "the proof obligation remains explicitly unexercised",
                    }
                )
        computed = highest_earned(rungs)
        findings = []
        for spec in raw_problem["finding_specs"]:
            finding_count += 1
            findings.append(
                {
                    **copy.deepcopy(spec),
                    "authority": "FINDINGS_ONLY",
                }
            )
        claimed = raw_problem["declared_status"]["claimed_level"]
        if claimed in LEVEL_ORDER and computed in LEVEL_ORDER:
            if LEVEL_ORDER.index(claimed) > LEVEL_ORDER.index(computed):
                finding_count += 1
                findings.append(
                    {
                        "id": f"FND-{finding_count:03d}",
                        "code": "DECLARED_STATUS_AHEAD_OF_EVIDENCE",
                        "statement": f"Declared level {claimed} is ahead of computed level {computed}.",
                        "anchors": [copy.deepcopy(raw_problem["declared_status"]["anchor"])],
                        "proposed_repair": "Lower the declaration or supply exact evidence for every missing rung in the correct lane.",
                        "authority": "FINDINGS_ONLY",
                    }
                )
        missing_lanes = []
        seen_lanes: set[str] = set()
        for rung in rungs:
            if rung["state"] != "PASS" and rung["lane"] not in seen_lanes:
                missing_lanes.append(rung["lane"])
                seen_lanes.add(rung["lane"])
        problems.append(
            {
                "id": raw_problem["id"],
                "statement": raw_problem["statement"],
                "declared_status": copy.deepcopy(raw_problem["declared_status"]),
                "highest_earned_level": computed,
                "missing_lanes": missing_lanes,
                "levels": rungs,
                "findings": findings,
            }
        )

    issue_delta = [
        {**copy.deepcopy(item), "write_authority": "NO_WRITE_AUTHORITY"}
        for item in plan["issue_delta"]
    ]
    audit = {
        "schema": "prel/product-closure-audit/v1",
        "reviewer": {
            "identity": "shadow-product-closure-ai-product-notes-stage6",
            "mode": "READ_ONLY_FINDINGS_ONLY",
            "writes_implementation": False,
            "requires_prior_conversation": False,
            "requests_private_reasoning": False,
        },
        "audit_subject": {
            "subject_id": plan["subject_id"],
            "surface": plan["surface"],
            "captured_at": plan["captured_at"],
            "subject_revision": stage5_binding["head_sha"],
            "compared_surfaces": [
                stage5_binding["path"],
                "evals/reverse-engineering/modern-web-architecture/dossier.json",
                skills_binding["problem_matrix_schema"]["path"],
                skills_binding["audit_schema"]["path"],
                skills_binding["shadow_module"]["path"],
                "GitHub Actions run 32271087668",
            ],
        },
        "external_authority": {
            "merge": "HUMAN_ADMIT_REQUIRED",
            "release": "HUMAN_ADMIT_REQUIRED",
            "rights": "HUMAN_ADMIT_REQUIRED",
            "customer_truth": "HUMAN_ADMIT_REQUIRED",
            "commercial": "HUMAN_ADMIT_REQUIRED",
        },
        "problems": problems,
        "reopened_obligations": reopened,
        "review_denominator": {
            "findings_raised": sum(len(problem["findings"]) for problem in problems),
            "findings_reported": sum(len(problem["findings"]) for problem in problems),
            "findings_withdrawn": [],
        },
        "issue_delta": issue_delta,
        "public_snapshot": {
            "contains_private_reasoning": False,
            "consumable_without_prior_conversation": True,
            "completion_meaning": "REVIEW_ONLY_NOT_MERGE_OR_RELEASE",
            "excluded_from_snapshot": [
                "private chain of thought",
                "credentials and secrets",
                "private repository metadata",
                "customer data",
            ],
        },
        "evidence_ceiling": copy.deepcopy(plan["evidence_ceiling"]),
    }

    matrix_subject_digest = digest_json(
        {
            "stage5_packet_digest": stage5_binding["packet_digest"],
            "skills_commit": skills_binding["commit"],
            "plan_digest": digest_json(plan),
        }
    )
    matrix = {
        "schema": "prel/problem-closure-matrix/v1",
        "subject": {
            "product_id": plan["subject_id"],
            "surface": plan["surface"],
            "captured_at": plan["captured_at"],
            "subject_digest": matrix_subject_digest,
        },
        "derived_from": {
            "artifact": technical_packet_raw["packet_id"],
            "digest": stage5_binding["packet_digest"],
        },
        "rows": copy.deepcopy(plan["matrix_rows"]),
        "evidence_ceiling": copy.deepcopy(plan["evidence_ceiling"]),
    }
    delta = {
        "schema_version": "problem-closure-issue-delta@1",
        "source_audit_digest": digest_json(audit),
        "items": issue_delta,
        "write_authority": "NO_WRITE_AUTHORITY",
        "human_admit_required": True,
    }

    validate_audit(audit)
    validate_matrix(matrix)
    validate_delta(delta, audit)
    return matrix, audit, delta


def validate_audit(audit_raw: Any) -> dict[str, Any]:
    audit = _object(audit_raw, "audit")
    required = {
        "schema",
        "reviewer",
        "audit_subject",
        "external_authority",
        "problems",
        "reopened_obligations",
        "review_denominator",
        "issue_delta",
        "public_snapshot",
        "evidence_ceiling",
    }
    _exact_keys(audit, required, "audit")
    if audit["schema"] != "prel/product-closure-audit/v1":
        raise ClosureError("audit schema mismatch")
    reviewer = _object(audit["reviewer"], "audit.reviewer")
    if reviewer != {
        "identity": reviewer.get("identity"),
        "mode": "READ_ONLY_FINDINGS_ONLY",
        "writes_implementation": False,
        "requires_prior_conversation": False,
        "requests_private_reasoning": False,
    }:
        raise ClosureError("Shadow reviewer authority widened")
    _text(reviewer["identity"], "reviewer.identity")
    authority = _object(audit["external_authority"], "audit.external_authority")
    for key in ("merge", "release", "rights", "customer_truth", "commercial"):
        if authority.get(key) != "HUMAN_ADMIT_REQUIRED":
            raise ClosureError(f"external authority widened: {key}")
    problems = _array(audit["problems"], "audit.problems")
    if not problems:
        raise ClosureError("audit requires problems")
    finding_total = 0
    for problem in problems:
        levels = _array(problem.get("levels"), "audit.problem.levels")
        if len(levels) != 7:
            raise ClosureError("audit problem must contain seven levels")
        if problem.get("highest_earned_level") != highest_earned(levels):
            raise ClosureError("highest earned level mismatch")
        finding_total += len(_array(problem.get("findings"), "audit.problem.findings"))
        for rung in levels:
            if rung["state"] == "PASS":
                allowed = ALLOWED_KIND_BY_LEVEL[rung["level"]]
                if not any(anchor["kind"] in allowed for anchor in rung["anchors"]):
                    raise ClosureError("audit evidence lane promotion")
    denominator = _object(audit["review_denominator"], "review_denominator")
    if denominator.get("findings_raised") != finding_total or denominator.get("findings_reported") != finding_total:
        raise ClosureError("review denominator mismatch")
    if denominator.get("findings_withdrawn") != []:
        raise ClosureError("withdrawn findings require an explicit product-specific policy not present in this canary")
    public = _object(audit["public_snapshot"], "public_snapshot")
    if public.get("contains_private_reasoning") is not False:
        raise ClosureError("public snapshot contains private reasoning")
    if public.get("consumable_without_prior_conversation") is not True:
        raise ClosureError("audit requires prior conversation")
    if public.get("completion_meaning") != "REVIEW_ONLY_NOT_MERGE_OR_RELEASE":
        raise ClosureError("audit completion widened to merge/release")
    _validate_evidence_ceiling(audit["evidence_ceiling"])
    _scan_forbidden(audit)
    return audit


def validate_matrix(matrix_raw: Any) -> dict[str, Any]:
    matrix = _object(matrix_raw, "matrix")
    _exact_keys(matrix, {"schema", "subject", "derived_from", "rows", "evidence_ceiling"}, "matrix")
    if matrix["schema"] != "prel/problem-closure-matrix/v1":
        raise ClosureError("matrix schema mismatch")
    subject = _object(matrix["subject"], "matrix.subject")
    _exact_keys(subject, {"product_id", "surface", "captured_at", "subject_digest"}, "matrix.subject")
    if not SHA256_RE.fullmatch(_text(subject["subject_digest"], "subject_digest")):
        raise ClosureError("matrix subject digest invalid")
    derived = _object(matrix["derived_from"], "matrix.derived_from")
    _exact_keys(derived, {"artifact", "digest"}, "matrix.derived_from")
    if not SHA256_RE.fullmatch(_text(derived["digest"], "derived_from.digest")):
        raise ClosureError("matrix derived digest invalid")
    _validate_matrix_rows(matrix["rows"])
    _validate_evidence_ceiling(matrix["evidence_ceiling"])
    _scan_forbidden(matrix)
    return matrix


def validate_delta(delta_raw: Any, audit: dict[str, Any]) -> dict[str, Any]:
    delta = _object(delta_raw, "delta")
    _exact_keys(
        delta,
        {"schema_version", "source_audit_digest", "items", "write_authority", "human_admit_required"},
        "delta",
    )
    if delta["schema_version"] != "problem-closure-issue-delta@1":
        raise ClosureError("delta schema mismatch")
    if delta["source_audit_digest"] != digest_json(audit):
        raise ClosureError("delta audit digest mismatch")
    if delta["write_authority"] != "NO_WRITE_AUTHORITY" or delta["human_admit_required"] is not True:
        raise ClosureError("issue delta authority widened")
    if delta["items"] != audit["issue_delta"]:
        raise ClosureError("issue delta diverges from audit")
    _scan_forbidden(delta)
    return delta
