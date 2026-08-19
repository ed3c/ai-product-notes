from __future__ import annotations

import copy
import hashlib
import json
from itertools import combinations
from typing import Any

from .scene_spec import CONSTRAINT_KINDS, SceneSpec, SceneSpecError

VALIDATOR_VERSION = "constraint-validator@1"
RECEIPT_SCHEMA_VERSION = "scene-validation-receipt@1"
AUTHORITY_CEILING = "DETERMINISTIC_IMPLEMENTATION_ONLY"


class ConstraintValidationError(ValueError):
    """Raised when the deterministic validator contract itself is unusable."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def _digest_without_receipt_digest(value: dict[str, Any]) -> str:
    payload = copy.deepcopy(value)
    payload.pop("receipt_digest", None)
    return "sha256:" + hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _stable_parameter_failure(constraint_id: str, names: list[str]) -> str:
    return f"RULE_PARAMETERS_MISSING:{constraint_id}:{','.join(sorted(names))}"


def _rectangles_overlap(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["x"] < right["x"] + right["width"]
        and right["x"] < left["x"] + left["width"]
        and left["y"] < right["y"] + right["height"]
        and right["y"] < left["y"] + left["height"]
    )


class ValidationReceipt:
    """Deterministic receipt bound to exactly one canonical SceneSpec digest."""

    def __init__(self, *, scene_id: str, scene_digest: str, violations: list[str]):
        if not isinstance(scene_id, str) or not scene_id:
            raise ConstraintValidationError("scene_id must be non-empty text")
        if not isinstance(scene_digest, str) or not scene_digest.startswith("sha256:"):
            raise ConstraintValidationError("scene_digest must be a sha256 digest")
        if any(not isinstance(item, str) or not item for item in violations):
            raise ConstraintValidationError("violations must contain non-empty strings")

        stable_violations = sorted(set(violations))
        payload = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "validator_version": VALIDATOR_VERSION,
            "authority_ceiling": AUTHORITY_CEILING,
            "scene_id": scene_id,
            "scene_digest": scene_digest,
            "status": "PASS" if not stable_violations else "FAIL",
            "violations": stable_violations,
            "receipt_digest": "sha256:" + "0" * 64,
        }
        payload["receipt_digest"] = _digest_without_receipt_digest(payload)
        self._payload = payload

    @property
    def status(self) -> str:
        return self._payload["status"]

    @property
    def scene_digest(self) -> str:
        return self._payload["scene_digest"]

    @property
    def receipt_digest(self) -> str:
        return self._payload["receipt_digest"]

    @property
    def violations(self) -> tuple[str, ...]:
        return tuple(self._payload["violations"])

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._payload)

    def canonical_json(self) -> str:
        return _canonical_json(self._payload)

    def canonical_bytes(self) -> bytes:
        return self.canonical_json().encode("utf-8")

    def state_for(self, scene: SceneSpec) -> str:
        if not isinstance(scene, SceneSpec):
            raise ConstraintValidationError("state_for requires a SceneSpec")
        return self.status if scene.digest() == self.scene_digest else "STALE"


def _validate_asset_references(scene: dict[str, Any]) -> list[str]:
    asset_ids = {asset["asset_id"] for asset in scene["assets"]}
    return [
        f"ASSET_REF_MISSING:{node['node_id']}:{node['asset_id']}"
        for node in scene["nodes"]
        if node["asset_id"] not in asset_ids
    ]


def _validate_within_canvas(
    constraint: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    canvas: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    constraint_id = constraint["constraint_id"]
    margin = constraint["parameters"].get("margin", 0)
    for node_id in constraint["subject_ids"]:
        node = nodes.get(node_id)
        if node is None:
            failures.append(f"SUBJECT_MISSING:{constraint_id}:{node_id}")
            continue
        if (
            node["x"] < margin
            or node["y"] < margin
            or node["x"] + node["width"] > canvas["width"] - margin
            or node["y"] + node["height"] > canvas["height"] - margin
        ):
            failures.append(f"WITHIN_CANVAS:{constraint_id}:{node_id}")
    return failures


def _validate_non_overlap(
    constraint: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    constraint_id = constraint["constraint_id"]
    subject_ids = sorted(constraint["subject_ids"])
    if len(subject_ids) < 2:
        failures.append(f"NON_OVERLAP_ARITY:{constraint_id}")
        return failures

    missing = [node_id for node_id in subject_ids if node_id not in nodes]
    failures.extend(f"SUBJECT_MISSING:{constraint_id}:{node_id}" for node_id in missing)
    present = [node_id for node_id in subject_ids if node_id in nodes]
    for left_id, right_id in combinations(present, 2):
        if _rectangles_overlap(nodes[left_id], nodes[right_id]):
            failures.append(f"NON_OVERLAP:{constraint_id}:{left_id}:{right_id}")
    return failures


def _validate_lock_aspect(
    constraint: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    constraint_id = constraint["constraint_id"]
    params = constraint["parameters"]
    required = [name for name in ("ratio_num", "ratio_den") if name not in params]
    if required:
        return [_stable_parameter_failure(constraint_id, required)]

    for node_id in constraint["subject_ids"]:
        node = nodes.get(node_id)
        if node is None:
            failures.append(f"SUBJECT_MISSING:{constraint_id}:{node_id}")
            continue
        if node["width"] * params["ratio_den"] != node["height"] * params["ratio_num"]:
            failures.append(f"LOCK_ASPECT:{constraint_id}:{node_id}")
    return failures


def _validate_anchor(
    constraint: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    constraint_id = constraint["constraint_id"]
    params = constraint["parameters"]
    if "axis" not in params:
        return [_stable_parameter_failure(constraint_id, ["axis"])]
    axis = params["axis"]
    target_key = "target_x" if axis == "x" else "target_y"
    if target_key not in params:
        return [_stable_parameter_failure(constraint_id, [target_key])]

    for node_id in constraint["subject_ids"]:
        node = nodes.get(node_id)
        if node is None:
            failures.append(f"SUBJECT_MISSING:{constraint_id}:{node_id}")
            continue
        if node[axis] != params[target_key]:
            failures.append(f"ANCHOR:{constraint_id}:{node_id}:{axis}")
    return failures


def validate_scene(scene: SceneSpec) -> ValidationReceipt:
    """Validate one SceneSpec without mutating it and emit a digest-bound receipt."""

    if not isinstance(scene, SceneSpec):
        raise ConstraintValidationError("validate_scene requires a SceneSpec")

    data = scene.to_dict()
    nodes = {node["node_id"]: node for node in data["nodes"]}
    violations = _validate_asset_references(data)

    validators = {
        "WITHIN_CANVAS": lambda item: _validate_within_canvas(item, nodes, data["canvas"]),
        "NON_OVERLAP": lambda item: _validate_non_overlap(item, nodes),
        "LOCK_ASPECT": lambda item: _validate_lock_aspect(item, nodes),
        "ANCHOR": lambda item: _validate_anchor(item, nodes),
    }

    for constraint in data["constraints"]:
        kind = constraint["kind"]
        if kind not in CONSTRAINT_KINDS or kind not in validators:
            violations.append(
                f"UNKNOWN_RULE:{constraint['constraint_id']}:{kind}"
            )
            continue
        violations.extend(validators[kind](constraint))

    return ValidationReceipt(
        scene_id=data["scene_id"],
        scene_digest=scene.digest(),
        violations=violations,
    )
