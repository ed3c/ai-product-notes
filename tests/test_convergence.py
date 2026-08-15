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
