from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.reverse_engineering import (  # noqa: E402
    DossierError,
    canonical_json,
    compile_dossier,
    git_blob_sha1,
    load_json,
    validate_dossier,
)

CANARY = ROOT / "evals/reverse-engineering/modern-web-architecture"
SIGNAL_PATH = CANARY / "product-signal.input.json"
BINDING_PATH = CANARY / "external-binding.json"
HYPOTHESES_PATH = CANARY / "hypotheses.json"


class ReverseEngineeringDossierTests(unittest.TestCase):
    def load_inputs(self):
        return load_json(SIGNAL_PATH), load_json(BINDING_PATH), load_json(HYPOTHESES_PATH)

    def compile(self, signal=None, binding=None, hypotheses=None):
        if signal is None or binding is None or hypotheses is None:
            loaded = self.load_inputs()
            signal = loaded[0] if signal is None else signal
            binding = loaded[1] if binding is None else binding
            hypotheses = loaded[2] if hypotheses is None else hypotheses
        return compile_dossier(signal, binding, hypotheses, snapshot_bytes=SIGNAL_PATH.read_bytes())

    def test_canary_compiles_only_to_validate(self) -> None:
        dossier = self.compile()
        self.assertEqual("VALIDATE", dossier["decision"])
        self.assertEqual("VALIDATION_DESIGN_ONLY", dossier["authority_ceiling"])
        self.assertEqual("ABSENT", dossier["gates"]["user_evidence"])
        self.assertEqual("ABSENT", dossier["gates"]["paid_evidence"])

    def test_input_snapshot_matches_exact_external_git_blob(self) -> None:
        binding = load_json(BINDING_PATH)
        self.assertEqual(binding["blob_sha"], git_blob_sha1(SIGNAL_PATH.read_bytes()))

    def test_compilation_is_byte_stable(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        first = canonical_json(self.compile(signal, binding, hypotheses))
        second = canonical_json(self.compile(copy.deepcopy(signal), copy.deepcopy(binding), copy.deepcopy(hypotheses)))
        self.assertEqual(first, second)

    def test_mutated_product_signal_digest_is_rejected(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        signal["decision"] = "BUILD"
        with self.assertRaises(DossierError):
            self.compile(signal, binding, hypotheses)

    def test_snapshot_blob_drift_is_rejected(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        binding["blob_sha"] = "0" * 40
        with self.assertRaises(DossierError):
            self.compile(signal, binding, hypotheses)

    def test_user_hypothesis_cannot_be_promoted_to_fact(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        hypotheses["user_context"]["pain"]["epistemic_state"] = "FACT"
        with self.assertRaises(DossierError):
            self.compile(signal, binding, hypotheses)

    def test_named_product_mechanism_hypothesis_cannot_become_source_statement(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        hypotheses["mechanisms"][1]["epistemic_state"] = "SOURCE_STATEMENT"
        with self.assertRaises(DossierError):
            self.compile(signal, binding, hypotheses)

    def test_rights_cannot_pass_without_legal_evidence(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        hypotheses["capabilities"][2]["rights_state"] = "PASS"
        with self.assertRaises(DossierError):
            self.compile(signal, binding, hypotheses)

    def test_stop_loss_is_required(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        hypotheses["mvp"]["stop_loss"] = []
        with self.assertRaises(DossierError):
            self.compile(signal, binding, hypotheses)

    def test_unknowns_and_contradictions_cannot_be_silenced(self) -> None:
        signal, _, _ = self.load_inputs()
        dossier = self.compile()
        dossier["lineage"]["unknown_claims"] = []
        dossier["dossier_digest"] = "sha256:" + "0" * 64
        with self.assertRaises(DossierError):
            validate_dossier(dossier, product_signal=signal)

    def test_dossier_digest_detects_mutation(self) -> None:
        signal, _, _ = self.load_inputs()
        dossier = self.compile()
        dossier["decision"] = "REJECT"
        with self.assertRaises(DossierError):
            validate_dossier(dossier, product_signal=signal)

    def test_private_or_secret_shaped_fields_are_rejected(self) -> None:
        signal, binding, hypotheses = self.load_inputs()
        hypotheses["target"]["private_repository_url"] = "https://example.invalid/private"
        with self.assertRaises(DossierError):
            self.compile(signal, binding, hypotheses)

    def test_canonical_output_check_shape(self) -> None:
        dossier = self.compile()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "dossier.json"
            path.write_text(canonical_json(dossier), encoding="utf-8")
            self.assertEqual(canonical_json(json.loads(path.read_text(encoding="utf-8"))), path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
