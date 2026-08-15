from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compile_history_evidence_ledger import LedgerError, compile_ledger  # noqa: E402
from replay_publisher_schema_revision import (  # noqa: E402
    PublisherHistoryError,
    canonical_bytes,
    compile_case,
)

CASE = ROOT / "experiments/agent-contract-evolution-replay/corpus/extensions/mcp-registry-publisher-schema-revision-2025-09/case.json"
RECEIPT = ROOT / "experiments/agent-contract-evolution-replay/corpus/extensions/mcp-registry-publisher-schema-revision-2025-09/receipt.json"
LEDGER_INPUT = ROOT / "experiments/agent-contract-evolution-replay/corpus/ledger-input.json"
LEDGER = ROOT / "experiments/agent-contract-evolution-replay/corpus/ledger.json"
BASE_RECEIPT = ROOT / "experiments/agent-contract-evolution-replay/corpus/receipts.json"


class PublisherSchemaRevisionHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = json.loads(CASE.read_text(encoding="utf-8"))
        self.compiled = compile_case(self.case)
        self.spec = json.loads(LEDGER_INPUT.read_text(encoding="utf-8"))
        self.ledger = compile_ledger(self.spec)

    def test_exact_old_pass_new_fail_reason(self) -> None:
        self.assertEqual("PASS", self.compiled["old_result"]["status"])
        self.assertEqual("FAIL", self.compiled["new_result"]["status"])
        self.assertEqual(
            ["schema_revision_not_admitted"],
            [reason["reason"] for reason in self.compiled["new_result"]["reasons"]],
        )
        self.assertEqual("HISTORICAL_BREAKAGE", self.compiled["decision"])
        self.assertTrue(self.compiled["counts_toward_real_breakage_gate"])

    def test_empty_and_current_revision_controls_pass(self) -> None:
        self.assertEqual(
            {"new_current_schema", "new_empty_schema", "old_current_schema", "old_empty_schema"},
            set(self.compiled["controls"]),
        )
        for result in self.compiled["controls"].values():
            self.assertEqual("PASS", result["status"])
            self.assertEqual([], result["reasons"])

    def test_exact_source_and_ci_bindings(self) -> None:
        sources = self.case["sources"]
        self.assertEqual("a72671c43f58120a22682b32e8e0e598c1759e3d", sources["old_publisher"]["blob_sha"])
        self.assertEqual("0f6b959e4d623f00bb0c926e9d8dd61b6eef88f4", sources["new_publisher"]["blob_sha"])
        self.assertEqual("0dd3f62dfb4643377973fee093528c5fba7b029f", sources["old_test"]["blob_sha"])
        self.assertEqual("67a7022791477b8a5ac98e797edb10140d3b7fb4", sources["new_test"]["blob_sha"])
        self.assertEqual("8766b2a49d545eb6d11b5344ded1f1008462f680", sources["old_schema"]["blob_sha"])
        self.assertEqual("bcf5ba5af6a33ac2de5344d24eb3db48860e4e73", sources["new_schema"]["blob_sha"])
        summary = self.compiled["validation_summary"]
        self.assertEqual(18078458326, summary["old_ci"]["run_id"])
        self.assertEqual(18109863200, summary["new_ci"]["run_id"])
        for lane in ("old_ci", "new_ci"):
            self.assertEqual(
                {"Build, Lint, and Validate": "success", "Tests": "success"},
                summary[lane]["jobs"],
            )

    def test_status_removal_is_explicitly_not_counted(self) -> None:
        finding = self.compiled["negative_findings"][0]
        self.assertEqual("publisher-status-removal", finding["finding_id"])
        self.assertEqual("NOT_COUNTED", finding["disposition"])
        self.assertEqual(
            "go_json_unmarshal_does_not_prove_unknown_field_rejection",
            finding["reason"],
        )
        self.assertEqual(
            "schema_revision_not_admitted",
            self.compiled["adjudication"]["counted_reason"],
        )

    def test_receipt_and_ledger_are_byte_reproducible(self) -> None:
        self.assertEqual(RECEIPT.read_bytes(), canonical_bytes(self.compiled))
        self.assertEqual(LEDGER.read_bytes(), canonical_bytes(self.ledger))
        self.assertEqual(
            canonical_bytes(self.compiled),
            canonical_bytes(compile_case(copy.deepcopy(self.case))),
        )
        self.assertEqual(
            canonical_bytes(self.ledger),
            canonical_bytes(compile_ledger(copy.deepcopy(self.spec))),
        )

    def test_changelog_and_ci_provenance_fail_closed(self) -> None:
        mutations = {
            "changelog": lambda c: c.update(evidence_basis="changelog_only"),
            "old_head": lambda c: c["validation"]["old_ci"].update(head_sha="0" * 40),
            "new_head": lambda c: c["validation"]["new_ci"].update(head_sha="0" * 40),
            "old_job": lambda c: c["validation"]["old_ci"]["jobs"].update({"Tests": "skipped"}),
            "new_job": lambda c: c["validation"]["new_ci"]["jobs"].update({"Build, Lint, and Validate": "failure"}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                case = copy.deepcopy(self.case)
                mutate(case)
                with self.assertRaises(PublisherHistoryError):
                    compile_case(case)

    def test_status_removal_cannot_be_substituted_as_counted_reason(self) -> None:
        case = copy.deepcopy(self.case)
        case["adjudication"]["counted_reason"] = "status_field_removed"
        with self.assertRaisesRegex(PublisherHistoryError, "counted reason"):
            compile_case(case)

        case = copy.deepcopy(self.case)
        case["negative_findings"][0]["disposition"] = "COUNTED"
        with self.assertRaisesRegex(PublisherHistoryError, "NOT_COUNTED"):
            compile_case(case)

    def test_append_only_ledger_advances_three_of_five(self) -> None:
        self.assertEqual("VALIDATE", self.ledger["market_state"])
        self.assertEqual(
            {
                "target": 5,
                "current": 3,
                "remaining": 2,
                "build_admitted": False,
            },
            self.ledger["gate"],
        )
        self.assertEqual(2, self.ledger["base_corpus"]["real_historical_breakage_count"])
        self.assertEqual(1, len(self.ledger["extensions"]))
        self.assertEqual(
            "sha256:4ca13352eb596c5ce7ba2bd91132f6ce0a3b976aac03489a926cc0bb1ea4326e",
            self.ledger["base_corpus"]["receipt_digest"],
        )

    def test_duplicate_case_and_change_event_fail(self) -> None:
        duplicate_case = copy.deepcopy(self.spec)
        second = copy.deepcopy(duplicate_case["extensions"][0])
        second["change_event_id"] = "modelcontextprotocol/registry#9999"
        duplicate_case["extensions"].append(second)
        with self.assertRaisesRegex(LedgerError, "duplicate case_id"):
            compile_ledger(duplicate_case)

        duplicate_event = copy.deepcopy(self.spec)
        second = copy.deepcopy(duplicate_event["extensions"][0])
        second["case_id"] = "second-case-same-upstream-event"
        duplicate_event["extensions"].append(second)
        with self.assertRaisesRegex(LedgerError, "duplicate change_event_id"):
            compile_ledger(duplicate_event)

    def test_expected_receipt_and_source_digest_drift_fail(self) -> None:
        bad_receipt = copy.deepcopy(self.spec)
        bad_receipt["extensions"][0]["expected_receipt_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(LedgerError, "expected receipt"):
            compile_ledger(bad_receipt)

        bad_source = copy.deepcopy(self.spec)
        bad_source["extensions"][0]["expected_source_digests"]["old_publisher"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(LedgerError, "source receipt"):
            compile_ledger(bad_source)

    def test_base_corpus_remains_immutable_two_of_five(self) -> None:
        base = json.loads(BASE_RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual("contract-history-corpus-receipt.v2", base["schema_version"])
        self.assertEqual(
            "sha256:4ca13352eb596c5ce7ba2bd91132f6ce0a3b976aac03489a926cc0bb1ea4326e",
            base["receipt_digest"],
        )
        self.assertEqual(2, base["summary"]["real_historical_breakage_count"])

    def test_roadmap_distinguishes_base_and_aggregate_gates(self) -> None:
        roadmap = (ROOT / "roadmap/ACTIVE.md").read_text(encoding="utf-8")
        self.assertIn("**Immutable base corpus:** `2 / 5`", roadmap)
        self.assertIn("**Aggregate evidence ledger:** `3 / 5`", roadmap)
        self.assertIn("**Remaining historical cases:** `2`", roadmap)
        self.assertIn("- **State:** `VALIDATE`", roadmap)
        self.assertIn("No item is currently in `BUILD`", roadmap)
        self.assertNotIn("**State:** `BUILD`", roadmap)


if __name__ == "__main__":
    unittest.main()
