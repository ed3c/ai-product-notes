from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.check_repository_contract import validate


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.copy = Path(self.tempdir.name) / "repo"
        shutil.copytree(ROOT, self.copy, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_current_repository_passes(self) -> None:
        self.assertEqual([], validate(ROOT))

    def test_private_boundary_removal_fails(self) -> None:
        path = self.copy / "README.md"
        text = path.read_text(encoding="utf-8").replace(
            "Private repository content is never an input to committed public artifacts",
            "Private content may be copied into public output",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("public/private boundary" in error for error in validate(self.copy)))

    def test_live_git_town_upgrade_without_receipt_fails(self) -> None:
        path = self.copy / "README.md"
        text = path.read_text(encoding="utf-8").replace(
            "| Live `git town sync` | `NOT_EXERCISED` |",
            "| Live `git town sync` | `PASS` |",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("NOT_EXERCISED" in error for error in validate(self.copy)))

    def test_managed_projection_mutation_fails(self) -> None:
        path = self.copy / "AGENTS.md"
        text = path.read_text(encoding="utf-8").replace(
            "Runtime identity is determined by observed capability",
            "Runtime identity is inferred from the model",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("projection drift" in error for error in validate(self.copy)))

    def test_unbounded_direct_main_policy_fails(self) -> None:
        path = self.copy / "docs/CONFIG.md"
        text = path.read_text(encoding="utf-8").replace(
            "Issue-first reviewable branches are mandatory",
            "All product changes write directly to main",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("delivery guard" in error for error in validate(self.copy)))

    def test_missing_state_owner_fails(self) -> None:
        path = self.copy / "README.md"
        text = path.read_text(encoding="utf-8").replace("LICENSE_GATED", "RIGHTS_CHECKED")
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("LICENSE_GATED" in error for error in validate(self.copy)))


if __name__ == "__main__":
    unittest.main()
