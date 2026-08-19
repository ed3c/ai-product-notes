from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


class DossierError(ValueError):
    """Raised when a reverse-engineering packet would weaken evidence boundaries."""


SHA256_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
GIT_SHA_RE = re.compile(r"^[a-f0-9]{40}$")
SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{1,191}$")
USER_FIELDS = (
    "target_user",
    "economic_buyer",
    "trigger",
    "job_to_be_done",
    "pain",
    "frequency",
    "cost",
    "current_workaround",
)
BUSINESS_FIELDS = ("distribution", "monetization", "retention", "defensibility")
FORBIDDEN_KEY_PARTS = {
    "credential",
    "secret",
    "token",
    "private_repository",
    "private_repo",
    "customer_data",
    "raw_session",
    "private_note_body",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest_json(value: Any, *, drop_key: str | None = None) -> str:
    payload = copy.deepcopy(value)
    if drop_key and isinstance(payload, dict):
        payload.pop(drop_key, None)
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("utf-8")
    return hashlib.sha1(header + raw).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DossierError(f"cannot load JSON {path}: {exc}") from exc


def _object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DossierError(f"{where} must be an object")
    return value


def _array(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise DossierError(f"{where} must be an array")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DossierError(f"{where} must be a non-empty string")
    return value


def _id(value: Any, where: str) -> str:
    text = _text(value, where)
    if not SAFE_ID_RE.fullmatch(text):
        raise DossierError(f"{where} has an invalid identifier")
    return text


def _exact_keys(value: dict[str, Any], expected: set[str], where: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        raise DossierError(f"{where} missing keys: {', '.join(missing)}")
    if extra:
        raise DossierError(f"{where} has unknown keys: {', '.join(extra)}")


def _nonempty_text_list(value: Any, where: str) -> list[str]:
    values = _array(value, where)
    if not values:
        raise DossierError(f"{where} must not be empty")
    result: list[str] = []
    for index, item in enumerate(values):
        result.append(_text(item, f"{where}[{index}]"))
    return result


def _scan_forbidden(value: Any, where: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(part in normalized for part in FORBIDDEN_KEY_PARTS):
                raise DossierError(f"forbidden public export field at {where}.{key}")
            _scan_forbidden(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{where}[{index}]")


def validate_product_signal(raw: Any) -> dict[str, Any]:
    packet = _object(raw, "product_signal")
    required = {
        "authority_ceiling",
        "claims_digest",
        "contradictions_digest",
        "decision",
        "evidence_digest",
        "evidence_state",
        "non_claims",
        "product_signal_digest",
        "schema_version",
        "signal_set_id",
        "signals",
        "source_binding",
        "unknown_claims",
        "unresolved_contradictions",
    }
    _exact_keys(packet, required, "product_signal")
    if packet["schema_version"] != "product-signal@1":
        raise DossierError("product_signal.schema_version must be product-signal@1")
    if packet["authority_ceiling"] != "SOURCE_EVIDENCE_ONLY":
        raise DossierError("product_signal authority must remain SOURCE_EVIDENCE_ONLY")
    if packet["decision"] != "VALIDATE":
        raise DossierError("Stage 4 canary accepts only a VALIDATE product signal")
    for key in ("claims_digest", "contradictions_digest", "evidence_digest", "product_signal_digest"):
        if not SHA256_RE.fullmatch(_text(packet[key], f"product_signal.{key}")):
            raise DossierError(f"product_signal.{key} is not a sha256 digest")
    expected_digest = digest_json(packet, drop_key="product_signal_digest")
    if packet["product_signal_digest"] != expected_digest:
        raise DossierError("product_signal digest mismatch")

    evidence_state = _object(packet["evidence_state"], "product_signal.evidence_state")
    _exact_keys(evidence_state, {"source", "runtime", "user", "paid", "legal"}, "product_signal.evidence_state")
    if evidence_state["source"] != "PASS":
        raise DossierError("source evidence must PASS before dossier compilation")
    for key in ("runtime", "user", "paid", "legal"):
        if evidence_state[key] not in {"PASS", "FAIL", "ABSENT", "NOT_EXERCISED"}:
            raise DossierError(f"invalid evidence state: {key}")

    source_binding = _object(packet["source_binding"], "product_signal.source_binding")
    _exact_keys(source_binding, {"source_id", "source_digest", "registry_digest", "dependency_key"}, "product_signal.source_binding")
    for key in ("source_digest", "registry_digest"):
        if not SHA256_RE.fullmatch(_text(source_binding[key], f"source_binding.{key}")):
            raise DossierError(f"source_binding.{key} is invalid")
    _text(source_binding["source_id"], "source_binding.source_id")
    _text(source_binding["dependency_key"], "source_binding.dependency_key")

    signal_ids: set[str] = set()
    claim_ids: set[str] = set()
    for index, raw_signal in enumerate(_array(packet["signals"], "product_signal.signals")):
        signal = _object(raw_signal, f"product_signal.signals[{index}]")
        _exact_keys(signal, {"signal_id", "signal_class", "title", "claim_ids", "open_gaps", "authority_ceiling"}, f"product_signal.signals[{index}]")
        signal_id = _id(signal["signal_id"], f"signal[{index}].signal_id")
        if signal_id in signal_ids:
            raise DossierError(f"duplicate signal id: {signal_id}")
        signal_ids.add(signal_id)
        if signal["authority_ceiling"] != "SOURCE_EVIDENCE_ONLY":
            raise DossierError("signal authority widened")
        _text(signal["signal_class"], f"signal[{index}].signal_class")
        _text(signal["title"], f"signal[{index}].title")
        for claim in _nonempty_text_list(signal["claim_ids"], f"signal[{index}].claim_ids"):
            claim_ids.add(claim)
        for gap in _array(signal["open_gaps"], f"signal[{index}].open_gaps"):
            _text(gap, f"signal[{index}].open_gaps[]")

    unknown_claims = _nonempty_text_list(packet["unknown_claims"], "product_signal.unknown_claims")
    _nonempty_text_list(packet["unresolved_contradictions"], "product_signal.unresolved_contradictions")
    if not set(unknown_claims).issubset(claim_ids):
        raise DossierError("unknown claims must resolve to signal claim ids")
    _nonempty_text_list(packet["non_claims"], "product_signal.non_claims")
    _scan_forbidden(packet, "product_signal")
    return packet


def validate_external_binding(raw: Any, product_signal: dict[str, Any], snapshot_bytes: bytes) -> dict[str, Any]:
    binding = _object(raw, "external_binding")
    expected = {
        "schema_version",
        "repository",
        "pull_request",
        "head_sha",
        "path",
        "blob_sha",
        "product_signal_digest",
        "source_digest",
        "authority_ceiling",
    }
    _exact_keys(binding, expected, "external_binding")
    if binding["schema_version"] != "external-product-signal-binding@1":
        raise DossierError("external binding schema version mismatch")
    if binding["repository"] != "ed3c/ai-content-notes":
        raise DossierError("unexpected product signal repository")
    if not isinstance(binding["pull_request"], int) or binding["pull_request"] <= 0:
        raise DossierError("external_binding.pull_request must be positive")
    if not GIT_SHA_RE.fullmatch(_text(binding["head_sha"], "external_binding.head_sha")):
        raise DossierError("external binding head SHA is invalid")
    if not GIT_SHA_RE.fullmatch(_text(binding["blob_sha"], "external_binding.blob_sha")):
        raise DossierError("external binding blob SHA is invalid")
    _text(binding["path"], "external_binding.path")
    if binding["authority_ceiling"] != "SOURCE_EVIDENCE_ONLY":
        raise DossierError("external binding authority widened")
    if binding["product_signal_digest"] != product_signal["product_signal_digest"]:
        raise DossierError("external binding product signal digest mismatch")
    if binding["source_digest"] != product_signal["source_binding"]["source_digest"]:
        raise DossierError("external binding source digest mismatch")
    if git_blob_sha1(snapshot_bytes) != binding["blob_sha"]:
        raise DossierError("local product signal snapshot does not match exact Git blob")
    return binding


def _validate_epistemic_item(raw: Any, where: str, allowed_states: set[str]) -> dict[str, Any]:
    item = _object(raw, where)
    _exact_keys(item, {"statement", "epistemic_state", "required_evidence"}, where)
    _text(item["statement"], f"{where}.statement")
    if item["epistemic_state"] not in allowed_states:
        raise DossierError(f"{where}.epistemic_state is not allowed")
    _nonempty_text_list(item["required_evidence"], f"{where}.required_evidence")
    return item


def validate_hypotheses(raw: Any, product_signal: dict[str, Any]) -> dict[str, Any]:
    hypotheses = _object(raw, "hypotheses")
    expected = {
        "schema_version",
        "hypothesis_set_id",
        "target",
        "user_context",
        "workflow",
        "mechanisms",
        "capabilities",
        "business",
        "riskiest_assumptions",
        "mvp",
    }
    _exact_keys(hypotheses, expected, "hypotheses")
    if hypotheses["schema_version"] != "reverse-engineering-hypotheses@1":
        raise DossierError("hypotheses schema version mismatch")
    _id(hypotheses["hypothesis_set_id"], "hypothesis_set_id")

    target = _object(hypotheses["target"], "hypotheses.target")
    _exact_keys(target, {"subject_id", "title", "kind"}, "hypotheses.target")
    _id(target["subject_id"], "hypotheses.target.subject_id")
    _text(target["title"], "hypotheses.target.title")
    if target["kind"] not in {"PRODUCT_PATTERN", "PRODUCT_HYPOTHESIS"}:
        raise DossierError("hypotheses.target.kind is invalid")

    user_context = _object(hypotheses["user_context"], "hypotheses.user_context")
    _exact_keys(user_context, set(USER_FIELDS), "hypotheses.user_context")
    for field in USER_FIELDS:
        _validate_epistemic_item(user_context[field], f"hypotheses.user_context.{field}", {"HYPOTHESIS", "UNKNOWN"})

    signal_by_id = {signal["signal_id"]: signal for signal in product_signal["signals"]}
    workflow = _array(hypotheses["workflow"], "hypotheses.workflow")
    if len(workflow) < 3:
        raise DossierError("workflow requires at least three explicit steps")
    seen_steps: set[str] = set()
    for index, raw_step in enumerate(workflow):
        step = _object(raw_step, f"hypotheses.workflow[{index}]")
        _exact_keys(step, {"step_id", "title", "epistemic_state", "signal_refs", "required_evidence"}, f"hypotheses.workflow[{index}]")
        step_id = _id(step["step_id"], f"workflow[{index}].step_id")
        if step_id in seen_steps:
            raise DossierError(f"duplicate workflow step: {step_id}")
        seen_steps.add(step_id)
        _text(step["title"], f"workflow[{index}].title")
        if step["epistemic_state"] not in {"SOURCE_STATEMENT", "HYPOTHESIS", "UNKNOWN"}:
            raise DossierError("workflow epistemic state is invalid")
        for signal_ref in _nonempty_text_list(step["signal_refs"], f"workflow[{index}].signal_refs"):
            if signal_ref not in signal_by_id:
                raise DossierError(f"workflow references unknown signal: {signal_ref}")
        _nonempty_text_list(step["required_evidence"], f"workflow[{index}].required_evidence")

    mechanisms = _array(hypotheses["mechanisms"], "hypotheses.mechanisms")
    if not mechanisms:
        raise DossierError("at least one mechanism hypothesis is required")
    seen_mechanisms: set[str] = set()
    for index, raw_mechanism in enumerate(mechanisms):
        mechanism = _object(raw_mechanism, f"hypotheses.mechanisms[{index}]")
        _exact_keys(mechanism, {"mechanism_id", "statement", "epistemic_state", "signal_refs", "required_evidence"}, f"hypotheses.mechanisms[{index}]")
        mechanism_id = _id(mechanism["mechanism_id"], f"mechanisms[{index}].mechanism_id")
        if mechanism_id in seen_mechanisms:
            raise DossierError(f"duplicate mechanism id: {mechanism_id}")
        seen_mechanisms.add(mechanism_id)
        _text(mechanism["statement"], f"mechanisms[{index}].statement")
        if mechanism["epistemic_state"] not in {"SOURCE_STATEMENT", "HYPOTHESIS", "UNKNOWN"}:
            raise DossierError("mechanism epistemic state is invalid")
        for signal_ref in _nonempty_text_list(mechanism["signal_refs"], f"mechanisms[{index}].signal_refs"):
            signal = signal_by_id.get(signal_ref)
            if signal is None:
                raise DossierError(f"mechanism references unknown signal: {signal_ref}")
            if signal["signal_class"] == "MECHANISM_HYPOTHESIS" and mechanism["epistemic_state"] == "SOURCE_STATEMENT":
                raise DossierError("mechanism hypothesis cannot be promoted to source statement")
        _nonempty_text_list(mechanism["required_evidence"], f"mechanisms[{index}].required_evidence")

    capabilities = _array(hypotheses["capabilities"], "hypotheses.capabilities")
    if not capabilities:
        raise DossierError("at least one capability is required")
    for index, raw_capability in enumerate(capabilities):
        capability = _object(raw_capability, f"hypotheses.capabilities[{index}]")
        _exact_keys(capability, {"capability_id", "description", "importance", "rights_state", "required_evidence"}, f"hypotheses.capabilities[{index}]")
        _id(capability["capability_id"], f"capabilities[{index}].capability_id")
        _text(capability["description"], f"capabilities[{index}].description")
        if capability["importance"] not in {"must", "should", "could"}:
            raise DossierError("capability importance is invalid")
        if capability["rights_state"] not in {"UNKNOWN", "CONDITIONAL", "PASS", "NOT_APPLICABLE"}:
            raise DossierError("capability rights state is invalid")
        if capability["rights_state"] == "PASS" and product_signal["evidence_state"]["legal"] != "PASS":
            raise DossierError("capability rights cannot PASS without legal evidence")
        _nonempty_text_list(capability["required_evidence"], f"capabilities[{index}].required_evidence")

    business = _object(hypotheses["business"], "hypotheses.business")
    _exact_keys(business, set(BUSINESS_FIELDS), "hypotheses.business")
    for field in BUSINESS_FIELDS:
        _validate_epistemic_item(business[field], f"hypotheses.business.{field}", {"HYPOTHESIS", "UNKNOWN"})

    assumptions = _array(hypotheses["riskiest_assumptions"], "hypotheses.riskiest_assumptions")
    if not assumptions:
        raise DossierError("riskiest_assumptions must not be empty")
    seen_assumptions: set[str] = set()
    for index, raw_assumption in enumerate(assumptions):
        assumption = _object(raw_assumption, f"hypotheses.riskiest_assumptions[{index}]")
        _exact_keys(assumption, {"assumption_id", "statement", "falsifier"}, f"hypotheses.riskiest_assumptions[{index}]")
        assumption_id = _id(assumption["assumption_id"], f"assumption[{index}].assumption_id")
        if assumption_id in seen_assumptions:
            raise DossierError(f"duplicate assumption id: {assumption_id}")
        seen_assumptions.add(assumption_id)
        _text(assumption["statement"], f"assumption[{index}].statement")
        _text(assumption["falsifier"], f"assumption[{index}].falsifier")

    mvp = _object(hypotheses["mvp"], "hypotheses.mvp")
    _exact_keys(mvp, {"wedge", "maximum_days", "budget_usd", "success_metrics", "stop_loss", "non_goals"}, "hypotheses.mvp")
    _text(mvp["wedge"], "hypotheses.mvp.wedge")
    if not isinstance(mvp["maximum_days"], int) or isinstance(mvp["maximum_days"], bool) or not 1 <= mvp["maximum_days"] <= 30:
        raise DossierError("mvp.maximum_days must be an integer from 1 to 30")
    if not isinstance(mvp["budget_usd"], (int, float)) or isinstance(mvp["budget_usd"], bool) or mvp["budget_usd"] <= 0:
        raise DossierError("mvp.budget_usd must be positive")
    for key in ("success_metrics", "stop_loss", "non_goals"):
        _nonempty_text_list(mvp[key], f"hypotheses.mvp.{key}")

    _scan_forbidden(hypotheses, "hypotheses")
    return hypotheses


def compile_dossier(product_signal: Any, external_binding: Any, hypotheses: Any, *, snapshot_bytes: bytes) -> dict[str, Any]:
    signal = validate_product_signal(product_signal)
    binding = validate_external_binding(external_binding, signal, snapshot_bytes)
    plan = validate_hypotheses(hypotheses, signal)

    signal_ids = sorted(item["signal_id"] for item in signal["signals"])
    claim_ids = sorted({claim for item in signal["signals"] for claim in item["claim_ids"]})
    signal_gaps = sorted({gap for item in signal["signals"] for gap in item["open_gaps"]})
    user_gaps = sorted({gap for field in USER_FIELDS for gap in plan["user_context"][field]["required_evidence"]})
    business_gaps = sorted({gap for field in BUSINESS_FIELDS for gap in plan["business"][field]["required_evidence"]})
    capability_gaps = sorted({gap for item in plan["capabilities"] for gap in item["required_evidence"]})
    blockers = sorted(set(signal_gaps + user_gaps + business_gaps + capability_gaps))

    dossier: dict[str, Any] = {
        "schema_version": "reverse-engineering-dossier@1",
        "dossier_id": f"dossier:{plan['hypothesis_set_id']}",
        "target": copy.deepcopy(plan["target"]),
        "source_subject": {
            "repository": binding["repository"],
            "pull_request": binding["pull_request"],
            "head_sha": binding["head_sha"],
            "path": binding["path"],
            "blob_sha": binding["blob_sha"],
            "product_signal_digest": binding["product_signal_digest"],
            "source_digest": binding["source_digest"],
        },
        "user_context": copy.deepcopy(plan["user_context"]),
        "workflow": copy.deepcopy(plan["workflow"]),
        "mechanisms": copy.deepcopy(plan["mechanisms"]),
        "capabilities": copy.deepcopy(plan["capabilities"]),
        "business": copy.deepcopy(plan["business"]),
        "riskiest_assumptions": copy.deepcopy(plan["riskiest_assumptions"]),
        "mvp": copy.deepcopy(plan["mvp"]),
        "lineage": {
            "signal_ids": signal_ids,
            "claim_ids": claim_ids,
            "unknown_claims": sorted(signal["unknown_claims"]),
            "unresolved_contradictions": sorted(signal["unresolved_contradictions"]),
        },
        "gates": {
            "source_evidence": signal["evidence_state"]["source"],
            "runtime_evidence": signal["evidence_state"]["runtime"],
            "user_evidence": signal["evidence_state"]["user"],
            "paid_evidence": signal["evidence_state"]["paid"],
            "legal_evidence": signal["evidence_state"]["legal"],
            "named_product_internals": "HYPOTHESIS_OR_UNKNOWN",
        },
        "open_evidence_gaps": blockers,
        "decision": "VALIDATE",
        "authority_ceiling": "VALIDATION_DESIGN_ONLY",
        "non_claims": [
            "The dossier is a source-constrained validation design, not proof of a named product's internal implementation.",
            "Target user, buyer, pain, workflow, distribution, monetization, retention, and defensibility remain hypotheses or unknowns until direct evidence exists.",
            "No package license, runtime quality, customer value, paid demand, BUILD, merge, release, or production state is established.",
        ],
        "dossier_digest": "sha256:" + "0" * 64,
    }
    dossier["dossier_digest"] = digest_json(dossier, drop_key="dossier_digest")
    validate_dossier(dossier, product_signal=signal)
    return dossier


def validate_dossier(raw: Any, *, product_signal: Any) -> dict[str, Any]:
    signal = validate_product_signal(product_signal)
    dossier = _object(raw, "dossier")
    expected = {
        "schema_version",
        "dossier_id",
        "target",
        "source_subject",
        "user_context",
        "workflow",
        "mechanisms",
        "capabilities",
        "business",
        "riskiest_assumptions",
        "mvp",
        "lineage",
        "gates",
        "open_evidence_gaps",
        "decision",
        "authority_ceiling",
        "non_claims",
        "dossier_digest",
    }
    _exact_keys(dossier, expected, "dossier")
    if dossier["schema_version"] != "reverse-engineering-dossier@1":
        raise DossierError("dossier schema version mismatch")
    if dossier["decision"] not in {"VALIDATE", "WATCH", "BLOCKED", "REJECT"}:
        raise DossierError("dossier decision exceeds validation authority")
    if dossier["decision"] == "BUILD":
        raise DossierError("BUILD is forbidden in reverse-engineering dossier")
    if dossier["authority_ceiling"] != "VALIDATION_DESIGN_ONLY":
        raise DossierError("dossier authority ceiling widened")
    expected_digest = digest_json(dossier, drop_key="dossier_digest")
    if dossier["dossier_digest"] != expected_digest:
        raise DossierError("dossier digest mismatch")

    lineage = _object(dossier["lineage"], "dossier.lineage")
    _exact_keys(lineage, {"signal_ids", "claim_ids", "unknown_claims", "unresolved_contradictions"}, "dossier.lineage")
    expected_signal_ids = sorted(item["signal_id"] for item in signal["signals"])
    expected_claim_ids = sorted({claim for item in signal["signals"] for claim in item["claim_ids"]})
    if lineage["signal_ids"] != expected_signal_ids:
        raise DossierError("dossier dropped or invented product signals")
    if lineage["claim_ids"] != expected_claim_ids:
        raise DossierError("dossier dropped or invented claim lineage")
    if lineage["unknown_claims"] != sorted(signal["unknown_claims"]):
        raise DossierError("dossier silenced UNKNOWN claims")
    if lineage["unresolved_contradictions"] != sorted(signal["unresolved_contradictions"]):
        raise DossierError("dossier silenced unresolved contradictions")

    gates = _object(dossier["gates"], "dossier.gates")
    _exact_keys(gates, {"source_evidence", "runtime_evidence", "user_evidence", "paid_evidence", "legal_evidence", "named_product_internals"}, "dossier.gates")
    if gates["source_evidence"] != "PASS":
        raise DossierError("dossier source evidence must remain PASS")
    if gates["named_product_internals"] != "HYPOTHESIS_OR_UNKNOWN":
        raise DossierError("named product internals were promoted")
    for field in ("runtime_evidence", "user_evidence", "paid_evidence", "legal_evidence"):
        if gates[field] != signal["evidence_state"][field.removesuffix("_evidence")]:
            raise DossierError(f"dossier gate drift: {field}")
    if gates["user_evidence"] in {"ABSENT", "NOT_EXERCISED"} and dossier["decision"] not in {"VALIDATE", "WATCH", "BLOCKED"}:
        raise DossierError("missing user evidence cannot promote the decision")
    if gates["paid_evidence"] in {"ABSENT", "NOT_EXERCISED"} and dossier["decision"] not in {"VALIDATE", "WATCH", "BLOCKED"}:
        raise DossierError("missing paid evidence cannot promote the decision")

    if gates["legal_evidence"] != "PASS":
        for item in _array(dossier["capabilities"], "dossier.capabilities"):
            if _object(item, "dossier.capability").get("rights_state") == "PASS":
                raise DossierError("rights PASS cannot appear without legal evidence")

    _nonempty_text_list(dossier["open_evidence_gaps"], "dossier.open_evidence_gaps")
    _nonempty_text_list(dossier["non_claims"], "dossier.non_claims")
    _scan_forbidden(dossier, "dossier")
    return dossier
