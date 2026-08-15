from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "opportunities/vendor-api-blast-radius/opportunity.json"


class ConvergenceTests(unittest.TestCase):
    def test_committed_opportunity_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "opportunity.json"
            subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/compile_opportunity.py"),
                    str(ROOT / "examples/signals/vendor-api-blast-radius.json"),
                    "--assets",
                    str(ROOT / "data/assets/registry.json"),
                    "--public-portfolio",
                    str(ROOT / "config/public-portfolio.json"),
                    "--output",
                    str(output),
                ],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(COMMITTED.read_bytes(), output.read_bytes())

    def test_active_roadmap_remains_validate(self) -> None:
        active = (ROOT / "roadmap/ACTIVE.md").read_text(encoding="utf-8")
        self.assertIn("**State:** `VALIDATE`", active)
        self.assertIn("No item is currently in `BUILD`", active)
        for unsupported in ("**State:** `BUILD`", "**State:** `PAID`", "**State:** `MARKET_VALIDATED`", "**State:** `DONE`"):
            self.assertNotIn(unsupported, active)

    def test_published_stack_trace_has_actual_refs(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ledger = (ROOT / "docs/git/STACKED_PRS.md").read_text(encoding="utf-8")
        combined = readme + "\n" + ledger
        self.assertNotIn("TBD", combined)
        for value in (
            "https://github.com/ed3c/ai-product-notes/pull/7",
            "https://github.com/ed3c/ai-product-notes/pull/8",
            "https://github.com/ed3c/ai-product-notes/pull/9",
            "8ae076852bce7f1abe3344b8db0d6b2df42c61eb",
            "849b50a011abdbe9940fa52d597a456902601e64",
            "6d88ed1fc26c74d8e5ad0d0e0fdef09e38560d81",
            "DRAFT_PUBLISHED",
        ):
            self.assertIn(value, combined)
        self.assertIn("base agent/4-market-control-plane", combined)
        self.assertIn("base agent/5-opportunity-compiler", combined)
        self.assertIn("live Git Town sync: NOT_EXERCISED", ledger)

    def test_public_convergence_surfaces_have_no_local_private_identifiers(self) -> None:
        paths = [
            ROOT / "opportunities/vendor-api-blast-radius/opportunity.json",
            ROOT / "opportunities/vendor-api-blast-radius/MVP.md",
            ROOT / "docs/PORTFOLIO_INTEGRATION.md",
            ROOT / "roadmap/ACTIVE.md",
        ]
        forbidden = ("/Users/", "/home/", "git@", "api_key", "access_token", "customer_data")
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text, f"{marker} leaked in {path}")


if __name__ == "__main__":
    unittest.main()
