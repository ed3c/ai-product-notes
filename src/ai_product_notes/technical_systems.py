from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


class TechnicalSystemsError(ValueError):
    """Fail-closed Stage 5 contract error."""


SHA256 = re.compile(r"^sha256:[a-f0-9]{64}$")
GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
RIGHT_TYPES = (
    "code",
    "model_weights",
    "datasets",
    "trajectories",
    "hosted_service",
    "third_party_content",
)
RIGHT_STATES = {"PASS", "CONDITIONAL", "UNKNOWN", "REJECT", "NOT_APPLICABLE", "STALE"}
EVAL_KINDS = {"POSITIVE", "NEGATIVE", "MUTATION", "FAULT", "RUNTIME"}
FORBIDDEN = (
    "credential",
    "secret",
    "token",
    "private_repository",
    "private_repo",
    "customer_data",
    "raw_session",
    "private_note_body",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest_json(value: Any, drop_key: str) -> str:
    payload = copy.deepcopy(value)
    payload.pop(drop_key, None)
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TechnicalSystemsError(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TechnicalSystemsError(f"{path} must contain a JSON object")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TechnicalSystemsError(f"{where} must be non-empty text")
    return value


def _list(value: Any, where: str, *, empty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (not value and not empty):
        raise TechnicalSystemsError(f"{where} must be a{' non-empty' if not empty else ''} list")
    return value


def _texts(value: Any, where: str, *, empty: bool = False) -> list[str]:
    values = [_text(item, f"{where}[]") for item in _list(value, where, empty=empty)]
    if len(values) != len(set(values)):
        raise TechnicalSystemsError(f"{where} contains duplicates")
    return values


def _scan_private(value: Any, where: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(part in normalized for part in FORBIDDEN):
                raise TechnicalSystemsError(f"forbidden public field at {where}.{key}")
            _scan_private(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_private(child, f"{where}[{index}]")


def validate_dossier(dossier: dict[str, Any]) -> dict[str, Any]:
    if dossier.get("schema_version") != "reverse-engineering-dossier@1":
        raise TechnicalSystemsError("unexpected dossier schema")
    if dossier.get("authority_ceiling") != "VALIDATION_DESIGN_ONLY":
        raise TechnicalSystemsError("dossier authority widened")
    if dossier.get("decision") != "VALIDATE":
        raise TechnicalSystemsError("Stage 5 accepts only VALIDATE")
    digest = _text(dossier.get("dossier_digest"), "dossier_digest")
    if not SHA256.fullmatch(digest) or digest_json(dossier, "dossier_digest") != digest:
        raise TechnicalSystemsError("dossier digest mismatch")

    gates = dossier.get("gates")
    if not isinstance(gates, dict) or gates.get("source_evidence") != "PASS":
        raise TechnicalSystemsError("source evidence must PASS")
    for key in ("runtime_evidence", "user_evidence", "paid_evidence", "legal_evidence"):
        if gates.get(key) not in {"PASS", "FAIL", "ABSENT", "NOT_EXERCISED"}:
            raise TechnicalSystemsError(f"invalid dossier gate {key}")

    caps = _list(dossier.get("capabilities"), "dossier.capabilities")
    ids: set[str] = set()
    for cap in caps:
        if not isinstance(cap, dict):
            raise TechnicalSystemsError("dossier capability must be object")
        cap_id = _text(cap.get("capability_id"), "dossier capability id")
        if cap_id in ids:
            raise TechnicalSystemsError(f"duplicate dossier capability {cap_id}")
        ids.add(cap_id)
        if cap.get("importance") not in {"must", "should", "could"}:
            raise TechnicalSystemsError("invalid capability importance")
        if cap.get("rights_state") not in RIGHT_STATES:
            raise TechnicalSystemsError("invalid dossier rights state")
        _texts(cap.get("required_evidence"), "dossier required evidence")

    lineage = dossier.get("lineage")
    if not isinstance(lineage, dict):
        raise TechnicalSystemsError("dossier lineage missing")
    _texts(lineage.get("unknown_claims"), "upstream unknown claims")
    _texts(lineage.get("unresolved_contradictions"), "upstream contradictions")
    _scan_private(dossier)
    return dossier


def validate_binding(binding: dict[str, Any], dossier: dict[str, Any], dossier_bytes: bytes) -> dict[str, Any]:
    if binding.get("schema_version") != "stage4-dossier-binding@1":
        raise TechnicalSystemsError("binding schema mismatch")
    if binding.get("repository") != "ed3c/ai-product-notes" or binding.get("pull_request") != 54:
        raise TechnicalSystemsError("unexpected Stage 4 subject")
    if not GIT_SHA.fullmatch(_text(binding.get("head_sha"), "binding head")):
        raise TechnicalSystemsError("invalid binding head")
    if not GIT_SHA.fullmatch(_text(binding.get("blob_sha"), "binding blob")):
        raise TechnicalSystemsError("invalid binding blob")
    if binding.get("dossier_digest") != dossier["dossier_digest"]:
        raise TechnicalSystemsError("binding dossier digest mismatch")
    if binding.get("authority_ceiling") != "VALIDATION_DESIGN_ONLY":
        raise TechnicalSystemsError("binding authority widened")
    if git_blob_sha1(dossier_bytes) != binding["blob_sha"]:
        raise TechnicalSystemsError("dossier bytes do not match bound Git blob")
    return binding


def _rights(rights: Any, where: str) -> None:
    if not isinstance(rights, dict) or set(rights) != set(RIGHT_TYPES):
        raise TechnicalSystemsError(f"{where} must gate all six rights lanes")
    for right_type in RIGHT_TYPES:
        item = rights[right_type]
        if not isinstance(item, dict) or set(item) != {"status", "evidence", "scope"}:
            raise TechnicalSystemsError(f"invalid right object at {where}.{right_type}")
        if item["status"] not in RIGHT_STATES:
            raise TechnicalSystemsError(f"invalid right state at {where}.{right_type}")
        evidence = _texts(item["evidence"], f"{where}.{right_type}.evidence", empty=True)
        _text(item["scope"], f"{where}.{right_type}.scope")
        if item["status"] == "PASS" and not evidence:
            raise TechnicalSystemsError(f"PASS right lacks direct evidence at {where}.{right_type}")


def _acyclic(graph: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise TechnicalSystemsError(f"dependency cycle at {node}")
        if node in done:
            return
        visiting.add(node)
        for parent in graph[node]:
            visit(parent)
        visiting.remove(node)
        done.add(node)

    for node in graph:
        visit(node)


def validate_plan(plan: dict[str, Any], dossier: dict[str, Any]) -> dict[str, Any]:
    if plan.get("schema_version") != "technical-systems-plan@1":
        raise TechnicalSystemsError("plan schema mismatch")
    if plan.get("dossier_digest") != dossier["dossier_digest"]:
        raise TechnicalSystemsError("plan dossier digest mismatch")
    if plan.get("authority_ceiling") != "TECHNICAL_DESIGN_ONLY" or plan.get("decision_ceiling") != "VALIDATE":
        raise TechnicalSystemsError("plan authority or decision widened")

    dossier_caps = {item["capability_id"]: item for item in dossier["capabilities"]}
    caps = _list(plan.get("capabilities"), "plan.capabilities")
    ids: set[str] = set()
    graph: dict[str, list[str]] = {}
    for cap in caps:
        if not isinstance(cap, dict):
            raise TechnicalSystemsError("plan capability must be object")
        cap_id = _text(cap.get("capability_id"), "capability id")
        if cap_id in ids:
            raise TechnicalSystemsError(f"duplicate capability {cap_id}")
        ids.add(cap_id)
        dossier_id = _text(cap.get("dossier_capability_id"), "dossier capability id")
        if dossier_id not in dossier_caps or cap.get("importance") != dossier_caps[dossier_id]["importance"]:
            raise TechnicalSystemsError(f"capability {cap_id} does not preserve dossier importance")
        if cap.get("boundary") not in {"DETERMINISTIC", "PROBABILISTIC", "ADAPTER"}:
            raise TechnicalSystemsError(f"invalid boundary for {cap_id}")
        for field in ("owner", "oracle", "failure_state", "rollback"):
            _text(cap.get(field), f"{cap_id}.{field}")
        for field in ("inputs", "outputs", "interfaces", "required_evidence"):
            _texts(cap.get(field), f"{cap_id}.{field}")
        dependencies = _texts(cap.get("dependencies"), f"{cap_id}.dependencies", empty=True)
        if cap_id in dependencies:
            raise TechnicalSystemsError("self dependency")
        graph[cap_id] = dependencies
        transitions = _list(cap.get("transitions"), f"{cap_id}.transitions")
        for transition in transitions:
            if not isinstance(transition, dict) or set(transition) != {"from", "event", "to"}:
                raise TechnicalSystemsError(f"invalid transition for {cap_id}")
            for field in ("from", "event", "to"):
                _text(transition[field], f"{cap_id}.transition.{field}")
        _rights(cap.get("rights"), f"{cap_id}.rights")

    for cap_id, dependencies in graph.items():
        if not set(dependencies).issubset(ids):
            raise TechnicalSystemsError(f"unknown dependency for {cap_id}")
    _acyclic(graph)

    for item in _list(plan.get("substitutions"), "plan.substitutions", empty=True):
        if not isinstance(item, dict) or item.get("capability_id") not in ids:
            raise TechnicalSystemsError("invalid substitution capability")
        if item.get("status") not in {"CANDIDATE", "UNKNOWN", "REJECTED", "SELECTED"}:
            raise TechnicalSystemsError("invalid substitution status")
        _text(item.get("candidate"), "substitution candidate")
        _texts(item.get("required_evidence"), "substitution evidence")
        _rights(item.get("rights"), "substitution.rights")
        if item["status"] == "SELECTED" and item["rights"]["code"]["status"] != "PASS":
            raise TechnicalSystemsError("selected substitution requires PASS code rights")

    kinds: set[str] = set()
    for item in _list(plan.get("evals"), "plan.evals"):
        if not isinstance(item, dict) or item.get("kind") not in EVAL_KINDS:
            raise TechnicalSystemsError("invalid eval")
        kinds.add(item["kind"])
        if not set(_texts(item.get("capability_ids"), "eval capability ids")).issubset(ids):
            raise TechnicalSystemsError("eval references unknown capability")
        _text(item.get("procedure"), "eval procedure")
        _text(item.get("oracle"), "eval oracle")
        if item.get("evidence_state") not in {"PLANNED", "NOT_EXERCISED", "BLOCKED"}:
            raise TechnicalSystemsError("Stage 5 cannot claim executed eval evidence")
    if kinds != EVAL_KINDS:
        raise TechnicalSystemsError("all five eval kinds are required")

    mvp = plan.get("mvp_slice")
    if not isinstance(mvp, dict):
        raise TechnicalSystemsError("MVP slice missing")
    mvp_ids = set(_texts(mvp.get("capability_ids"), "MVP capability ids"))
    excluded = set(_texts(mvp.get("excluded_capabilities"), "MVP excluded", empty=True))
    if not (mvp_ids | excluded).issubset(ids) or mvp_ids & excluded:
        raise TechnicalSystemsError("invalid MVP capability partition")
    must = {cap["capability_id"] for cap in caps if cap["importance"] == "must"}
    if not must.issubset(mvp_ids):
        raise TechnicalSystemsError("MVP omits a must capability")
    by_id = {cap["capability_id"]: cap for cap in caps}
    if any(by_id[cap_id]["boundary"] == "PROBABILISTIC" for cap_id in mvp_ids):
        raise TechnicalSystemsError("current MVP cannot depend on probabilistic rendering")
    if not isinstance(mvp.get("maximum_days"), int) or not 1 <= mvp["maximum_days"] <= dossier["mvp"]["maximum_days"]:
        raise TechnicalSystemsError("MVP time exceeds dossier bound")
    if isinstance(mvp.get("budget_usd"), bool) or not isinstance(mvp.get("budget_usd"), (int, float)) or not 0 < mvp["budget_usd"] <= dossier["mvp"]["budget_usd"]:
        raise TechnicalSystemsError("MVP budget exceeds dossier bound")
    for field in ("success_oracles", "stop_loss"):
        _texts(mvp.get(field), f"MVP {field}")
    _text(mvp.get("rollback"), "MVP rollback")

    nfr = plan.get("nonfunctional_evidence")
    if not isinstance(nfr, dict) or set(nfr) != {"cost", "latency", "security", "privacy", "rollback"}:
        raise TechnicalSystemsError("nonfunctional evidence must cover cost/latency/security/privacy/rollback")
    for key, value in nfr.items():
        _texts(value, f"nonfunctional {key}")
    _texts(plan.get("non_claims"), "plan non-claims")
    _scan_private(plan)
    return plan


def compile_packet(dossier: dict[str, Any], binding: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    validate_dossier(dossier)
    validate_plan(plan, dossier)
    capabilities = copy.deepcopy(plan["capabilities"])
    packet = {
        "schema_version": "technical-systems-packet@1",
        "packet_id": plan["packet_id"],
        "source_subject": {
            "repository": binding["repository"],
            "pull_request": binding["pull_request"],
            "head_sha": binding["head_sha"],
            "path": binding["path"],
            "blob_sha": binding["blob_sha"],
            "dossier_digest": dossier["dossier_digest"],
        },
        "authority_ceiling": "TECHNICAL_DESIGN_ONLY",
        "decision": "VALIDATE",
        "boundaries": copy.deepcopy(plan["boundaries"]),
        "capabilities": capabilities,
        "dependency_edges": [
            {"from": parent, "to": cap["capability_id"]}
            for cap in capabilities
            for parent in cap["dependencies"]
        ],
        "substitutions": copy.deepcopy(plan["substitutions"]),
        "evals": copy.deepcopy(plan["evals"]),
        "mvp_slice": copy.deepcopy(plan["mvp_slice"]),
        "nonfunctional_evidence": copy.deepcopy(plan["nonfunctional_evidence"]),
        "upstream_unknown_claims": copy.deepcopy(dossier["lineage"]["unknown_claims"]),
        "upstream_unresolved_contradictions": copy.deepcopy(dossier["lineage"]["unresolved_contradictions"]),
        "evidence_state": {
            "design": "PASS",
            "implementation": "ABSENT",
            "runtime": dossier["gates"]["runtime_evidence"],
            "user": dossier["gates"]["user_evidence"],
            "paid": dossier["gates"]["paid_evidence"],
            "legal": dossier["gates"]["legal_evidence"],
        },
        "non_claims": copy.deepcopy(plan["non_claims"]),
        "packet_digest": "sha256:" + "0" * 64,
    }
    packet["packet_digest"] = digest_json(packet, "packet_digest")
    return packet


def validate_packet(packet: dict[str, Any]) -> dict[str, Any]:
    if packet.get("schema_version") != "technical-systems-packet@1":
        raise TechnicalSystemsError("packet schema mismatch")
    if packet.get("authority_ceiling") != "TECHNICAL_DESIGN_ONLY" or packet.get("decision") != "VALIDATE":
        raise TechnicalSystemsError("packet authority or decision widened")
    evidence = packet.get("evidence_state")
    if not isinstance(evidence, dict) or evidence.get("implementation") != "ABSENT":
        raise TechnicalSystemsError("Stage 5 packet cannot claim implementation")
    if not packet.get("upstream_unknown_claims") or not packet.get("upstream_unresolved_contradictions"):
        raise TechnicalSystemsError("packet silenced upstream uncertainty")
    if digest_json(packet, "packet_digest") != packet.get("packet_digest"):
        raise TechnicalSystemsError("packet digest mismatch")
    _scan_private(packet)
    return packet


def compile_from_paths(dossier_path: Path, binding_path: Path, plan_path: Path) -> dict[str, Any]:
    dossier_bytes = dossier_path.read_bytes()
    dossier = validate_dossier(json.loads(dossier_bytes.decode("utf-8")))
    binding = validate_binding(load_json(binding_path), dossier, dossier_bytes)
    plan = validate_plan(load_json(plan_path), dossier)
    return validate_packet(compile_packet(dossier, binding, plan))
