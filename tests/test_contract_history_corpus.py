from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from replay_contract_history import (  # noqa: E402
    CorpusError,
    canonical_bytes,
    compile_manifest,
)

MANIFEST_PATH = (
    ROOT
    / "experiments/agent-contract-evolution-replay/corpus/manifest.json"
)
RECEIPT_PATH = (
    ROOT
    / "experiments/agent-contract-evolution-replay/corpus/receipts.json"
)


class ContractHistoryCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.compiled = compile_manifest(self.manifest)
        self.by_id = {
            receipt["case_id"]: receipt for receipt in self.compiled["receipts"]
        }

    def test_corpus_has_three_source_bound_adapters(self) -> None:
        self.assertEqual(3, self.compiled["summary"]["case_count"])
        self.assertEqual(
            {
                "protocol-envelope": 1,
                "registry-schema": 1,
                "sdk-api": 1,
            },
            self.compiled["summary"]["adapter_counts"],
        )
        for case in self.manifest["cases"]:
            for lane in ("old_contract", "new_contract", "consumer", "change"):
                source = case["sources"][lane]
                self.assertEqual(40, len(source["commit"]))
                self.assertEqual(40, len(source["blob_sha"]))
                self.assertTrue(source["repository"])
                self.assertTrue(source["path"])

    def test_registry_fixture_is_the_only_counted_historical_breakage(self) -> None:
        receipt = self.by_id["mcp-registry-package-json-casing-2025-09"]
        self.assertEqual("PASS", receipt["old_result"]["status"])
        self.assertEqual("FAIL", receipt["new_result"]["status"])
        self.assertEqual("HISTORICAL_BREAKAGE", receipt["decision"])
        self.assertTrue(receipt["counts_toward_real_breakage_gate"])
        self.assertEqual(
            [
                {"field": "registryType", "reason": "missing_required_field"},
                {"field": "registry_base_url", "reason": "unknown_field"},
                {"field": "registry_type", "reason": "unknown_field"},
            ],
            receipt["new_result"]["reasons"],
        )
        self.assertEqual(
            1, self.compiled["summary"]["real_historical_breakage_count"]
        )

    def test_sdk_positional_break_is_visible_but_not_counted(self) -> None:
        receipt = self.by_id[
            "mcp-typescript-sdk-get-task-result-2026-03"
        ]
        self.assertEqual("PASS", receipt["old_result"]["status"])
        self.assertEqual("FAIL", receipt["new_result"]["status"])
        self.assertEqual(
            "CONTRACT_BREAKAGE_NOT_COUNTED", receipt["decision"]
        )
        self.assertFalse(receipt["counts_toward_real_breakage_gate"])
        reason = receipt["new_result"]["reasons"][0]
        self.assertEqual("positional_argument_role_changed", reason["reason"])
        self.assertEqual("result_schema", reason["historical_role"])
        self.assertEqual("options", reason["new_parameter"])

    def test_protocol_envelope_gap_stays_unsupported(self) -> None:
        receipt = self.by_id[
            "mcp-2026-discover-server-info-envelope-relocation"
        ]
        self.assertEqual("UNSUPPORTED_ADAPTER", receipt["decision"])
        self.assertEqual("NOT_EXERCISED", receipt["old_result"]["status"])
        self.assertEqual("NOT_EXERCISED", receipt["new_result"]["status"])
        self.assertFalse(receipt["counts_toward_real_breakage_gate"])
        self.assertIn("negotiated protocol era", receipt["unsupported_reason"])

    def test_source_contract_and_consumer_digests_are_separate(self) -> None:
        for receipt in self.compiled["receipts"]:
            self.assertEqual(
                {"old_contract", "new_contract", "consumer", "change"},
                set(receipt["source_digests"]),
            )
            self.assertEqual(
                {"old_contract", "new_contract"},
                set(receipt["contract_digests"]),
            )
            for value in (
                list(receipt["source_digests"].values())
                + list(receipt["contract_digests"].values())
                + [receipt["consumer_digest"]]
            ):
                self.assertRegex(value, r"^sha256:[0-9a-f]{64}$")

    def test_committed_receipt_is_byte_reproducible(self) -> None:
        self.assertEqual(
            RECEIPT_PATH.read_bytes(), canonical_bytes(self.compiled)
        )
        self.assertEqual(
            canonical_bytes(compile_manifest(self.manifest)),
            canonical_bytes(compile_manifest(copy.deepcopy(self.manifest))),
        )

    def test_changelog_only_case_cannot_be_promoted(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        case = mutated["cases"][0]
        case["evidence_basis"] = "changelog_only"
        with self.assertRaisesRegex(CorpusError, "changelog prose"):
            compile_manifest(mutated)

    def test_upstream_self_consumer_cannot_be_counted(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        sdk_case = next(
            case
            for case in mutated["cases"]
            if case["adapter"] == "sdk-api"
        )
        sdk_case["counts_toward_real_breakage_gate"] = True
        with self.assertRaisesRegex(CorpusError, "cannot count"):
            compile_manifest(mutated)

    def test_roadmap_remains_validate_and_records_one_of_five(self) -> None:
        roadmap = (ROOT / "roadmap/ACTIVE.md").read_text(encoding="utf-8")
        self.assertIn("- **State:** `VALIDATE`", roadmap)
        self.assertIn("**Current real-history gate:** `1 / 5`", roadmap)
        self.assertIn("`UNSUPPORTED_ADAPTER`", roadmap)
        self.assertIn("No item is currently in `BUILD`", roadmap)
        self.assertNotIn("**State:** `BUILD`", roadmap)


if __name__ == "__main__":
    unittest.main()
