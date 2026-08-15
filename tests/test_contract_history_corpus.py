from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from replay_contract_history import CorpusError, canonical_bytes, compile_manifest  # noqa: E402

MANIFEST = ROOT / "experiments/agent-contract-evolution-replay/corpus/manifest.json"
RECEIPT = ROOT / "experiments/agent-contract-evolution-replay/corpus/receipts.json"


class ContractHistoryCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.compiled = compile_manifest(self.manifest)
        self.receipts = {r["case_id"]: r for r in self.compiled["receipts"]}

    def sdk(self, manifest: dict | None = None) -> dict:
        source = manifest or self.manifest
        return next(c for c in source["cases"] if c["adapter"] == "sdk-api")

    def test_summary_and_source_bindings(self) -> None:
        self.assertEqual("contract-history-corpus.v2", self.manifest["schema_version"])
        self.assertEqual(2, self.compiled["summary"]["real_historical_breakage_count"])
        self.assertEqual(
            {"HISTORICAL_BREAKAGE": 2, "UNSUPPORTED_ADAPTER": 1},
            self.compiled["summary"]["decision_counts"],
        )
        self.assertEqual(
            {"protocol-envelope": 1, "registry-schema": 1, "sdk-api": 1},
            self.compiled["summary"]["adapter_counts"],
        )
        for case in self.manifest["cases"]:
            for lane in ("old_contract", "new_contract", "consumer", "change"):
                source = case["sources"][lane]
                self.assertEqual(40, len(source["commit"]))
                self.assertEqual(40, len(source["blob_sha"]))

    def test_registry_breakage_remains_counted(self) -> None:
        r = self.receipts["mcp-registry-package-json-casing-2025-09"]
        self.assertEqual(("PASS", "FAIL"), (r["old_result"]["status"], r["new_result"]["status"]))
        self.assertEqual("HISTORICAL_BREAKAGE", r["decision"])
        self.assertTrue(r["counts_toward_real_breakage_gate"])

    def test_sdk_downstream_migration_is_counted_with_exact_reasons(self) -> None:
        r = self.receipts["mcp-typescript-sdk-get-task-result-1x-to-2x"]
        self.assertEqual(("PASS", "FAIL"), (r["old_result"]["status"], r["new_result"]["status"]))
        self.assertEqual("HISTORICAL_BREAKAGE", r["decision"])
        self.assertTrue(r["counts_toward_real_breakage_gate"])
        self.assertEqual(
            ["extra_positional_argument", "positional_argument_role_changed"],
            [reason["reason"] for reason in r["new_result"]["reasons"]],
        )
        self.assertEqual("request_options", r["new_result"]["reasons"][0]["historical_role"])
        self.assertEqual("omitted_optional_placeholder", r["new_result"]["reasons"][1]["historical_role"])

    def test_sdk_receipt_binds_lock_packages_and_exact_ci(self) -> None:
        case = self.sdk()
        r = self.receipts[case["case_id"]]
        summary = r["validation_summary"]
        self.assertEqual(31865385554, summary["old_ci_run_id"])
        self.assertEqual("ff88581e741c79cfbb5f6ddb827b90f39447be71", summary["old_ci_head_sha"])
        self.assertEqual("@modelcontextprotocol/sdk", summary["locked_package"])
        self.assertEqual("1.29.0", summary["locked_version"])
        self.assertEqual(
            {"Test & Build": "success", "TypeScript Typecheck": "success", "Typecheck & Build": "success"},
            summary["required_jobs"],
        )
        self.assertEqual("@modelcontextprotocol/sdk", case["old_contract"]["package_identity"])
        self.assertEqual("@modelcontextprotocol/client", case["new_contract"]["package_identity"])
        self.assertEqual("sdk-major-package-migration", case["old_contract"]["migration_kind"])
        self.assertRegex(r["validation_digest"], r"^sha256:[0-9a-f]{64}$")

    def test_protocol_envelope_stays_unsupported(self) -> None:
        r = self.receipts["mcp-2026-discover-server-info-envelope-relocation"]
        self.assertEqual("UNSUPPORTED_ADAPTER", r["decision"])
        self.assertEqual(("NOT_EXERCISED", "NOT_EXERCISED"), (r["old_result"]["status"], r["new_result"]["status"]))
        self.assertFalse(r["counts_toward_real_breakage_gate"])

    def test_receipt_is_byte_reproducible_and_digests_are_separate(self) -> None:
        self.assertEqual(RECEIPT.read_bytes(), canonical_bytes(self.compiled))
        self.assertEqual(canonical_bytes(self.compiled), canonical_bytes(compile_manifest(copy.deepcopy(self.manifest))))
        for r in self.compiled["receipts"]:
            self.assertEqual({"old_contract", "new_contract", "consumer", "change"}, set(r["source_digests"]))
            self.assertEqual({"old_contract", "new_contract"}, set(r["contract_digests"]))

    def test_changelog_only_cannot_count(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        mutated["cases"][0]["evidence_basis"] = "changelog_only"
        with self.assertRaisesRegex(CorpusError, "changelog prose"):
            compile_manifest(mutated)

    def test_sdk_provenance_failures_block_counting(self) -> None:
        mutations = {
            "dependency": lambda c: c["validation"].pop("dependency_lock"),
            "head": lambda c: c["validation"]["old_ci"].update(head_sha="0" * 40),
            "job": lambda c: c["validation"]["old_ci"]["jobs"].update({"TypeScript Typecheck": "skipped"}),
            "version": lambda c: c["validation"]["dependency_lock"].update(version="1.28.0"),
            "package": lambda c: (
                c["new_contract"].update(package_identity=c["old_contract"]["package_identity"]),
                c["validation"]["new_package_manifest"].update(package=c["old_contract"]["package_identity"]),
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                manifest = copy.deepcopy(self.manifest)
                mutate(self.sdk(manifest))
                with self.assertRaises(CorpusError):
                    compile_manifest(manifest)

    def test_two_argument_new_consumer_is_not_reported_as_historical_breakage(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        case = self.sdk(manifest)
        case["counts_toward_real_breakage_gate"] = False
        case["consumer"]["arguments"] = [
            {"role": "task_id", "value": "capturedTaskId"},
            {"role": "request_options", "value": "requestOptions"},
        ]
        r = next(x for x in compile_manifest(manifest)["receipts"] if x["adapter"] == "sdk-api")
        self.assertEqual("PASS", r["new_result"]["status"])
        self.assertEqual("INCONCLUSIVE", r["decision"])
        self.assertFalse(r["counts_toward_real_breakage_gate"])

    def test_roadmap_remains_validate_at_two_of_five(self) -> None:
        roadmap = (ROOT / "roadmap/ACTIVE.md").read_text(encoding="utf-8")
        self.assertIn("- **State:** `VALIDATE`", roadmap)
        self.assertIn("**Current real-history gate:** `2 / 5`", roadmap)
        self.assertIn("`UNSUPPORTED_ADAPTER`", roadmap)
        self.assertIn("No item is currently in `BUILD`", roadmap)
        self.assertNotIn("**State:** `BUILD`", roadmap)


if __name__ == "__main__":
    unittest.main()
