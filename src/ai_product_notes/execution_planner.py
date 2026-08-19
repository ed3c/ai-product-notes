from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


class ExecutionPlanError(ValueError):
    """Fail-closed Stage 7 planning error."""


GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
ATOM_TYPES = {"C", "K", "A", "E", "X", "D"}
LANES = {"CLOUD", "LOCAL", "PRIVATE", "HUMAN"}
STACK_CLASSES = {"root", "sibling", "child", "review-only", "convergence"}
HUMAN_OPS = {
    "merge",
    "release",
    "rights admission",
    "customer truth",
    "commercial truth",
    "production promotion",
    "semantic conflict resolution",
}
FORBIDDEN = (
    "credential",
    "secret",
    "token",
    "private_repository",
    "private_repo",
    "customer_data",
    "raw_session",
    "chain_of_thought",
    "private_reasoning",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest_json(value: Any, *, drop_key: str | None = None) -> str:
    payload = copy.deepcopy(value)
    if drop_key and isinstance(payload, dict):
        payload.pop(drop_key, None)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("utf-8") + raw).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutionPlanError(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExecutionPlanError(f"{path} must contain a JSON object")
    return value


def _obj(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ExecutionPlanError(f"{where} must be object")
    return value


def _arr(value: Any, where: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ExecutionPlanError(f"{where} must be {'non-empty ' if nonempty else ''}array")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExecutionPlanError(f"{where} must be non-empty text")
    return value


def _scan(value: Any, where: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            norm = str(key).lower().replace("-", "_")
            if any(part in norm for part in FORBIDDEN):
                raise ExecutionPlanError(f"forbidden public field at {where}.{key}")
            _scan(child, f"{where}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _scan(child, f"{where}[{i}]")


def validate_stage6_binding(
    binding: dict[str, Any],
    matrix_bytes: bytes,
    audit_bytes: bytes,
    delta_bytes: bytes,
    shadow_bytes: bytes,
) -> dict[str, Any]:
    if binding.get("schema_version") != "stage6-closure-binding@1":
        raise ExecutionPlanError("Stage 6 binding schema mismatch")
    if binding.get("repository") != "ed3c/ai-product-notes" or binding.get("pull_request") != 57:
        raise ExecutionPlanError("unexpected Stage 6 subject")
    if not GIT_SHA.fullmatch(_text(binding.get("head_sha"), "stage6.head_sha")):
        raise ExecutionPlanError("Stage 6 head must be full SHA")
    if binding.get("authority_ceiling") != "FINDINGS_ONLY":
        raise ExecutionPlanError("Stage 6 authority widened")
    if not isinstance(binding.get("hosted_run"), int) or binding["hosted_run"] <= 0:
        raise ExecutionPlanError("Stage 6 hosted run missing")
    for key, raw, expected_path in (
        ("matrix", matrix_bytes, "problem-closure-matrix.json"),
        ("audit", audit_bytes, "product-closure-audit.json"),
        ("delta", delta_bytes, "issue-delta.json"),
        ("shadow", shadow_bytes, "shadow-review.json"),
    ):
        item = _obj(binding.get(key), f"stage6.{key}")
        if not item.get("path", "").endswith(expected_path):
            raise ExecutionPlanError(f"Stage 6 {key} path mismatch")
        if git_blob_sha1(raw) != item.get("blob_sha"):
            raise ExecutionPlanError(f"Stage 6 {key} Git blob drift")
    audit = json.loads(audit_bytes.decode("utf-8"))
    if digest_json(audit) != binding["audit"]["canonical_digest"]:
        raise ExecutionPlanError("Stage 6 audit canonical digest drift")
    if audit.get("schema") != "prel/product-closure-audit/v1":
        raise ExecutionPlanError("Stage 6 audit schema mismatch")
    if any(p.get("highest_earned_level") in {
        "IMPLEMENTED", "TECH_VERIFIED", "LIVE_WORKFLOW_VERIFIED",
        "USER_VALIDATED", "PAID_VALIDATED"
    } for p in audit.get("problems", [])):
        raise ExecutionPlanError("Stage 6 input unexpectedly promotes closure")
    delta = json.loads(delta_bytes.decode("utf-8"))
    if delta.get("write_authority") != "NO_WRITE_AUTHORITY":
        raise ExecutionPlanError("Stage 6 delta has write authority")
    shadow = json.loads(shadow_bytes.decode("utf-8"))
    if shadow.get("authority_ceiling") != "FINDINGS_ONLY":
        raise ExecutionPlanError("Stage 6 Shadow authority widened")
    return binding


def validate_skills_binding(binding: dict[str, Any]) -> dict[str, Any]:
    if binding.get("schema_version") != "stage7-skills-binding@1":
        raise ExecutionPlanError("skills binding schema mismatch")
    if binding.get("repository") != "ed3c/skills-shared":
        raise ExecutionPlanError("unexpected skills repository")
    for key in ("commit", "tree_sha"):
        if not GIT_SHA.fullmatch(_text(binding.get(key), f"skills.{key}")):
            raise ExecutionPlanError(f"skills {key} invalid")
    for key in ("prompt_packet_schema", "prompt_catalogue", "molecular_stack_schema"):
        item = _obj(binding.get(key), f"skills.{key}")
        _text(item.get("path"), f"skills.{key}.path")
        if not GIT_SHA.fullmatch(_text(item.get("blob_sha"), f"skills.{key}.blob_sha")):
            raise ExecutionPlanError(f"skills {key} blob invalid")
    if binding.get("authority_ceiling") != "PORTABLE_METHOD_ONLY":
        raise ExecutionPlanError("skills authority widened")
    return binding


def _path_overlap(a: str, b: str) -> bool:
    pa = a.rstrip("/*")
    pb = b.rstrip("/*")
    return pa == pb or pa.startswith(pb + "/") or pb.startswith(pa + "/")


def validate_plan(plan: dict[str, Any], stage6: dict[str, Any], skills: dict[str, Any]) -> dict[str, Any]:
    if plan.get("schema_version") != "execution-planner-input@1":
        raise ExecutionPlanError("planner schema mismatch")
    if plan.get("authority_ceiling") != "PLANNING_ONLY" or plan.get("decision") != "VALIDATE":
        raise ExecutionPlanError("planner authority/decision widened")
    expected_subject = digest_json({
        "stage6": stage6["head_sha"],
        "audit": stage6["audit"]["canonical_digest"],
        "skills": skills["commit"],
    })
    if plan.get("subject_digest") != expected_subject:
        raise ExecutionPlanError("planner subject digest drift")

    atoms = _arr(plan.get("atoms"), "atoms", nonempty=True)
    by_id: dict[str, dict[str, Any]] = {}
    for atom in atoms:
        item = _obj(atom, "atom")
        atom_id = _text(item.get("id"), "atom.id")
        if atom_id in by_id:
            raise ExecutionPlanError(f"duplicate atom {atom_id}")
        by_id[atom_id] = item
        if item.get("atom") not in ATOM_TYPES or item.get("lane") not in LANES:
            raise ExecutionPlanError(f"invalid atom/lane {atom_id}")
        if item.get("stack_class") not in STACK_CLASSES:
            raise ExecutionPlanError(f"invalid stack class {atom_id}")
        for key in ("purpose", "branch", "base_branch", "oracle", "rollback"):
            _text(item.get(key), f"{atom_id}.{key}")
        owns = _arr(item.get("owns_paths"), f"{atom_id}.owns_paths", nonempty=True)
        consumes = _arr(item.get("consumes_paths"), f"{atom_id}.consumes_paths", nonempty=True)
        if set(owns) & set(consumes):
            raise ExecutionPlanError(f"{atom_id} owns and consumes same path")
        for key in ("start_dependencies", "completion_dependencies", "negative_controls"):
            _arr(item.get(key), f"{atom_id}.{key}", nonempty=True)
        budget = _obj(item.get("budget"), f"{atom_id}.budget")
        if not isinstance(budget.get("maximum_hours"), int) or budget["maximum_hours"] <= 0:
            raise ExecutionPlanError(f"{atom_id} invalid hour budget")
        if not isinstance(budget.get("maximum_files"), int) or budget["maximum_files"] < len(owns):
            raise ExecutionPlanError(f"{atom_id} file budget smaller than lease")
        if len(owns) > budget["maximum_files"]:
            raise ExecutionPlanError(f"{atom_id} lease exceeds file budget")

    ids = list(by_id)
    for i, left in enumerate(ids):
        for right in ids[i + 1:]:
            for a in by_id[left]["owns_paths"]:
                for b in by_id[right]["owns_paths"]:
                    if _path_overlap(a, b):
                        raise ExecutionPlanError(f"overlapping writer lease: {left}/{right}: {a} vs {b}")

    graph: dict[str, list[str]] = {}
    for atom_id, item in by_id.items():
        parents = _arr(item.get("parents"), f"{atom_id}.parents")
        if atom_id in parents or not set(parents).issubset(by_id):
            raise ExecutionPlanError(f"invalid parent for {atom_id}")
        graph[atom_id] = parents
        if item["stack_class"] == "child":
            if len(parents) != 1:
                raise ExecutionPlanError(f"child {atom_id} needs exactly one parent")
            parent = by_id[parents[0]]
            if not any(
                _path_overlap(consumed, owned)
                for consumed in item["consumes_paths"]
                for owned in parent["owns_paths"]
            ):
                raise ExecutionPlanError(f"false child edge: {atom_id} consumes no parent bytes")
        if item["stack_class"] == "root" and parents:
            raise ExecutionPlanError(f"root {atom_id} cannot have parents")

    visiting: set[str] = set()
    done: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ExecutionPlanError(f"cycle at {node}")
        if node in done:
            return
        visiting.add(node)
        for parent in graph[node]:
            visit(parent)
        visiting.remove(node)
        done.add(node)

    for node in graph:
        visit(node)

    convergence = [a for a in atoms if a["stack_class"] == "convergence"]
    if len(convergence) != 1:
        raise ExecutionPlanError("exactly one convergence owner required")
    if convergence[0]["atom"] != "D":
        raise ExecutionPlanError("convergence owner must be D atom")

    issue_plan = _arr(plan.get("issue_plan"), "issue_plan", nonempty=True)
    if {i.get("atom_id") for i in issue_plan} != set(by_id):
        raise ExecutionPlanError("issue plan must cover every atom exactly once")
    if any(i.get("write_authority") != "PROPOSAL_ONLY" for i in issue_plan):
        raise ExecutionPlanError("issue plan write authority widened")

    gates = _arr(plan.get("existing_gates"), "existing_gates", nonempty=True)
    issue_ids = [g.get("issue") for g in gates]
    if len(issue_ids) != len(set(issue_ids)):
        raise ExecutionPlanError("duplicate existing gate")
    if any(g.get("required_action") not in {"DO_NOT_DUPLICATE_OR_SUBSTITUTE", "KEEP_SEPARATE", "RECONCILE_NOT_DUPLICATE"} for g in gates):
        raise ExecutionPlanError("existing gate handling invalid")

    if set(plan.get("human_owned_operations", [])) != HUMAN_OPS:
        raise ExecutionPlanError("Human-owned operation set drift")
    _arr(plan.get("nonclaims"), "nonclaims", nonempty=True)
    _scan(plan)
    return plan


def compile_outputs(plan: dict[str, Any], stage6: dict[str, Any], skills: dict[str, Any]) -> dict[str, Any]:
    validate_plan(plan, stage6, skills)
    atoms = copy.deepcopy(plan["atoms"])

    run_contract = {
        "schema_version": "execution-plan-run-contract@1",
        "run_id": plan["run_id"],
        "subject": {
            "stage6_head": stage6["head_sha"],
            "stage6_audit_digest": stage6["audit"]["canonical_digest"],
            "skills_commit": skills["commit"],
            "planner_subject_digest": plan["subject_digest"],
        },
        "authority_ceiling": "PLANNING_ONLY",
        "decision": "VALIDATE",
        "human_owned_operations": copy.deepcopy(plan["human_owned_operations"]),
        "nonclaims": copy.deepcopy(plan["nonclaims"]),
        "run_contract_digest": "0" * 64,
    }
    run_contract["run_contract_digest"] = digest_json(run_contract, drop_key="run_contract_digest")

    execution_dag = {
        "schema_version": "dual-edge-execution-dag@1",
        "run_id": plan["run_id"],
        "nodes": [
            {
                "atom_id": a["id"],
                "atom": a["atom"],
                "branch": a["branch"],
                "parents": copy.deepcopy(a["parents"]),
                "start_dependencies": copy.deepcopy(a["start_dependencies"]),
                "completion_dependencies": copy.deepcopy(a["completion_dependencies"]),
                "evidence_lane": a["lane"],
            }
            for a in atoms
        ],
        "laws": {
            "start_is_not_completion": True,
            "false_serialization_forbidden": True,
            "parent_edge_requires_consumed_bytes": True,
        },
        "dag_digest": "0" * 64,
    }
    execution_dag["dag_digest"] = digest_json(execution_dag, drop_key="dag_digest")

    path_leases = {
        "schema_version": "path-leases@1",
        "run_id": plan["run_id"],
        "active_writers": 0,
        "leases": [
            {
                "atom_id": a["id"],
                "state": "PROPOSED",
                "branch": a["branch"],
                "paths": copy.deepcopy(a["owns_paths"]),
                "resource_owner": f"worker:{a['id']}",
            }
            for a in atoms
        ],
        "law": "One mutable branch has one active writer; overlapping active path/resource leases are forbidden.",
    }

    issue_plan = {
        "schema_version": "execution-issue-plan@1",
        "run_id": plan["run_id"],
        "planned_issues": copy.deepcopy(plan["issue_plan"]),
        "existing_gate_reconciliation": copy.deepcopy(plan["existing_gates"]),
        "write_authority": "PROPOSAL_ONLY",
        "duplicate_safe": True,
    }

    stack_plan = {
        "schema_version": "git-town/molecular-stack-index/v1",
        "subject": {"repository": "ed3c/ai-product-notes", "commit": stage6["head_sha"]},
        "main_branch": "prel/56-problem-closure-audit",
        "required_atoms": ["C", "K", "E", "X", "D"],
        "convergence_owner": "PREL-D02",
        "atoms": [
            {
                "id": a["id"],
                "atom": a["atom"],
                "purpose": a["purpose"],
                "stack_class": a["stack_class"],
                "lane": a["lane"],
                "branch": a["branch"],
                "base_branch": a["base_branch"],
                "parents": copy.deepcopy(a["parents"]),
                "owns_paths": copy.deepcopy(a["owns_paths"]),
                "consumes_paths": copy.deepcopy(a["consumes_paths"]),
                "oracle": a["oracle"],
                "gates": [
                    {"name": dep, "required_lane": a["lane"], "receipt_lane": None}
                    for dep in a["completion_dependencies"]
                ],
                "blockers": copy.deepcopy(a["start_dependencies"]),
                "writer_lease": f"worker:{a['id']}",
                "pr": {"state": "NOT_CREATED", "head_sha": None, "head_source": "ABSENT"},
            }
            for a in atoms
        ],
    }

    queue = {
        "schema_version": "local-handoff-queue@1",
        "queue_id": "PREL-S7-TO-S8-2026-08-20",
        "items": [
            {
                "id": "LH-S7-VERIFY",
                "state": "ACTIVE",
                "owner": "CODEX_CLI_LOCAL_OR_CLAUDE_CODE_LOCAL",
                "subject": {"branch": "prel/58-execution-plan", "expected_parent": stage6["head_sha"]},
                "entry": "Stage 7 Draft PR exact head is readable.",
                "argv": ["python3 -m unittest -q tests/test_execution_plan.py", "python3 scripts/compile_execution_plan.py --check"],
                "cwd": "repository-root",
                "timeout_seconds": 600,
                "durable_receipt": "evals/execution-plan/structured-product-compiler/local-stage7-receipt.json",
                "cleanup": "workspace must remain clean and exact head unchanged",
                "exit": "all Stage 7 planner controls PASS on a clean local checkout",
                "next": "LH-S8-C02",
            },
            {
                "id": "LH-S8-C02",
                "state": "BLOCKED_BY_PREDECESSOR",
                "owner": "CODEX_CLI_LOCAL_OR_CLAUDE_CODE_LOCAL",
                "subject": {"branch": "prel/59-scene-spec-contract", "atom_id": "PREL-C02"},
                "entry": "LH-S7-VERIFY exact receipt PASS and Stage 8 issue/lease admitted.",
                "argv": ["execute prompt-packets/PREL-C02.md"],
                "cwd": "fresh isolated worktree",
                "timeout_seconds": 14400,
                "durable_receipt": "future Stage 8 C02 exact-subject receipt",
                "cleanup": "no out-of-lease changes and no untracked artifacts",
                "exit": "SceneSpec contract and canonicalization oracle PASS",
                "next": "PREL-K03",
            },
        ],
    }

    surfaces = {
        "PREL-C02": "STAGE_8_MOLECULAR_WORKER",
        "PREL-K03": "STAGE_8_MOLECULAR_WORKER",
        "PREL-E02": "STAGE_8_MOLECULAR_WORKER",
        "PREL-X02": "STAGE_8_MOLECULAR_WORKER",
        "PREL-D02": "STAGE_9_CONVERGENCE_OWNER",
    }
    prompts: dict[str, str] = {}
    for a in atoms:
        prompt = f"""# Zero-context Worker Packet — {a['id']}

## Common system envelope

You are executing a bounded Product Reverse-Engineering implementation packet.
Do not use prior conversation as contract evidence. Read repository `AGENTS.md`,
the owning Issue, nearest README, and exact Stage 7 plan before mutation.
Preserve `PASS`, `FAIL`, `ABSENT`, `NOT_IMPLEMENTED`, `NOT_EXERCISED`,
`SKIPPED_BY_POLICY`, and `HUMAN_ADMIT_REQUIRED` as distinct states.
Do not reveal private chain of thought. Findings and receipts only.
You have no merge, permission, secret, rights, production, user-truth,
commercial-truth, or release authority.

## Packet

```text
surface             {surfaces[a['id']]}
atom                {a['id']} / {a['atom']}
planner subject     {plan['subject_digest']}
parent Stage 6      {stage6['head_sha']}
branch              {a['branch']}
base branch          {a['base_branch']}
lane                 {a['lane']}
```

Objective:
{a['purpose']}

Non-goals:
- do not select a rendering/model/provider unless this packet explicitly owns it;
- do not satisfy user, paid or rights lanes with technical evidence;
- do not merge, release or broaden scope;
- do not write outside the lease.

Writable lease:
{chr(10).join(f'- `{p}`' for p in a['owns_paths'])}

Consumed paths/contracts:
{chr(10).join(f'- `{p}`' for p in a['consumes_paths'])}

Start dependencies:
{chr(10).join(f'- {d}' for d in a['start_dependencies'])}

Completion dependencies:
{chr(10).join(f'- {d}' for d in a['completion_dependencies'])}

Oracle:
{a['oracle']}

Negative controls:
{chr(10).join(f'- {c}' for c in a['negative_controls'])}

Budget:
- maximum hours: {a['budget']['maximum_hours']}
- maximum leased path entries: {a['budget']['maximum_files']}

Rollback:
{a['rollback']}

Completion report must include exact base/head/tree, changed paths, commands,
results, negative controls, receipt digests, evidence states, non-claims,
rollback subject and next owner. Exit with a typed blocker rather than widening
authority or silently rebinding stale input.
"""
        prompts[a["id"]] = prompt

    return {
        "run-contract.json": run_contract,
        "execution-dag.json": execution_dag,
        "issue-plan.json": issue_plan,
        "path-leases.json": path_leases,
        "stack-plan.json": stack_plan,
        "local-handoff-queue.json": queue,
        "prompts": prompts,
    }


def compile_from_paths(
    plan_path: Path,
    skills_binding_path: Path,
    stage6_binding_path: Path,
    matrix_path: Path,
    audit_path: Path,
    delta_path: Path,
    shadow_path: Path,
) -> dict[str, Any]:
    matrix_bytes = matrix_path.read_bytes()
    audit_bytes = audit_path.read_bytes()
    delta_bytes = delta_path.read_bytes()
    shadow_bytes = shadow_path.read_bytes()
    stage6 = validate_stage6_binding(
        load_json(stage6_binding_path), matrix_bytes, audit_bytes, delta_bytes, shadow_bytes
    )
    skills = validate_skills_binding(load_json(skills_binding_path))
    plan = validate_plan(load_json(plan_path), stage6, skills)
    return compile_outputs(plan, stage6, skills)
