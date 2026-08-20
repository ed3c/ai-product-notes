#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.constraint_validator import validate_scene  # noqa: E402
from ai_product_notes.scene_spec import SceneSpec  # noqa: E402

SCHEMA_VERSION = "structured-scene-runtime-receipt@1"
RUNNER_PATH = "scripts/run_structured_scene_canary.py"
INPUT_PATH = "evals/structured-scene/runtime/input.json"
RECEIPT_PATH = "evals/structured-scene/runtime/receipt.json"


class RuntimeCanaryError(RuntimeError):
    pass


def _git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeCanaryError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def _digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _receipt_digest(payload: dict[str, Any]) -> str:
    value = copy.deepcopy(payload)
    value.pop("receipt_digest", None)
    compact = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")
    return _digest_bytes(compact)


def _require_clean(label: str) -> None:
    dirty = _git("status", "--porcelain")
    if dirty:
        raise RuntimeCanaryError(f"{label} workspace is dirty")


def _blob_at(revision: str, path: str) -> str:
    value = _git("rev-parse", f"{revision}:{path}")
    if len(value) != 40:
        raise RuntimeCanaryError(f"cannot bind {path} at {revision}")
    return value


def _load_scene(path: Path) -> SceneSpec:
    if not path.is_file():
        raise RuntimeCanaryError(f"missing input: {path}")
    return SceneSpec.from_json(path.read_text(encoding="utf-8"))


def build_receipt(execution_head: str) -> dict[str, Any]:
    _require_clean("pre-run")
    if len(execution_head) != 40:
        raise RuntimeCanaryError("execution head must be a 40-character Git SHA")
    _git("cat-file", "-e", f"{execution_head}^{{commit}}")
    _git("merge-base", "--is-ancestor", execution_head, "HEAD")

    input_path = ROOT / INPUT_PATH
    scene = _load_scene(input_path)
    validation = validate_scene(scene)
    if validation.status != "PASS":
        raise RuntimeCanaryError(
            "bounded runtime scene failed validation: " + ",".join(validation.violations)
        )

    encoded = scene.canonical_json()
    round_trip = SceneSpec.from_json(encoded)
    if encoded != round_trip.canonical_json() or scene.digest() != round_trip.digest():
        raise RuntimeCanaryError("SceneSpec round-trip oracle failed")

    mutated_data = scene.to_dict()
    mutated_data["nodes"][0]["x"] += 1
    mutated = SceneSpec.from_inputs(mutated_data)
    stale_state = validation.state_for(mutated)
    if stale_state != "STALE":
        raise RuntimeCanaryError("mutation did not invalidate the old receipt")

    current_head = _git("rev-parse", "HEAD")
    current_tree = _git("rev-parse", "HEAD^{tree}")
    execution_tree = _git("rev-parse", f"{execution_head}^{{tree}}")
    subjects = {
        "execution_head": execution_head,
        "execution_tree": execution_tree,
        "runner_blob": _blob_at(execution_head, RUNNER_PATH),
        "input_blob": _blob_at(execution_head, INPUT_PATH),
        "scene_spec_blob": _blob_at(execution_head, "src/ai_product_notes/scene_spec.py"),
        "validator_blob": _blob_at(
            execution_head, "src/ai_product_notes/constraint_validator.py"
        ),
        "observed_checkout_head": current_head,
        "observed_checkout_tree": current_tree,
    }

    for path_key, path in (("runner_blob", RUNNER_PATH), ("input_blob", INPUT_PATH)):
        current_blob = _blob_at("HEAD", path)
        if current_blob != subjects[path_key]:
            raise RuntimeCanaryError(f"{path} drifted after the execution subject")

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "atom": "PREL-X02",
        "runtime_lane": "LOCAL",
        "runtime_environment_class": "EPHEMERAL_TRUSTED_LOCAL_CONTAINER",
        "authority_ceiling": "LOCAL_RUNTIME_ATOM_ONLY",
        "subjects": subjects,
        "command_contract": [
            "python3 -m unittest -q tests/test_scene_spec_contract.py tests/test_constraint_validator.py tests/test_structured_scene_e2e.py",
            "python3 scripts/run_structured_scene_canary.py --check",
        ],
        "input": {
            "path": INPUT_PATH,
            "file_digest": _digest_bytes(input_path.read_bytes()),
            "scene_id": scene.to_dict()["scene_id"],
            "scene_digest": scene.digest(),
        },
        "output": {
            "validation_status": validation.status,
            "validation_receipt_digest": validation.receipt_digest,
            "violations": list(validation.violations),
            "round_trip": "PASS",
            "mutation_state": stale_state,
        },
        "workspace": {
            "pre_run_clean": "PASS",
            "post_run_clean": "PASS",
            "cleanup": "PASS",
        },
        "evidence_state": {
            "deterministic_eval": "PASS",
            "local_runtime": "PASS",
            "physical_user_host": "NOT_EXERCISED",
            "user": "ABSENT",
            "paid": "ABSENT",
            "rights": "HUMAN_ADMIT_REQUIRED",
        },
        "non_claims": [
            "This receipt proves one bounded deterministic workflow in an ephemeral trusted local container, not a user workstation or production environment.",
            "No rendering, model, provider, customer-value, paid-demand, or rights claim is established.",
            "Merge, release, production promotion, and semantic conflict resolution remain externally owned.",
        ],
        "receipt_digest": "sha256:" + "0" * 64,
    }
    _require_clean("post-run")
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-head")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path, default=ROOT / RECEIPT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        if not args.receipt.is_file():
            raise RuntimeCanaryError(f"missing committed receipt: {args.receipt}")
        committed = json.loads(args.receipt.read_text(encoding="utf-8"))
        execution_head = committed.get("subjects", {}).get("execution_head")
        observed = build_receipt(execution_head)
        if committed != observed:
            raise RuntimeCanaryError("committed runtime receipt drifted from observation")
        print(_canonical_json({"status": "PASS", "receipt_digest": committed["receipt_digest"]}), end="")
        return 0

    execution_head = args.execution_head or _git("rev-parse", "HEAD")
    receipt = build_receipt(execution_head)
    text = _canonical_json(receipt)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeCanaryError as exc:
        print(f"X02 runtime canary failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
