from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.replay_agent_contract import canonical_bytes, replay


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "examples/agent-contract-replay"


def load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AgentContractReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old = load("old-contract.json")
        self.breaking = load("new-contract-breaking.json")
        self.compatible = load("new-contract-compatible.json")
        self.trajectory = load("known-good-trajectory.json")

    def test_breaking_contract_detects_three_impacts(self) -> None:
        receipt = replay(self.old, self.breaking, self.trajectory)
        self.assertEqual("BREAKING", receipt["decision"])
        self.assertEqual(3, receipt["impact_count"])
        reasons = [impact["reason"] for impact in receipt["impacts"]]
        self.assertEqual(
            ["new_required_argument_missing", "enum_value_no_longer_admitted", "tool_removed"],
            reasons,
        )

    def test_compatible_contract_passes(self) -> None:
        receipt = replay(self.old, self.compatible, self.trajectory)
        self.assertEqual("PASS", receipt["decision"])
        self.assertEqual(0, receipt["impact_count"])
        self.assertEqual([], receipt["impacts"])

    def test_receipt_is_byte_stable(self) -> None:
        first = canonical_bytes(replay(self.old, self.breaking, self.trajectory))
        second = canonical_bytes(replay(self.old, self.breaking, self.trajectory))
        self.assertEqual(first, second)

    def test_receipt_binds_all_input_subjects(self) -> None:
        receipt = replay(self.old, self.breaking, self.trajectory)
        for key in ("old_contract_digest", "new_contract_digest", "trajectory_digest"):
            self.assertTrue(receipt[key].startswith("sha256:"))
            self.assertEqual(71, len(receipt[key]))


if __name__ == "__main__":
    unittest.main()
