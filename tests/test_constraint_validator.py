from __future__ import annotations

import ast
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.constraint_validator import validate_scene  # noqa: E402
from ai_product_notes.scene_spec import SceneSpec  # noqa: E402


def valid_scene() -> dict:
    return {
        "schema_version": "scene-spec@1",
        "scene_id": "scene:validator-canary",
        "canvas": {"width": 1000, "height": 800, "unit": "px"},
        "assets": [
            {"asset_id": "asset:a", "kind": "IMAGE", "content_ref": "sha256:a"},
            {"asset_id": "asset:b", "kind": "SHAPE", "content_ref": "shape:b"},
        ],
        "nodes": [
            {
                "node_id": "node:a",
                "asset_id": "asset:a",
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 200,
                "z_index": 1,
                "rotation_mdeg": 0,
            },
            {
                "node_id": "node:b",
                "asset_id": "asset:b",
                "x": 500,
                "y": 100,
                "width": 200,
                "height": 100,
                "z_index": 2,
                "rotation_mdeg": 0,
            },
        ],
        "constraints": [
            {
                "constraint_id": "constraint:bounds",
                "kind": "WITHIN_CANVAS",
                "subject_ids": ["node:b", "node:a"],
                "parameters": {"margin": 20},
            },
            {
                "constraint_id": "constraint:no-overlap",
                "kind": "NON_OVERLAP",
                "subject_ids": ["node:b", "node:a"],
                "parameters": {},
            },
            {
                "constraint_id": "constraint:aspect",
                "kind": "LOCK_ASPECT",
                "subject_ids": ["node:a"],
                "parameters": {"ratio_num": 1, "ratio_den": 1},
            },
            {
                "constraint_id": "constraint:anchor",
                "kind": "ANCHOR",
                "subject_ids": ["node:a"],
                "parameters": {"axis": "x", "target_x": 100},
            },
        ],
    }


class ConstraintValidatorTests(unittest.TestCase):
    def test_valid_scene_yields_digest_bound_pass_receipt(self) -> None:
        scene = SceneSpec.from_inputs(valid_scene())
        receipt = validate_scene(scene)
        self.assertEqual("PASS", receipt.status)
        self.assertEqual(scene.digest(), receipt.scene_digest)
        self.assertEqual((), receipt.violations)
        self.assertTrue(receipt.receipt_digest.startswith("sha256:"))
        self.assertEqual("PASS", receipt.state_for(scene))

    def test_equivalent_input_order_yields_same_receipt_bytes(self) -> None:
        left = valid_scene()
        right = copy.deepcopy(left)
        right["assets"].reverse()
        right["nodes"].reverse()
        right["constraints"].reverse()
        for item in right["constraints"]:
            item["subject_ids"].reverse()
        left_receipt = validate_scene(SceneSpec.from_inputs(left))
        right_receipt = validate_scene(SceneSpec.from_inputs(right))
        self.assertEqual(left_receipt.canonical_json(), right_receipt.canonical_json())
        self.assertEqual(left_receipt.receipt_digest, right_receipt.receipt_digest)

    def test_missing_asset_reference_fails_with_stable_identifier(self) -> None:
        payload = valid_scene()
        payload["nodes"][0]["asset_id"] = "asset:missing"
        receipt = validate_scene(SceneSpec.from_inputs(payload))
        self.assertEqual("FAIL", receipt.status)
        self.assertIn("ASSET_REF_MISSING:node:a:asset:missing", receipt.violations)

    def test_out_of_bounds_scene_fails_with_stable_identifier(self) -> None:
        payload = valid_scene()
        payload["nodes"][0]["x"] = 900
        receipt = validate_scene(SceneSpec.from_inputs(payload))
        self.assertIn("WITHIN_CANVAS:constraint:bounds:node:a", receipt.violations)

    def test_non_overlap_constraint_detects_conflict(self) -> None:
        payload = valid_scene()
        payload["nodes"][1]["x"] = 150
        payload["nodes"][1]["y"] = 150
        receipt = validate_scene(SceneSpec.from_inputs(payload))
        self.assertIn(
            "NON_OVERLAP:constraint:no-overlap:node:a:node:b",
            receipt.violations,
        )

    def test_lock_aspect_constraint_detects_conflict(self) -> None:
        payload = valid_scene()
        payload["nodes"][0]["width"] = 201
        receipt = validate_scene(SceneSpec.from_inputs(payload))
        self.assertIn("LOCK_ASPECT:constraint:aspect:node:a", receipt.violations)

    def test_anchor_constraint_detects_conflict(self) -> None:
        payload = valid_scene()
        payload["nodes"][0]["x"] = 101
        receipt = validate_scene(SceneSpec.from_inputs(payload))
        self.assertIn("ANCHOR:constraint:anchor:node:a:x", receipt.violations)

    def test_validator_does_not_mutate_scene(self) -> None:
        scene = SceneSpec.from_inputs(valid_scene())
        before = scene.canonical_json()
        validate_scene(scene)
        self.assertEqual(before, scene.canonical_json())

    def test_old_receipt_becomes_stale_after_semantic_mutation(self) -> None:
        original = valid_scene()
        first_scene = SceneSpec.from_inputs(original)
        receipt = validate_scene(first_scene)
        changed = copy.deepcopy(original)
        changed["nodes"][0]["x"] = 101
        changed_scene = SceneSpec.from_inputs(changed)
        self.assertEqual("STALE", receipt.state_for(changed_scene))

    def test_unknown_rule_fails_closed(self) -> None:
        scene = SceneSpec.from_inputs(valid_scene())
        scene._data["constraints"][0]["kind"] = "FUTURE_RULE"  # planted internal-corruption control
        receipt = validate_scene(scene)
        self.assertIn(
            "UNKNOWN_RULE:constraint:anchor:FUTURE_RULE",
            receipt.violations,
        )
        self.assertEqual("FAIL", receipt.status)

    def test_missing_rule_parameters_fail_closed(self) -> None:
        payload = valid_scene()
        for item in payload["constraints"]:
            if item["constraint_id"] == "constraint:anchor":
                item["parameters"] = {}
        receipt = validate_scene(SceneSpec.from_inputs(payload))
        self.assertIn(
            "RULE_PARAMETERS_MISSING:constraint:anchor:axis",
            receipt.violations,
        )

    def test_validator_imports_no_rendering_model_or_provider_sdk(self) -> None:
        module_path = SRC / "ai_product_notes" / "constraint_validator.py"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        self.assertTrue(roots.issubset({"__future__", "copy", "hashlib", "json", "itertools", "typing", "scene_spec"}))
        self.assertFalse({"requests", "openai", "anthropic", "torch", "transformers"} & roots)


if __name__ == "__main__":
    unittest.main()
