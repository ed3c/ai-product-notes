#!/usr/bin/env python3
"""Execute and verify the PREL-X02 local structured-scene canary.

The first clean run writes a receipt bound to the committed runner/input
candidate. After that receipt is committed, the same command verifies the
receipt and its subject without trying to make a receipt self-reference the
commit that contains it.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = Path("evals/structured-scene/runtime/contract.json")


class CanaryError(RuntimeError):
    """A PREL-X02 runtime invariant was not satisfied."""


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "git failed"
        raise CanaryError(detail)
    return completed.stdout.strip()


def _require_clean(root: Path) -> None:
    if _git(root, "status", "--porcelain"):
        raise CanaryError("dirty workspace")


def _require_local_runtime(root: Path, runtime_identity: str) -> None:
    if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
        raise CanaryError("hosted CI cannot satisfy the local runtime lane")
    if runtime_identity == "CODEX_CLI_LOCAL":
        if not os.environ.get("CODEX_THREAD_ID"):
            raise CanaryError("CODEX_CLI_LOCAL requires current Codex thread evidence")
        return
    if runtime_identity == "CLAUDE_CODE_LOCAL":
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if os.environ.get("CLAUDECODE") != "1" or not project_dir:
            raise CanaryError("CLAUDE_CODE_LOCAL requires current Claude Code evidence")
        if Path(project_dir).resolve() != root.resolve():
            raise CanaryError("CLAUDE_PROJECT_DIR does not identify this checkout")
        return
    raise CanaryError("unknown local runtime identity")


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CanaryError(f"{label} is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise CanaryError(f"{label} must contain one JSON object")
    return value


def _relative_path(root: Path, path: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise CanaryError(f"{label} escapes repository root") from exc


def _declared_repo_path(
    root: Path, raw: Any, label: str, allowed_paths: list[str]
) -> Path:
    if not isinstance(raw, str) or not raw:
        raise CanaryError(f"{label} must be a non-empty repository-relative path")
    logical = PurePosixPath(raw)
    if logical.is_absolute() or raw != logical.as_posix() or ".." in logical.parts:
        raise CanaryError(f"{label} must be a normalized repository-relative path")
    path = root.joinpath(*logical.parts)
    if _relative_path(root, path, label) != raw:
        raise CanaryError(f"{label} does not resolve to its declared repository path")
    if not _path_allowed(raw, allowed_paths):
        raise CanaryError(f"{label} escapes runtime lease")
    return path


def _validate_contract(contract: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "atom",
        "repository",
        "expected_base",
        "expected_branch",
        "runtime_identities",
        "input_path",
        "receipt_path",
        "allowed_paths",
        "authority_ceiling",
    }
    if set(contract) != required:
        raise CanaryError("runtime contract fields drifted")
    if contract["schema_version"] != "structured-scene-runtime-contract@1":
        raise CanaryError("runtime contract schema drifted")
    if contract["atom"] != "PREL-X02":
        raise CanaryError("runtime contract belongs to another atom")
    if contract["repository"] != "ed3c/ai-product-notes":
        raise CanaryError("runtime contract repository drifted")
    if contract["authority_ceiling"] != "LOCAL_RUNTIME_ATOM_ONLY":
        raise CanaryError("runtime contract authority widened")
    for name in ("expected_base",):
        value = contract[name]
        if not isinstance(value, str) or len(value) != 40 or any(
            char not in "0123456789abcdef" for char in value
        ):
            raise CanaryError(f"runtime contract {name} is not a 40-hex SHA")
    if contract["runtime_identities"] != ["CODEX_CLI_LOCAL", "CLAUDE_CODE_LOCAL"]:
        raise CanaryError("runtime identity denominator drifted")
    if contract["allowed_paths"] != [
        "scripts/run_structured_scene_canary.py",
        "evals/structured-scene/runtime/**",
    ]:
        raise CanaryError("runtime path lease drifted")


def _path_allowed(path: str, rules: list[str]) -> bool:
    for rule in rules:
        if rule.endswith("/**"):
            prefix = rule[:-3].rstrip("/")
            if path == prefix or path.startswith(prefix + "/"):
                return True
        elif path == rule:
            return True
    return False


def _bind_subject(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    expected_base = contract["expected_base"]
    head = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    branch = _git(root, "branch", "--show-current")
    if branch != contract["expected_branch"]:
        raise CanaryError(
            f"branch drift: expected {contract['expected_branch']}, observed {branch or 'DETACHED'}"
        )
    if _git(root, "merge-base", expected_base, head) != expected_base:
        raise CanaryError("expected deterministic parent is not an ancestor of HEAD")
    changed = sorted(
        line
        for line in _git(root, "diff", "--name-only", f"{expected_base}..{head}").splitlines()
        if line
    )
    escaped = [path for path in changed if not _path_allowed(path, contract["allowed_paths"])]
    if escaped:
        raise CanaryError(f"write escaped runtime lease: {', '.join(escaped)}")
    return {
        "base_sha": expected_base,
        "head_sha": head,
        "tree_sha": tree,
        "branch": branch,
        "changed_paths": changed,
    }


def _changed_paths(root: Path, older: str, newer: str) -> list[str]:
    return sorted(
        line
        for line in _git(root, "diff", "--name-only", f"{older}..{newer}").splitlines()
        if line
    )


def _execute_workflow(root: Path, input_path: Path) -> dict[str, Any]:
    source = root / "src"
    sys.path.insert(0, str(source))
    try:
        from ai_product_notes.constraint_validator import validate_scene
        from ai_product_notes.scene_spec import SceneSpec

        raw = input_path.read_bytes()
        scene = SceneSpec.from_json(raw.decode("utf-8"))
        validation = validate_scene(scene)
    except (OSError, UnicodeError, ValueError) as exc:
        raise CanaryError(f"structured-scene workflow failed: {exc}") from exc
    finally:
        try:
            sys.path.remove(str(source))
        except ValueError:
            pass
    if validation.status != "PASS":
        raise CanaryError(
            "structured-scene validation failed: " + ", ".join(validation.violations)
        )
    return {
        "input_file_sha256": _sha256(raw),
        "scene_digest": scene.digest(),
        "validation_status": validation.status,
        "validation_receipt_digest": validation.receipt_digest,
        "validation_receipt_sha256": _sha256(validation.canonical_bytes()),
    }


def _run_bounded_workflow(
    root: Path, input_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    input_relative = _relative_path(root, input_path, "input_path")
    logical_command = [
        "python3",
        "scripts/run_structured_scene_canary.py",
        "--execute-worker",
        "--repo-root",
        ".",
        "--input",
        input_relative,
    ]
    try:
        completed = subprocess.run(
            [sys.executable, *logical_command[1:]],
            cwd=root,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise CanaryError("structured-scene worker exceeded 30 second bound") from exc
    command_receipt = {
        "command": logical_command,
        "exit_code": completed.returncode,
        "stdout_sha256": _sha256(completed.stdout),
        "stderr_sha256": _sha256(completed.stderr),
        "timeout_seconds": 30,
        "bounded": True,
    }
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise CanaryError(f"structured-scene worker failed: {detail or 'no stderr'}")
    try:
        workflow = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CanaryError("structured-scene worker returned invalid JSON") from exc
    if not isinstance(workflow, dict):
        raise CanaryError("structured-scene worker returned a non-object result")
    return workflow, command_receipt


def _subject_file_digests(root: Path, contract_path: Path, input_path: Path) -> dict[str, str]:
    paths = (
        contract_path,
        input_path,
        root / "scripts" / "run_structured_scene_canary.py",
        root / "src" / "ai_product_notes" / "scene_spec.py",
        root / "src" / "ai_product_notes" / "constraint_validator.py",
    )
    return {
        _relative_path(root, path, "subject file"): _sha256(path.read_bytes())
        for path in paths
    }


def _with_receipt_digest(receipt: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(receipt)
    result["receipt_digest"] = _sha256(_canonical_bytes(result))
    return result


def _receipt_digest_valid(receipt: dict[str, Any]) -> bool:
    unsigned = copy.deepcopy(receipt)
    claimed = unsigned.pop("receipt_digest", None)
    return claimed == _sha256(_canonical_bytes(unsigned))


def _create_receipt(
    root: Path,
    contract: dict[str, Any],
    contract_path: Path,
    receipt_path: Path,
    runtime_identity: str,
) -> None:
    subject = _bind_subject(root, contract)
    input_path = _declared_repo_path(
        root, contract["input_path"], "input_path", contract["allowed_paths"]
    )
    workflow, command_receipt = _run_bounded_workflow(root, input_path)
    receipt = _with_receipt_digest(
        {
            "schema_version": "structured-scene-runtime-receipt@1",
            "atom": "PREL-X02",
            "repository": contract["repository"],
            "authority_ceiling": contract["authority_ceiling"],
            "runtime": {
                "identity": runtime_identity,
                "hosted_ci": False,
                "command": ["python3", "scripts/run_structured_scene_canary.py", "--check"],
            },
            "subject": {
                **subject,
                "contract_sha256": _sha256(contract_path.read_bytes()),
                "subject_files": _subject_file_digests(root, contract_path, input_path),
            },
            "workflow": workflow,
            "command_receipt": command_receipt,
            "cleanup": {
                "pre_run": "CLEAN",
                "post_run": "RECEIPT_ONLY_PENDING_COMMIT",
                "allowed_dirty_paths": [contract["receipt_path"]],
                "out_of_lease_writes": [],
            },
            "evidence_state": {
                "deterministic_eval": "PASS",
                "local_runtime": "PASS",
                "user": "ABSENT",
                "paid": "ABSENT",
                "rights": "HUMAN_ADMIT_REQUIRED",
                "rendering_provider": "NOT_EXERCISED",
            },
            "queue_reconciliation": {
                "stage7_predecessor_receipt": "ABSENT",
                "machine_queue_advanced": False,
                "state": "RECONCILIATION_REQUIRED_BY_PREL_D02",
            },
            "non_claims": [
                "This receipt proves one local deterministic SceneSpec-to-validation workflow only.",
                "It does not prove rendering, model/provider quality, user value, paid demand or rights.",
                "It does not advance the Stage 7 machine queue or authorize merge, release or production.",
            ],
        }
    )
    if not receipt_path.parent.is_dir():
        raise CanaryError("receipt parent directory is absent")
    receipt_path.write_bytes(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        + b"\n"
    )
    dirty = sorted(
        line[3:]
        for line in _git(root, "status", "--porcelain").splitlines()
        if line
    )
    expected = [contract["receipt_path"]]
    if dirty != expected:
        receipt_path.unlink(missing_ok=True)
        raise CanaryError(
            f"post-run workspace differs outside receipt: expected={expected} observed={dirty}"
        )


def _verify_receipt(
    root: Path,
    contract: dict[str, Any],
    contract_path: Path,
    receipt_path: Path,
    runtime_identity: str,
) -> None:
    receipt = _read_json(receipt_path, "runtime receipt")
    if not _receipt_digest_valid(receipt):
        raise CanaryError("runtime receipt digest is stale")
    if receipt.get("schema_version") != "structured-scene-runtime-receipt@1":
        raise CanaryError("runtime receipt schema drifted")
    if receipt.get("authority_ceiling") != contract["authority_ceiling"]:
        raise CanaryError("runtime receipt authority drifted")
    if receipt.get("runtime", {}).get("identity") != runtime_identity:
        raise CanaryError("runtime receipt identity differs from current runtime")
    subject = receipt.get("subject", {})
    subject_head = subject.get("head_sha", "")
    current_head = _git(root, "rev-parse", "HEAD")
    try:
        actual_subject_tree = _git(root, "rev-parse", f"{subject_head}^{{tree}}")
    except CanaryError as exc:
        raise CanaryError("runtime receipt subject commit is unavailable") from exc
    if subject.get("tree_sha") != actual_subject_tree:
        raise CanaryError("runtime receipt subject tree is stale")
    if subject.get("base_sha") != contract["expected_base"]:
        raise CanaryError("runtime receipt base differs from contract")
    subject_changed = _changed_paths(root, contract["expected_base"], subject_head)
    if subject.get("changed_paths") != subject_changed:
        raise CanaryError("runtime receipt subject path set is stale")
    escaped = [
        path
        for path in subject_changed
        if not _path_allowed(path, contract["allowed_paths"])
    ]
    if escaped:
        raise CanaryError(f"receipt subject escaped runtime lease: {', '.join(escaped)}")
    if _git(root, "rev-parse", f"{current_head}^") != subject_head:
        raise CanaryError("current HEAD is not the single receipt commit over its subject")
    receipt_delta = _changed_paths(root, subject_head, current_head)
    if receipt_delta != [contract["receipt_path"]]:
        raise CanaryError("receipt commit contains changes beyond the receipt")
    _bind_subject(root, contract)
    input_path = _declared_repo_path(
        root, contract["input_path"], "input_path", contract["allowed_paths"]
    )
    observed_files = _subject_file_digests(root, contract_path, input_path)
    if subject.get("subject_files") != observed_files:
        raise CanaryError("runtime receipt subject files are stale")
    if subject.get("contract_sha256") != _sha256(contract_path.read_bytes()):
        raise CanaryError("runtime contract digest is stale")
    observed_workflow, observed_command = _run_bounded_workflow(root, input_path)
    if receipt.get("workflow") != observed_workflow:
        raise CanaryError("runtime workflow output is stale")
    if receipt.get("command_receipt") != observed_command:
        raise CanaryError("bounded command receipt is stale")


def run_check(root: Path, contract_path: Path, runtime_identity: str) -> str:
    _require_local_runtime(root, runtime_identity)
    _require_clean(root)
    contract_relative = _relative_path(root, contract_path, "contract path")
    contract = _read_json(contract_path, "runtime contract")
    _validate_contract(contract)
    if not _path_allowed(contract_relative, contract["allowed_paths"]):
        raise CanaryError("contract path escapes runtime lease")
    if runtime_identity not in contract["runtime_identities"]:
        raise CanaryError("runtime identity is not admitted by contract")
    _declared_repo_path(
        root, contract["input_path"], "input_path", contract["allowed_paths"]
    )
    receipt_path = _declared_repo_path(
        root, contract["receipt_path"], "receipt_path", contract["allowed_paths"]
    )
    if receipt_path.exists():
        _verify_receipt(root, contract, contract_path, receipt_path, runtime_identity)
        _require_clean(root)
        return "PASS receipt verified workspace=CLEAN cleanup=PASS"
    _create_receipt(root, contract, contract_path, receipt_path, runtime_identity)
    return "PASS receipt created"


def run_selftest() -> str:
    rules = [
        "scripts/run_structured_scene_canary.py",
        "evals/structured-scene/runtime/**",
    ]
    if not _path_allowed("evals/structured-scene/runtime/receipt.json", rules):
        raise CanaryError("selftest path-lease positive control failed")
    if _path_allowed("docs/git/STACKED_PRS.md", rules):
        raise CanaryError("selftest path-lease negative control failed")

    signed = _with_receipt_digest({"state": "PASS"})
    if not _receipt_digest_valid(signed):
        raise CanaryError("selftest receipt-digest positive control failed")
    signed["state"] = "STALE"
    if _receipt_digest_valid(signed):
        raise CanaryError("selftest receipt-digest mutation control failed")

    contract = {
        "schema_version": "structured-scene-runtime-contract@1",
        "atom": "PREL-X02",
        "repository": "ed3c/ai-product-notes",
        "expected_base": "0" * 40,
        "expected_branch": "fixture/runtime",
        "runtime_identities": ["CODEX_CLI_LOCAL", "CLAUDE_CODE_LOCAL"],
        "input_path": "evals/structured-scene/runtime/input.json",
        "receipt_path": "evals/structured-scene/runtime/receipt.json",
        "allowed_paths": rules,
        "authority_ceiling": "MERGE_ALLOWED",
    }
    try:
        _validate_contract(contract)
    except CanaryError:
        pass
    else:
        raise CanaryError("selftest authority-ceiling mutation was accepted")

    prior = os.environ.get("GITHUB_ACTIONS")
    os.environ["GITHUB_ACTIONS"] = "true"
    try:
        try:
            _require_local_runtime(ROOT, "CODEX_CLI_LOCAL")
        except CanaryError:
            pass
        else:
            raise CanaryError("selftest hosted-CI mutation was accepted")
    finally:
        if prior is None:
            os.environ.pop("GITHUB_ACTIONS", None)
        else:
            os.environ["GITHUB_ACTIONS"] = prior

    return "SELFTEST PASS controls=authority-ceiling,hosted-ci,path-lease,receipt-digest"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--selftest", action="store_true")
    modes.add_argument("--execute-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--input", type=Path, help=argparse.SUPPRESS)
    parser.add_argument(
        "--runtime-identity",
        choices=("CODEX_CLI_LOCAL", "CLAUDE_CODE_LOCAL"),
        default="CODEX_CLI_LOCAL",
    )
    args = parser.parse_args()

    try:
        if args.selftest:
            print(run_selftest())
            return 0
        root = args.repo_root.resolve()
        if args.execute_worker:
            if args.input is None:
                raise CanaryError("worker input is required")
            input_path = _declared_repo_path(
                root,
                args.input.as_posix(),
                "worker input",
                ["evals/structured-scene/runtime/**"],
            )
            sys.stdout.buffer.write(_canonical_bytes(_execute_workflow(root, input_path)))
            return 0
        contract_path = (
            args.contract.resolve() if args.contract else root / DEFAULT_CONTRACT
        )
        print(run_check(root, contract_path, args.runtime_identity))
    except CanaryError as exc:
        print(f"BLOCK {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
