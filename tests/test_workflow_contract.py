from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
WORKFLOW = WORKFLOW_DIR / "opportunity-contracts.yml"
EXACT_EXPRESSION = "${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha || github.sha }}"
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"


def workflow_security_errors(text: str) -> list[str]:
    errors: list[str] = []
    for subject in re.findall(r"uses:\s*actions/checkout@([^\s]+)", text):
        if subject != CHECKOUT_SHA:
            errors.append("checkout must use the admitted immutable v7.0.1 SHA")
    forbidden_patterns = (
        (
            r"(?m)^\s*contents:\s*['\"]?write['\"]?\s*$",
            "workflow must not request write permission",
        ),
        (r"(?m)^\s*issues:\s*(?:#.*)?$", "workflow must not run on Issue events"),
        (
            r"(?m)\bgit\s+push\b[^\n]*\bmain\b",
            "workflow must not push directly to main",
        ),
    )
    for pattern, reason in forbidden_patterns:
        if re.search(pattern, text):
            errors.append(reason)
    return errors


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
    checkout_subjects = re.findall(r"uses:\s*actions/checkout@([^\s]+)", text)
    if checkout_subjects != [CHECKOUT_SHA, CHECKOUT_SHA]:
        errors.append("both checkout steps must use the admitted immutable v7.0.1 SHA")
    if "permissions:\n  contents: read\n" not in text:
        errors.append("workflow must retain read-only repository permission")

    errors.extend(workflow_security_errors(text))
    return errors


def repository_workflow_errors(workflows: dict[str, str]) -> list[str]:
    admitted = {"opportunity-contracts.yml"}
    observed = set(workflows)
    errors = [
        f"unexpected workflow must be separately admitted: {name}"
        for name in sorted(observed - admitted)
    ]
    for name in sorted(admitted - observed):
        errors.append(f"admitted workflow is missing: {name}")
    if "opportunity-contracts.yml" in workflows:
        errors.extend(workflow_errors(workflows["opportunity-contracts.yml"]))
    for name in sorted(observed - admitted):
        errors.extend(workflow_security_errors(workflows[name]))
    return errors


class WorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")
        paths = sorted(set(WORKFLOW_DIR.glob("*.yml")) | set(WORKFLOW_DIR.glob("*.yaml")))
        self.workflows = {
            path.name: path.read_text(encoding="utf-8") for path in paths
        }

    def test_current_workflow_separates_subjects(self) -> None:
        self.assertEqual([], repository_workflow_errors(self.workflows))

    def test_floating_checkout_pin_fails(self) -> None:
        mutated = self.text.replace(f"actions/checkout@{CHECKOUT_SHA}", "actions/checkout@v7")
        self.assertTrue(any("immutable" in error for error in workflow_errors(mutated)))

    def test_bootstrap_workflow_reappearance_fails(self) -> None:
        workflows = dict(self.workflows)
        workflows["bootstrap-rebuild.yml"] = "on:\n  issues:\n    types: [opened]\n"
        errors = repository_workflow_errors(workflows)
        self.assertTrue(any("unexpected workflow" in error for error in errors))
        self.assertTrue(any("Issue events" in error for error in errors))

    def test_renamed_dangerous_workflow_fails(self) -> None:
        workflows = {
            "opportunity-contracts.yml": self.text,
            "renamed-maintenance.yml": (
                "permissions:\n  contents: write\n"
                "on:\n  issues:\n    types: [opened]\n"
                "run: git push origin HEAD:main\n"
            ),
        }
        errors = repository_workflow_errors(workflows)
        self.assertTrue(any("unexpected workflow" in error for error in errors))

    def test_write_permission_or_direct_main_push_fails(self) -> None:
        mutated = self.text.replace("contents: read", "contents: write")
        mutated += "\nrun: git push origin HEAD:main\n"
        errors = workflow_errors(mutated)
        self.assertTrue(any("write permission" in error for error in errors))
        self.assertTrue(any("directly to main" in error for error in errors))

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
