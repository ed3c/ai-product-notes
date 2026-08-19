from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.problem_closure import (  # noqa: E402
    ClosureError,
    canonical_json,
    compile_outputs,
    digest_json,
    git_blob_sha1,
    validate_audit,
)


class ProblemClosureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = {
            "schema_version": "technical-systems-packet@1",
            "packet_id": "technical-systems:test",
            "packet_digest": "sha256:" + "0" * 64,
            "authority_ceiling": "TECHNICAL_DESIGN_ONLY",
            "decision": "VALIDATE",
            "source_subject": {"dossier_digest": "sha256:" + "b" * 64},
            "evidence_state": {
                "design": "PASS",
                "implementation": "ABSENT",
                "runtime": "ABSENT",
                "user": "ABSENT",
                "paid": "ABSENT",
                "legal": "ABSENT",
            },
        }
        self.packet["packet_digest"] = "sha256:" + digest_json(self.packet, drop_key="packet_digest")
        self.packet_bytes = canonical_json(self.packet).encode("utf-8")
        self.stage5 = {
            "schema_version": "technical-systems-binding@1",
            "repository": "ed3c/ai-product-notes",
            "pull_request": 55,
            "head_sha": "1" * 40,
            "path": "evals/technical-systems/test/technical-systems-packet.json",
            "blob_sha": git_blob_sha1(self.packet_bytes),
            "packet_digest": self.packet["packet_digest"].removeprefix("sha256:"),
            "parent_dossier_digest": "b" * 64,
            "hosted_run": 123,
            "authority_ceiling": "TECHNICAL_DESIGN_ONLY",
        }
        self.skills = {
            "schema_version": "prel-skill-binding@1",
            "repository": "ed3c/skills-shared",
            "commit": "2" * 40,
            "tree_sha": "3" * 40,
            "problem_matrix_schema": {"path": "matrix.json", "blob_sha": "4" * 40},
            "audit_schema": {"path": "audit.json", "blob_sha": "5" * 40},
            "shadow_module": {"path": "shadow.md", "blob_sha": "6" * 40},
            "authority_ceiling": "PORTABLE_METHOD_ONLY",
        }
        source_anchor = {
            "kind": "SOURCE_DOCUMENT",
            "locator": "source statement",
            "observed": "the exact source records the problem as a bounded hypothesis",
            "exact_subject": {"artifact": "source", "digest": "7" * 64},
        }
        mechanism_anchor = {
            "kind": "MECHANISM_OBSERVATION",
            "locator": "mechanism contract",
            "observed": "the technical design binds an observable oracle and falsifier",
            "exact_subject": {"artifact": "technical-design", "digest": "a" * 64},
        }
        empty = lambda level, state, note: {"level": level, "state": state, "anchors": [], "note": note}
        self.plan = {
            "schema_version": "problem-closure-plan@1",
            "subject_id": "test-product",
            "surface": "test surface",
            "captured_at": "2026-08-19T16:00:00Z",
            "problems": [
                {
                    "id": "PRB-001",
                    "statement": "A deterministic mechanism is useful enough to justify implementation.",
                    "declared_status": {
                        "statement": "The mechanism is bound but implementation remains absent.",
                        "claimed_level": "MECHANISM_BOUND",
                        "anchor": source_anchor,
                    },
                    "rungs": [
                        {"level": "SOURCE_ANCHORED", "state": "PASS", "anchors": [source_anchor], "note": "source bound"},
                        {"level": "MECHANISM_BOUND", "state": "PASS", "anchors": [mechanism_anchor], "note": "mechanism bound"},
                        empty("IMPLEMENTED", "NOT_IMPLEMENTED", "owned implementation is not materialized"),
                        empty("TECH_VERIFIED", "NOT_EXERCISED", "implementation suite cannot run before code exists"),
                        empty("LIVE_WORKFLOW_VERIFIED", "NOT_EXERCISED", "live runtime is not exercised"),
                        empty("USER_VALIDATED", "ABSENT", "no user report exists"),
                        empty("PAID_VALIDATED", "ABSENT", "no payment exists"),
                    ],
                    "finding_specs": [
                        {
                            "id": "FND-001",
                            "code": "OBLIGATION_SKIPPED_AT_FIRST_GREEN",
                            "statement": "Design CI cannot close the unimplemented runtime obligations.",
                            "anchors": [mechanism_anchor],
                            "proposed_repair": "Materialize owned implementation and execute its exact deterministic and runtime oracles.",
                        }
                    ],
                }
            ],
            "matrix_rows": [
                {
                    "id": "CLR-001",
                    "source_id": "PRB-001",
                    "requirement": "Materialize and execute the deterministic mechanism before claiming implementation closure.",
                    "lane": "DETERMINISTIC",
                    "oracle_id": "ORC-001",
                    "oracle_lane": "DETERMINISTIC",
                    "closure_state": "OPEN_WITH_ORACLE",
                    "evidence_state": "NOT_IMPLEMENTED",
                    "owner": "test-owner",
                }
            ],
            "evidence_ceiling": {
                "portable_procedure": "PASS",
                "deterministic_contract": "PASS",
                "product_market_fit": "ABSENT",
                "live_provider_execution": "NOT_EXERCISED",
                "production_readiness": "NOT_EXERCISED",
            },
            "issue_delta": [
                {
                    "id": "DLT-001",
                    "problem_id": "PRB-001",
                    "action": "PROPOSE_UPDATE",
                    "statement": "Keep implementation and runtime obligations explicitly open until exact receipts exist.",
                }
            ],
        }

    def compile(self):
        return compile_outputs(self.plan, self.skills, self.stage5, self.packet, self.packet_bytes)

    def test_valid_packet_stops_at_mechanism_bound(self) -> None:
        matrix, audit, delta = self.compile()
        self.assertEqual("MECHANISM_BOUND", audit["problems"][0]["highest_earned_level"])
        self.assertEqual("NOT_IMPLEMENTED", audit["problems"][0]["levels"][2]["state"])
        self.assertEqual("NO_WRITE_AUTHORITY", delta["write_authority"])
        self.assertEqual("OPEN_WITH_ORACLE", matrix["rows"][0]["closure_state"])

    def test_design_ci_cannot_promote_implementation(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["problems"][0]["rungs"][2] = {
            "level": "IMPLEMENTED",
            "state": "PASS",
            "anchors": [
                {
                    "kind": "CI_RUN",
                    "locator": "design CI",
                    "observed": "green design suite",
                    "exact_subject": {"artifact": "ci", "digest": "8" * 64},
                }
            ],
            "note": "invalid promotion",
        }
        with self.assertRaises(ClosureError):
            compile_outputs(plan, self.skills, self.stage5, self.packet, self.packet_bytes)

    def test_user_lane_requires_user_report(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["problems"][0]["rungs"][5] = {
            "level": "USER_VALIDATED",
            "state": "PASS",
            "anchors": [
                {
                    "kind": "CI_RUN",
                    "locator": "green CI",
                    "observed": "technical checks passed",
                    "exact_subject": {"artifact": "ci", "digest": "8" * 64},
                }
            ],
            "note": "invalid promotion",
        }
        with self.assertRaises(ClosureError):
            compile_outputs(plan, self.skills, self.stage5, self.packet, self.packet_bytes)

    def test_paid_lane_requires_paid_or_human_admission(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["problems"][0]["rungs"][6] = {
            "level": "PAID_VALIDATED",
            "state": "PASS",
            "anchors": [
                {
                    "kind": "USER_REPORT",
                    "locator": "interview",
                    "observed": "user said the problem matters",
                    "exact_subject": {"artifact": "user", "digest": "9" * 64},
                }
            ],
            "note": "invalid promotion",
        }
        with self.assertRaises(ClosureError):
            compile_outputs(plan, self.skills, self.stage5, self.packet, self.packet_bytes)

    def test_stage5_blob_drift_is_rejected(self) -> None:
        binding = copy.deepcopy(self.stage5)
        binding["blob_sha"] = "f" * 40
        with self.assertRaisesRegex(ClosureError, "Git blob mismatch"):
            compile_outputs(self.plan, self.skills, binding, self.packet, self.packet_bytes)

    def test_stage5_runtime_pass_is_rejected(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["evidence_state"]["runtime"] = "PASS"
        packet["packet_digest"] = "sha256:" + digest_json(packet, drop_key="packet_digest")
        packet_bytes = canonical_json(packet).encode("utf-8")
        binding = copy.deepcopy(self.stage5)
        binding["packet_digest"] = packet["packet_digest"].removeprefix("sha256:")
        binding["blob_sha"] = git_blob_sha1(packet_bytes)
        with self.assertRaisesRegex(ClosureError, "cannot promote runtime"):
            compile_outputs(self.plan, self.skills, binding, packet, packet_bytes)

    def test_audit_is_read_only_and_context_free(self) -> None:
        _, audit, _ = self.compile()
        validate_audit(audit)
        self.assertFalse(audit["reviewer"]["writes_implementation"])
        self.assertFalse(audit["reviewer"]["requires_prior_conversation"])
        self.assertFalse(audit["reviewer"]["requests_private_reasoning"])
        self.assertEqual("REVIEW_ONLY_NOT_MERGE_OR_RELEASE", audit["public_snapshot"]["completion_meaning"])

    def test_dissent_denominator_cannot_silently_shrink(self) -> None:
        _, audit, _ = self.compile()
        audit["review_denominator"]["findings_reported"] = 0
        with self.assertRaisesRegex(ClosureError, "denominator mismatch"):
            validate_audit(audit)

    def test_issue_delta_has_no_write_authority(self) -> None:
        _, audit, delta = self.compile()
        self.assertTrue(all(item["write_authority"] == "NO_WRITE_AUTHORITY" for item in audit["issue_delta"]))
        self.assertTrue(delta["human_admit_required"])

    def test_committed_canary_reproduces_from_exact_parent(self) -> None:
        canary = ROOT / "evals" / "problem-closure" / "modern-web-architecture"
        packet_path = ROOT / "evals" / "technical-systems" / "modern-web-architecture" / "technical-systems-packet.json"
        required = [
            canary / "closure-plan.json",
            canary / "skills-binding.json",
            canary / "stage5-binding.json",
            canary / "problem-closure-matrix.json",
            canary / "product-closure-audit.json",
            canary / "issue-delta.json",
            packet_path,
        ]
        if not all(path.is_file() for path in required):
            self.skipTest("repository canary is unavailable in isolated authoring fixture")
        packet_bytes = packet_path.read_bytes()
        matrix, audit, delta = compile_outputs(
            json.loads((canary / "closure-plan.json").read_text(encoding="utf-8")),
            json.loads((canary / "skills-binding.json").read_text(encoding="utf-8")),
            json.loads((canary / "stage5-binding.json").read_text(encoding="utf-8")),
            json.loads(packet_bytes.decode("utf-8")),
            packet_bytes,
        )
        self.assertEqual(canonical_json(matrix), (canary / "problem-closure-matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(canonical_json(audit), (canary / "product-closure-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(canonical_json(delta), (canary / "issue-delta.json").read_text(encoding="utf-8"))
        self.assertEqual("MECHANISM_BOUND", next(item for item in audit["problems"] if item["id"] == "PRB-003")["highest_earned_level"])
        self.assertTrue(all(item["highest_earned_level"] not in {"IMPLEMENTED", "TECH_VERIFIED", "LIVE_WORKFLOW_VERIFIED", "USER_VALIDATED", "PAID_VALIDATED"} for item in audit["problems"]))

    def test_outputs_are_byte_stable(self) -> None:
        first = self.compile()
        second = self.compile()
        self.assertEqual([canonical_json(item) for item in first], [canonical_json(item) for item in second])


if __name__ == "__main__":
    unittest.main()
