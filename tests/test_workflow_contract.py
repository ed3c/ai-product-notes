from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/opportunity-contracts.yml"
EXACT_EXPRESSION = "${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha || github.sha }}"


def workflow_errors(text: str) -> list[str]:
    errors: list[str] = []
    required = (
        "  exact-head-contracts:\n",
        "name: Exact head contracts",
        "name: Checkout exact head subject",
        f"ref: {EXACT_EXPRESSION}",
        "EXPECTED_SUBJECT:",
        'test "$actual" = "$EXPECTED_SUBJECT"',
        "subject_kind=exact-head",
        "  merge-compatibility:\n",
        "name: Synthetic merge compatibility",
        "if: github.event_name == 'pull_request'",
        "name: Checkout synthetic merge subject",
        "fetch-depth: 2",
        "EXPECTED_BASE:",
        "EXPECTED_HEAD:",
        'test "$actual" != "$EXPECTED_HEAD"',
        'test "$base_parent" = "$EXPECTED_BASE"',
        'test "$head_parent" = "$EXPECTED_HEAD"',
        "subject_kind=synthetic-merge",
    )
    for marker in required:
        if marker not in text:
            errors.append(f"missing workflow subject guard: {marker}")

    if text.count(f"ref: {EXACT_EXPRESSION}") != 1:
        errors.append("exact-head checkout must have one explicit subject ref")
    if "  contracts:\n" in text:
        errors.append("ambiguous legacy contracts job must not remain")
    if "name: Checkout exact subject" in text:
        errors.append("misleading merge-only exact-subject label must not remain")
    if "ref: ${{ github.event.pull_request.merge_commit_sha }}" in text:
        errors.append("exact-head lane must not use the synthetic merge SHA")
    if 'test "$actual" = "$EXPECTED_HEAD"' in text:
        errors.append("merge lane must not claim that its subject equals the head")
    return errors


class WorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_current_workflow_separates_subjects(self) -> None:
        self.assertEqual([], workflow_errors(self.text))

    def test_missing_explicit_head_ref_fails(self) -> None:
        mutated = self.text.replace(f"ref: {EXACT_EXPRESSION}", "ref: ${{ github.sha }}")
        self.assertTrue(any("subject ref" in error or "subject guard" in error for error in workflow_errors(mutated)))

    def test_missing_head_assertion_fails(self) -> None:
        mutated = self.text.replace('test "$actual" = "$EXPECTED_SUBJECT"', "true")
        self.assertTrue(any("EXPECTED_SUBJECT" in error for error in workflow_errors(mutated)))

    def test_merge_lane_cannot_claim_head_identity(self) -> None:
        mutated = self.text.replace('test "$actual" != "$EXPECTED_HEAD"', 'test "$actual" = "$EXPECTED_HEAD"')
        errors = workflow_errors(mutated)
        self.assertTrue(any("EXPECTED_HEAD" in error or "equals the head" in error for error in errors))

    def test_legacy_misleading_job_fails(self) -> None:
        mutated = self.text.replace("  exact-head-contracts:\n", "  contracts:\n", 1)
        self.assertTrue(any("legacy contracts" in error or "exact-head-contracts" in error for error in workflow_errors(mutated)))

    def test_published_dual_subject_receipt_is_indexed(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ledger = (ROOT / "docs/git/STACKED_PRS.md").read_text(encoding="utf-8")
        combined = readme + "\n" + ledger
        for marker in (
            "https://github.com/ed3c/ai-product-notes/issues/10",
            "https://github.com/ed3c/ai-product-notes/pull/11",
            "31878162441",
            "5b646ec6fe70dd2047734636b8dfd517ee2998b2",
            "3bb417881393b5faad2a91056c49c77eefeb3cc8",
            "83243ba32729a75e953125370a8cb0b61cee197f",
            "HOSTED_VERIFIED",
        ):
            self.assertIn(marker, combined)
        self.assertIn("exact-head", combined)
        self.assertIn("synthetic-merge", combined)
        self.assertIn("live Git Town sync: NOT_EXERCISED", ledger)


if __name__ == "__main__":
    unittest.main()
