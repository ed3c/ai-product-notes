from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

SCHEMA_VERSION = "scene-spec@1"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{1,127}$")
ASSET_KINDS = {"IMAGE", "TEXT", "SHAPE"}
CONSTRAINT_KINDS = {"WITHIN_CANVAS", "NON_OVERLAP", "LOCK_ASPECT", "ANCHOR"}
PARAMETER_KEYS = {"margin", "axis", "target_x", "target_y", "ratio_num", "ratio_den"}
TOP_LEVEL_KEYS = {"schema_version", "scene_id", "canvas", "assets", "nodes", "constraints"}
CANVAS_KEYS = {"width", "height", "unit"}
ASSET_KEYS = {"asset_id", "kind", "content_ref"}
NODE_KEYS = {"node_id", "asset_id", "x", "y", "width", "height", "z_index", "rotation_mdeg"}
CONSTRAINT_KEYS = {"constraint_id", "kind", "subject_ids", "parameters"}


class SceneSpecError(ValueError):
    """Raised when SceneSpec input is not part of the admitted deterministic contract."""


def _exact_keys(value: dict[str, Any], expected: set[str], where: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        raise SceneSpecError(f"{where} missing keys: {', '.join(missing)}")
    if extra:
        raise SceneSpecError(f"{where} has unknown keys: {', '.join(extra)}")


def _object(value: Any, where: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise SceneSpecError(f"{where} must be an object")
    return value


def _array(value: Any, where: str) -> list[Any]:
    if type(value) is not list:
        raise SceneSpecError(f"{where} must be an array")
    return value


def _text(value: Any, where: str, *, max_length: int = 500) -> str:
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise SceneSpecError(f"{where} must be non-empty text up to {max_length} characters")
    return value


def _identifier(value: Any, where: str) -> str:
    text = _text(value, where, max_length=128)
    if not ID_RE.fullmatch(text):
        raise SceneSpecError(f"{where} is not a valid identifier")
    return text


def _integer(value: Any, where: str, *, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise SceneSpecError(f"{where} must be an integer in [{minimum}, {maximum}]")
    return value


def _unique(values: list[str], where: str) -> None:
    if len(values) != len(set(values)):
        raise SceneSpecError(f"{where} contains duplicate identifiers")


def _no_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SceneSpecError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _normalize_canvas(raw: Any) -> dict[str, Any]:
    canvas = _object(raw, "canvas")
    _exact_keys(canvas, CANVAS_KEYS, "canvas")
    if canvas["unit"] != "px":
        raise SceneSpecError("canvas.unit must be px")
    return {
        "width": _integer(canvas["width"], "canvas.width", minimum=1, maximum=100000),
        "height": _integer(canvas["height"], "canvas.height", minimum=1, maximum=100000),
        "unit": "px",
    }


def _normalize_asset(raw: Any, index: int) -> dict[str, Any]:
    asset = _object(raw, f"assets[{index}]")
    _exact_keys(asset, ASSET_KEYS, f"assets[{index}]")
    asset_id = _identifier(asset["asset_id"], f"assets[{index}].asset_id")
    kind = _text(asset["kind"], f"assets[{index}].kind")
    if kind not in ASSET_KINDS:
        raise SceneSpecError(f"assets[{index}].kind is not admitted")
    return {
        "asset_id": asset_id,
        "kind": kind,
        "content_ref": _text(asset["content_ref"], f"assets[{index}].content_ref"),
    }


def _normalize_node(raw: Any, index: int) -> dict[str, Any]:
    node = _object(raw, f"nodes[{index}]")
    _exact_keys(node, NODE_KEYS, f"nodes[{index}]")
    return {
        "node_id": _identifier(node["node_id"], f"nodes[{index}].node_id"),
        "asset_id": _identifier(node["asset_id"], f"nodes[{index}].asset_id"),
        "x": _integer(node["x"], f"nodes[{index}].x", minimum=-1000000, maximum=1000000),
        "y": _integer(node["y"], f"nodes[{index}].y", minimum=-1000000, maximum=1000000),
        "width": _integer(node["width"], f"nodes[{index}].width", minimum=1, maximum=1000000),
        "height": _integer(node["height"], f"nodes[{index}].height", minimum=1, maximum=1000000),
        "z_index": _integer(node["z_index"], f"nodes[{index}].z_index", minimum=-1000000, maximum=1000000),
        "rotation_mdeg": _integer(
            node["rotation_mdeg"],
            f"nodes[{index}].rotation_mdeg",
            minimum=-360000,
            maximum=360000,
        ),
    }


def _normalize_parameters(raw: Any, where: str) -> dict[str, Any]:
    params = _object(raw, where)
    extra = sorted(set(params) - PARAMETER_KEYS)
    if extra:
        raise SceneSpecError(f"{where} has unknown keys: {', '.join(extra)}")
    normalized: dict[str, Any] = {}
    for key, value in params.items():
        if key == "axis":
            if value not in {"x", "y"}:
                raise SceneSpecError(f"{where}.axis must be x or y")
            normalized[key] = value
        elif key in {"ratio_num", "ratio_den"}:
            normalized[key] = _integer(value, f"{where}.{key}", minimum=1, maximum=1000000)
        elif key == "margin":
            normalized[key] = _integer(value, f"{where}.{key}", minimum=0, maximum=1000000)
        else:
            normalized[key] = _integer(
                value,
                f"{where}.{key}",
                minimum=-1000000,
                maximum=1000000,
            )
    return normalized


def _normalize_constraint(raw: Any, index: int) -> dict[str, Any]:
    constraint = _object(raw, f"constraints[{index}]")
    _exact_keys(constraint, CONSTRAINT_KEYS, f"constraints[{index}]")
    kind = _text(constraint["kind"], f"constraints[{index}].kind")
    if kind not in CONSTRAINT_KINDS:
        raise SceneSpecError(f"constraints[{index}].kind is not admitted")
    subjects = [
        _identifier(item, f"constraints[{index}].subject_ids[]")
        for item in _array(constraint["subject_ids"], f"constraints[{index}].subject_ids")
    ]
    if not subjects:
        raise SceneSpecError(f"constraints[{index}].subject_ids must not be empty")
    _unique(subjects, f"constraints[{index}].subject_ids")
    return {
        "constraint_id": _identifier(
            constraint["constraint_id"],
            f"constraints[{index}].constraint_id",
        ),
        "kind": kind,
        "subject_ids": sorted(subjects),
        "parameters": _normalize_parameters(
            constraint["parameters"],
            f"constraints[{index}].parameters",
        ),
    }


def normalize_scene(raw: Any) -> dict[str, Any]:
    scene = _object(raw, "scene")
    _exact_keys(scene, TOP_LEVEL_KEYS, "scene")
    if scene["schema_version"] != SCHEMA_VERSION:
        raise SceneSpecError(f"scene.schema_version must be {SCHEMA_VERSION}")

    assets = [_normalize_asset(item, i) for i, item in enumerate(_array(scene["assets"], "assets"))]
    nodes = [_normalize_node(item, i) for i, item in enumerate(_array(scene["nodes"], "nodes"))]
    constraints = [
        _normalize_constraint(item, i)
        for i, item in enumerate(_array(scene["constraints"], "constraints"))
    ]

    _unique([item["asset_id"] for item in assets], "assets")
    _unique([item["node_id"] for item in nodes], "nodes")
    _unique([item["constraint_id"] for item in constraints], "constraints")

    return {
        "schema_version": SCHEMA_VERSION,
        "scene_id": _identifier(scene["scene_id"], "scene.scene_id"),
        "canvas": _normalize_canvas(scene["canvas"]),
        "assets": sorted(assets, key=lambda item: item["asset_id"]),
        "nodes": sorted(nodes, key=lambda item: item["node_id"]),
        "constraints": sorted(constraints, key=lambda item: item["constraint_id"]),
    }


class SceneSpec:
    """Immutable-by-copy deterministic SceneSpec value object."""

    def __init__(self, data: Any):
        self._data = normalize_scene(data)

    @classmethod
    def from_inputs(cls, data: Any) -> "SceneSpec":
        return cls(data)

    @classmethod
    def from_json(cls, text: str) -> "SceneSpec":
        if not isinstance(text, str):
            raise SceneSpecError("SceneSpec JSON input must be text")
        try:
            parsed = json.loads(text, object_pairs_hook=_no_duplicate_object_pairs)
        except (json.JSONDecodeError, TypeError) as exc:
            raise SceneSpecError(f"invalid SceneSpec JSON: {exc}") from exc
        return cls(parsed)

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)

    def canonical_json(self) -> str:
        return json.dumps(
            self._data,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        ) + "\n"

    def canonical_bytes(self) -> bytes:
        return self.canonical_json().encode("utf-8")

    def digest(self) -> str:
        return "sha256:" + hashlib.sha256(self.canonical_bytes()).hexdigest()
