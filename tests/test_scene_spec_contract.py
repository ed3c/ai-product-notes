from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.scene_spec import SceneSpec, SceneSpecError  # noqa: E402


def canonical_cases() -> list[dict]:
    return [
        {
            "schema_version": "scene-spec@1",
            "scene_id": "scene:single-product",
            "canvas": {"width": 1200, "height": 1200, "unit": "px"},
            "assets": [
                {"asset_id": "asset:product", "kind": "IMAGE", "content_ref": "sha256:product-a"}
            ],
            "nodes": [
                {
                    "node_id": "node:product",
                    "asset_id": "asset:product",
                    "x": 100,
                    "y": 140,
                    "width": 800,
                    "height": 800,
                    "z_index": 1,
                    "rotation_mdeg": 0,
                }
            ],
            "constraints": [
                {
                    "constraint_id": "constraint:canvas",
                    "kind": "WITHIN_CANVAS",
                    "subject_ids": ["node:product"],
                    "parameters": {"margin": 32},
                }
            ],
        },
        {
            "schema_version": "scene-spec@1",
            "scene_id": "scene:hero-with-label",
            "canvas": {"height": 900, "unit": "px", "width": 1600},
            "assets": [
                {"content_ref": "copy:headline", "kind": "TEXT", "asset_id": "asset:headline"},
                {"content_ref": "sha256:hero-b", "asset_id": "asset:hero", "kind": "IMAGE"},
            ],
            "nodes": [
                {
                    "asset_id": "asset:headline",
                    "height": 100,
                    "node_id": "node:headline",
                    "rotation_mdeg": 0,
                    "width": 500,
                    "x": 80,
                    "y": 90,
                    "z_index": 2,
                },
                {
                    "height": 700,
                    "x": 720,
                    "node_id": "node:hero",
                    "rotation_mdeg": 0,
                    "asset_id": "asset:hero",
                    "z_index": 1,
                    "y": 80,
                    "width": 700,
                },
            ],
            "constraints": [
                {
                    "parameters": {},
                    "subject_ids": ["node:hero", "node:headline"],
                    "kind": "NON_OVERLAP",
                    "constraint_id": "constraint:no-overlap",
                },
                {
                    "parameters": {"target_y": 90, "axis": "y"},
                    "kind": "ANCHOR",
                    "constraint_id": "constraint:headline-y",
                    "subject_ids": ["node:headline"],
                },
            ],
        },
        {
            "schema_version": "scene-spec@1",
            "scene_id": "scene:editable-card",
            "canvas": {"width": 1024, "unit": "px", "height": 1024},
            "assets": [
                {"asset_id": "asset:card", "content_ref": "shape:card", "kind": "SHAPE"},
                {"asset_id": "asset:badge", "content_ref": "shape:badge", "kind": "SHAPE"},
            ],
            "nodes": [
                {
                    "node_id": "node:badge",
                    "asset_id": "asset:badge",
                    "x": 700,
                    "y": 80,
                    "width": 180,
                    "height": 80,
                    "z_index": 2,
                    "rotation_mdeg": 15000,
                },
                {
                    "node_id": "node:card",
                    "asset_id": "asset:card",
                    "x": 100,
                    "y": 100,
                    "width": 824,
                    "height": 824,
                    "z_index": 1,
                    "rotation_mdeg": 0,
                },
            ],
            "constraints": [
                {
                    "constraint_id": "constraint:card-bounds",
                    "kind": "WITHIN_CANVAS",
                    "subject_ids": ["node:card", "node:badge"],
                    "parameters": {"margin": 20},
                }
            ],
        },
    ]


class SceneSpecContractTests(unittest.TestCase):
    def test_three_canonical_scenes_round_trip_byte_stably(self) -> None:
        for payload in canonical_cases():
            first = SceneSpec.from_inputs(payload)
            encoded = first.canonical_json()
            second = SceneSpec.from_json(encoded)
            self.assertEqual(encoded, second.canonical_json())
            self.assertEqual(first.digest(), second.digest())

    def test_mapping_and_collection_order_do_not_change_canonical_bytes(self) -> None:
        payload = canonical_cases()[1]
        reordered = {
            "constraints": list(reversed(copy.deepcopy(payload["constraints"]))),
            "nodes": list(reversed(copy.deepcopy(payload["nodes"]))),
            "assets": list(reversed(copy.deepcopy(payload["assets"]))),
            "canvas": {"unit": "px", "height": 900, "width": 1600},
            "scene_id": payload["scene_id"],
            "schema_version": payload["schema_version"],
        }
        self.assertEqual(
            SceneSpec.from_inputs(payload).canonical_json(),
            SceneSpec.from_inputs(reordered).canonical_json(),
        )

    def test_semantic_mutation_changes_digest(self) -> None:
        payload = canonical_cases()[0]
        original = SceneSpec.from_inputs(payload)
        mutated = copy.deepcopy(payload)
        mutated["nodes"][0]["x"] += 1
        self.assertNotEqual(original.digest(), SceneSpec.from_inputs(mutated).digest())

    def test_unknown_top_level_field_is_rejected(self) -> None:
        payload = canonical_cases()[0]
        payload["provider"] = "not-admitted"
        with self.assertRaises(SceneSpecError):
            SceneSpec.from_inputs(payload)

    def test_unknown_nested_field_is_rejected(self) -> None:
        payload = canonical_cases()[0]
        payload["nodes"][0]["renderer"] = "not-admitted"
        with self.assertRaises(SceneSpecError):
            SceneSpec.from_inputs(payload)

    def test_unknown_constraint_parameter_is_rejected(self) -> None:
        payload = canonical_cases()[0]
        payload["constraints"][0]["parameters"]["provider_hint"] = "not-admitted"
        with self.assertRaises(SceneSpecError):
            SceneSpec.from_inputs(payload)

    def test_duplicate_ids_are_rejected(self) -> None:
        payload = canonical_cases()[1]
        payload["assets"][1]["asset_id"] = payload["assets"][0]["asset_id"]
        with self.assertRaises(SceneSpecError):
            SceneSpec.from_inputs(payload)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        raw = '{"schema_version":"scene-spec@1","scene_id":"scene:x","scene_id":"scene:y","canvas":{},"assets":[],"nodes":[],"constraints":[]}'
        with self.assertRaises(SceneSpecError):
            SceneSpec.from_json(raw)

    def test_boolean_is_not_accepted_as_integer(self) -> None:
        payload = canonical_cases()[0]
        payload["canvas"]["width"] = True
        with self.assertRaises(SceneSpecError):
            SceneSpec.from_inputs(payload)

    def test_to_dict_is_defensive_copy(self) -> None:
        spec = SceneSpec.from_inputs(canonical_cases()[0])
        exported = spec.to_dict()
        exported["canvas"]["width"] = 1
        self.assertNotEqual(exported, spec.to_dict())

    def test_canonical_json_is_valid_json_and_newline_terminated(self) -> None:
        spec = SceneSpec.from_inputs(canonical_cases()[2])
        text = spec.canonical_json()
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(spec.to_dict(), json.loads(text))

    def test_core_contract_contains_no_rendering_or_provider_field(self) -> None:
        keys = set(SceneSpec.from_inputs(canonical_cases()[0]).to_dict())
        self.assertNotIn("renderer", keys)
        self.assertNotIn("provider", keys)
        self.assertNotIn("model", keys)


if __name__ == "__main__":
    unittest.main()
