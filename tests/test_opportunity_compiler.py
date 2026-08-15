from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.compiler import (  # noqa: E402
    ValidationError,
    canonical_json,
    compile_opportunity,
    load_json,
    validate_packet,
)


SIGNAL = ROOT / "examples/signals/vendor-api-blast-radius.json"
ASSETS = ROOT / "data/assets/registry.json"
PORTFOLIO = ROOT / "config/public-portfolio.json"
PRIVATE = ROOT / "config/private-portfolio.example.json"


class OpportunityCompilerTests(unittest.TestCase):
    def load_inputs(self):
        return load_json(SIGNAL), load_json(ASSETS), load_json(PORTFOLIO)

    def test_fixture_compiles_to_validate(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        packet = compile_opportunity(signal, assets, portfolio)
        self.assertEqual("VALIDATE", packet["decision"])
        self.assertFalse(packet["gates"]["demand"]["direct_paid_demand"])
        self.assertIn("callsite-impact-join", packet["gates"]["uncovered_must_capabilities"])
        validate_packet(packet)

    def test_identical_input_is_byte_stable(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        first = canonical_json(compile_opportunity(signal, assets, portfolio))
        second = canonical_json(compile_opportunity(copy.deepcopy(signal), copy.deepcopy(assets), copy.deepcopy(portfolio)))
        self.assertEqual(first, second)

    def test_single_launch_cannot_become_build(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        signal["demand_evidence"] = signal["demand_evidence"][:1]
        for key in signal["metrics"]:
            signal["metrics"][key] = 10 if key != "competition_pressure" else 1
        packet = compile_opportunity(signal, assets, portfolio)
        self.assertNotEqual("BUILD", packet["decision"])
        self.assertFalse(packet["gates"]["demand"]["qualified"])

    def test_unknown_asset_does_not_count_and_blocks_required_match(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        signal["required_capabilities"] = [
            {
                "id": "unknown-only-capability",
                "importance": "must",
                "asset_types": ["code"],
                "accepted_asset_capabilities": ["unknown-only-capability"],
                "portfolio_capabilities": [],
                "description": "negative control",
            }
        ]
        candidate = copy.deepcopy(assets["assets"][0])
        candidate["id"] = "unknown-only-asset"
        candidate["capabilities"] = ["unknown-only-capability"]
        candidate["rights"]["code"]["status"] = "UNKNOWN"
        candidate["rights"]["code"]["license"] = ""
        candidate["rights"]["code"]["evidence_url"] = ""
        candidate["rights"]["code"]["commercial_use"] = False
        assets["assets"] = [candidate]
        packet = compile_opportunity(signal, assets, portfolio)
        self.assertEqual("BLOCKED", packet["decision"])
        self.assertEqual(0.0, packet["score"]["substitution_coverage_1_10"])
        self.assertIn("unknown-only-capability", packet["gates"]["hard_rights_gaps"])

    def test_private_overlay_forbidden_metadata_is_rejected(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        overlay = load_json(PRIVATE)
        overlay["capabilities"][0]["repository_url"] = "https://example.invalid/private"
        with self.assertRaises(ValidationError):
            compile_opportunity(signal, assets, portfolio, overlay)

    def test_private_overlay_is_sanitized_in_output(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        overlay = load_json(PRIVATE)
        packet = compile_opportunity(signal, assets, portfolio, overlay)
        rendered = canonical_json(packet)
        self.assertIn("private-envelope", rendered)
        self.assertNotIn("repository_url", rendered)
        self.assertNotIn("github.com/ed3c/", rendered.split('"private_portfolio_matches"', 1)[-1])

    def test_packet_digest_detects_mutation(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        packet = compile_opportunity(signal, assets, portfolio)
        packet["decision"] = "BUILD"
        with self.assertRaises(ValidationError):
            validate_packet(packet)

    def test_canonical_file_check_shape(self) -> None:
        signal, assets, portfolio = self.load_inputs()
        packet = compile_opportunity(signal, assets, portfolio)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "packet.json"
            path.write_text(canonical_json(packet), encoding="utf-8")
            self.assertEqual(canonical_json(load_json(path)), path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
