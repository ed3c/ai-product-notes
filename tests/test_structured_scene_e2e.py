from __future__ import annotations

import copy
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.constraint_validator import validate_scene  # noqa: E402
from ai_product_notes.scene_spec import SceneSpec  # noqa: E402

CANARY = ROOT / "evals" / "structured-scene" / "deterministic"
CASES_PATH = CANARY / "cases.json"
RECEIPT_PATH = CANARY / "receipt.json"

NON_CLAIMS = [
    "This receipt proves only the deterministic SceneSpec and constraint-validator eval denominator on its exact Git subject.",
    "Hosted test success does not prove a local runtime workflow, rendering backend, model/provider quality, user value or paid demand.",
    "Rights admission, merge, release and production promotion remain externally owned.",
]


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain an object")
    return value


def _base_scene() -> dict:
    return {
        "schema_version": "scene-spec@1",
        "scene_id": "scene:e02-canary",
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
                "subject_ids": ["node:a", "node:b"],
                "parameters": {"margin": 20},
            },
            {
                "constraint_id": "constraint:no-overlap",
                "kind": "NON_OVERLAP",
                "subject_ids": ["node:a", "node:b"],
                "parameters": {},
            },
            {
                "constraint_id": "constraint:anchor",
                "kind": "ANCHOR",
                "subject_ids": ["node:a"],
                "parameters": {"axis": "x", "target_x": 100},
            },
        ],
    }


def _transform(name: str) -> dict:
    payload = _base_scene()
    if name == "BASE":
        return payload
    if name == "MOVE_NODE_B_RIGHT":
        payload["nodes"][1]["x"] = 650
        return payload
    if name == "ANCHOR_NODE_A_Y":
        payload["constraints"][2]["parameters"] = {"axis": "y", "target_y": 100}
        return payload
    if name == "MISSING_ASSET":
        payload["nodes"][0]["asset_id"] = "asset:missing"
        return payload
    if name == "OUT_OF_BOUNDS":
        payload["nodes"][0]["x"] = 900
        return payload
    if name == "OVERLAP":
        payload["nodes"][1]["x"] = 150
        payload["nodes"][1]["y"] = 150
        return payload
    if name == "MOVE_NODE_A_ONE_PX_AFTER_PASS":
        payload["nodes"][0]["x"] = 101
        return payload
    raise AssertionError(f"unknown eval transform: {name}")


def _observe_case(case: dict) -> dict:
    case_id = case["case_id"]
    kind = case["kind"]
    transform = case["transform"]

    if kind == "POSITIVE":
        scene = SceneSpec.from_inputs(_transform(transform))
        receipt = validate_scene(scene)
        round_trip = SceneSpec.from_json(scene.canonical_json())
        state = (
            "PASS"
            if receipt.status == "PASS"
            and scene.canonical_json() == round_trip.canonical_json()
            and scene.digest() == round_trip.digest()
            else "UNEXPECTED"
        )
    elif kind == "NEGATIVE":
        scene = SceneSpec.from_inputs(_transform(transform))
        receipt = validate_scene(scene)
        state = (
            "FAIL_AS_EXPECTED"
            if receipt.status == "FAIL"
            and case["expected_violation"] in receipt.violations
            else "UNEXPECTED"
        )
    elif kind == "MUTATION":
        baseline = SceneSpec.from_inputs(_base_scene())
        old_receipt = validate_scene(baseline)
        mutated = SceneSpec.from_inputs(_transform(transform))
        state = (
            "STALE_AS_EXPECTED"
            if old_receipt.status == "PASS" and old_receipt.state_for(mutated) == "STALE"
            else "UNEXPECTED"
        )
    else:
        raise AssertionError(f"unknown eval kind: {kind}")

    return {"case_id": case_id, "kind": kind, "state": state}


