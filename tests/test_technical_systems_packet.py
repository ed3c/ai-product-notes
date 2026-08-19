from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.technical_systems import (  # noqa: E402
    TechnicalSystemsError,
    canonical_json,
    compile_from_paths,
    compile_packet,
    load_json,
    validate_dossier,
    validate_packet,
    validate_plan,
)

CANARY = ROOT / "evals" / "technical-systems" / "modern-web-architecture"
DOSSIER = ROOT / "evals" / "reverse-engineering" / "modern-web-architecture" / "dossier.json"
BINDING = CANARY / "stage4-binding.json"
PLAN = CANARY / "technical-systems-plan.json"
PACKET = CANARY / "technical-systems-packet.json"


class TechnicalSystemsPacketTests(unittest.TestCase):
    def load_inputs(self):
        return load_json(DOSSIER), load_json(BINDING), load_json(PLAN)

    def test_canary_reproduces_byte_for_byte(self) -> None:
        packet = compile_from_paths(DOSSIER, BINDING, PLAN)
        self.assertEqual(canonical_json(packet), PACKET.read_text(encoding="utf-8"))
        validate_packet(packet)

    def test_dossier_digest_drift_is_rejected(self) -> None:
        dossier, _, plan = self.load_inputs()
        mutated = copy.deepcopy(dossier)
        mutated["mvp"]["budget_usd"] += 1
        with self.assertRaises(TechnicalSystemsError):
            validate_dossier(mutated)
        rebound = copy.deepcopy(dossier)
        rebound["dossier_digest"] = "sha256:" + "1" * 64
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, rebound)

    def test_dependency_cycle_is_rejected(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["capabilities"][0]["dependencies"] = ["constraint-validation"]
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_unknown_dependency_is_rejected(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["capabilities"][1]["dependencies"] = ["missing-capability"]
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_pass_right_without_evidence_is_rejected(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["substitutions"][0]["rights"]["code"]["status"] = "PASS"
        plan["substitutions"][0]["rights"]["code"]["evidence"] = []
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_selected_substitution_requires_pass_code_right(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["substitutions"][0]["status"] = "SELECTED"
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_runtime_eval_cannot_claim_pass(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        runtime_eval = next(item for item in plan["evals"] if item["kind"] == "RUNTIME")
        runtime_eval["evidence_state"] = "PASS"
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_mvp_cannot_omit_must_capability(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["mvp_slice"]["capability_ids"] = ["structured-scene-ir"]
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_mvp_cannot_include_probabilistic_backend(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["mvp_slice"]["capability_ids"].append("candidate-rendering-stack")
        plan["mvp_slice"]["excluded_capabilities"] = []
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_budget_and_time_cannot_exceed_dossier(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["mvp_slice"]["maximum_days"] = 15
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)
        plan = copy.deepcopy(self.load_inputs()[2])
        plan["mvp_slice"]["budget_usd"] = 501
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_packet_cannot_claim_implementation(self) -> None:
        dossier, binding, plan = self.load_inputs()
        packet = compile_packet(dossier, binding, plan)
        packet["evidence_state"]["implementation"] = "PASS"
        packet["packet_digest"] = "sha256:" + "0" * 64
        with self.assertRaises(TechnicalSystemsError):
            validate_packet(packet)

    def test_unknowns_and_contradictions_cannot_disappear(self) -> None:
        dossier, binding, plan = self.load_inputs()
        packet = compile_packet(dossier, binding, plan)
        packet["upstream_unknown_claims"] = []
        with self.assertRaises(TechnicalSystemsError):
            validate_packet(packet)
        packet = compile_packet(dossier, binding, plan)
        packet["upstream_unresolved_contradictions"] = []
        with self.assertRaises(TechnicalSystemsError):
            validate_packet(packet)

    def test_private_export_shape_is_rejected(self) -> None:
        dossier, _, plan = self.load_inputs()
        plan = copy.deepcopy(plan)
        plan["capabilities"][0]["private_repository_url"] = "https://example.invalid/private"
        with self.assertRaises(TechnicalSystemsError):
            validate_plan(plan, dossier)

    def test_identical_inputs_are_deterministic(self) -> None:
        dossier, binding, plan = self.load_inputs()
        first = compile_packet(dossier, binding, plan)
        second = compile_packet(copy.deepcopy(dossier), copy.deepcopy(binding), copy.deepcopy(plan))
        self.assertEqual(canonical_json(first), canonical_json(second))


if __name__ == "__main__":
    unittest.main()