def _observed_receipt(cases_packet: dict) -> dict:
    results = [_observe_case(case) for case in cases_packet["cases"]]
    counts = Counter(item["kind"] for item in results)
    return {
        "atom": "PREL-E02",
        "authority_ceiling": "DETERMINISTIC_EVAL_ONLY",
        "case_denominator": {
            "mutation": counts["MUTATION"],
            "negative": counts["NEGATIVE"],
            "positive": counts["POSITIVE"],
            "total": len(results),
        },
        "evidence_state": {
            "deterministic_eval": "PASS" if all(
                result["state"] != "UNEXPECTED" for result in results
            ) else "FAIL",
            "local_runtime": "NOT_EXERCISED",
            "paid": "ABSENT",
            "rights": "HUMAN_ADMIT_REQUIRED",
            "user": "ABSENT",
        },
        "non_claims": list(NON_CLAIMS),
        "parent_subjects": {
            "c02_head": "b0f59c7afad5b9acdbffbe9c87c1d86507237ea0",
            "k03_head": "dd185109378a34109313b3a6fa150af9de0b76cf",
        },
        "results": results,
        "schema_version": "structured-scene-eval-receipt@1",
        "summary": {
            "mutation_stale": f"{sum(item['state'] == 'STALE_AS_EXPECTED' for item in results)}/{counts['MUTATION']}",
            "negative_refused": f"{sum(item['state'] == 'FAIL_AS_EXPECTED' for item in results)}/{counts['NEGATIVE']}",
            "positive_pass": f"{sum(item['state'] == 'PASS' for item in results)}/{counts['POSITIVE']}",
        },
    }


class StructuredSceneE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = _load(CASES_PATH)
        self.receipt = _load(RECEIPT_PATH)

    def test_fixed_denominator_is_three_positive_three_negative_one_mutation(self) -> None:
        self.assertEqual(
            {"positive": 3, "negative": 3, "mutation": 1, "total": 7},
            self.cases["denominator"],
        )
        self.assertEqual(7, len(self.cases["cases"]))

    def test_all_three_positive_cases_round_trip_and_validate(self) -> None:
        positives = [item for item in self.cases["cases"] if item["kind"] == "POSITIVE"]
        self.assertEqual(3, len(positives))
        self.assertTrue(all(_observe_case(item)["state"] == "PASS" for item in positives))

    def test_all_planted_failures_remain_in_denominator(self) -> None:
        negatives = [item for item in self.cases["cases"] if item["kind"] == "NEGATIVE"]
        self.assertEqual(3, len(negatives))
        self.assertTrue(
            all(_observe_case(item)["state"] == "FAIL_AS_EXPECTED" for item in negatives)
        )

    def test_mutation_invalidates_old_receipt(self) -> None:
        mutation = next(item for item in self.cases["cases"] if item["kind"] == "MUTATION")
        self.assertEqual("STALE_AS_EXPECTED", _observe_case(mutation)["state"])

    def test_committed_receipt_matches_observed_outcomes_exactly(self) -> None:
        self.assertEqual(_observed_receipt(self.cases), self.receipt)

    def test_hosted_green_cannot_promote_local_runtime_or_market_lanes(self) -> None:
        evidence = self.receipt["evidence_state"]
        self.assertEqual("PASS", evidence["deterministic_eval"])
        self.assertEqual("NOT_EXERCISED", evidence["local_runtime"])
        self.assertEqual("ABSENT", evidence["user"])
        self.assertEqual("ABSENT", evidence["paid"])
        self.assertEqual("HUMAN_ADMIT_REQUIRED", evidence["rights"])

    def test_one_passing_edit_cannot_shrink_positive_denominator(self) -> None:
        modified = copy.deepcopy(self.cases)
        modified["cases"] = [
            item
            for item in modified["cases"]
            if item["kind"] != "POSITIVE" or item["case_id"] == "POS-001"
        ]
        observed = _observed_receipt(modified)
        self.assertNotEqual(self.receipt["case_denominator"], observed["case_denominator"])
        self.assertNotEqual(self.receipt, observed)


if __name__ == "__main__":
    unittest.main()
