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

from ai_product_notes.execution_planner import (  # noqa: E402
    ExecutionPlanError,
    canonical_json,
    compile_from_paths,
    compile_outputs,
    digest_json,
    git_blob_sha1,
    validate_plan,
    validate_stage6_binding,
)


class ExecutionPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = {
            "schema": "prel/product-closure-audit/v1",
            "problems": [{"highest_earned_level": "MECHANISM_BOUND"}],
        }
        self.delta = {"write_authority": "NO_WRITE_AUTHORITY"}
        self.shadow = {"authority_ceiling": "FINDINGS_ONLY"}
        self.matrix = {"schema": "prel/problem-closure-matrix/v1"}
        self.bytes = {
            "matrix": canonical_json(self.matrix).encode(),
            "audit": canonical_json(self.audit).encode(),
            "delta": canonical_json(self.delta).encode(),
            "shadow": canonical_json(self.shadow).encode(),
        }
        self.stage6 = {
            "schema_version": "stage6-closure-binding@1",
            "repository": "ed3c/ai-product-notes",
            "pull_request": 57,
            "head_sha": "1" * 40,
            "matrix": {"path": "x/problem-closure-matrix.json", "blob_sha": git_blob_sha1(self.bytes["matrix"])},
            "audit": {"path": "x/product-closure-audit.json", "blob_sha": git_blob_sha1(self.bytes["audit"]), "canonical_digest": digest_json(self.audit)},
            "delta": {"path": "x/issue-delta.json", "blob_sha": git_blob_sha1(self.bytes["delta"])},
            "shadow": {"path": "x/shadow-review.json", "blob_sha": git_blob_sha1(self.bytes["shadow"])},
            "hosted_run": 123,
            "authority_ceiling": "FINDINGS_ONLY",
        }
        self.skills = {
            "schema_version": "stage7-skills-binding@1",
            "repository": "ed3c/skills-shared",
            "commit": "2" * 40,
            "tree_sha": "3" * 40,
            "prompt_packet_schema": {"path": "prompt.json", "blob_sha": "4" * 40},
            "prompt_catalogue": {"path": "catalogue.md", "blob_sha": "5" * 40},
            "molecular_stack_schema": {"path": "stack.json", "blob_sha": "6" * 40},
            "authority_ceiling": "PORTABLE_METHOD_ONLY",
        }
        subject_digest = digest_json({
            "stage6": self.stage6["head_sha"],
            "audit": self.stage6["audit"]["canonical_digest"],
            "skills": self.skills["commit"],
        })
        root_atom = {
            "id": "PREL-C02", "atom": "C", "purpose": "root contract", "stack_class": "root", "lane": "CLOUD",
            "branch": "prel/c02", "base_branch": "prel/stage7", "parents": [], "owns_paths": ["src/a.py"],
            "consumes_paths": ["evals/plan.json"], "start_dependencies": ["PLAN_READABLE"],
            "completion_dependencies": ["C_RECEIPT_PASS"], "oracle": "canonical bytes are stable",
            "negative_controls": ["reject unknown fields"], "rollback": "remove root contract changes",
            "budget": {"maximum_hours": 1, "maximum_files": 1},
        }
        child = {
            "id": "PREL-K03", "atom": "K", "purpose": "child core", "stack_class": "child", "lane": "CLOUD",
            "branch": "prel/k03", "base_branch": "prel/c02", "parents": ["PREL-C02"], "owns_paths": ["src/b.py"],
            "consumes_paths": ["src/a.py"], "start_dependencies": ["C_BYTES_READABLE"],
            "completion_dependencies": ["C_RECEIPT_PASS", "K_RECEIPT_PASS"], "oracle": "deterministic rule passes",
            "negative_controls": ["reject drift"], "rollback": "remove child core changes",
            "budget": {"maximum_hours": 1, "maximum_files": 1},
        }
        convergence = {
            "id": "PREL-D02", "atom": "D", "purpose": "docs convergence", "stack_class": "convergence", "lane": "CLOUD",
            "branch": "prel/d02", "base_branch": "prel/k03", "parents": ["PREL-C02", "PREL-K03"],
            "owns_paths": ["docs/summary.md"], "consumes_paths": ["src/a.py", "src/b.py"],
            "start_dependencies": ["LEAVES_READABLE"], "completion_dependencies": ["C_RECEIPT_PASS", "K_RECEIPT_PASS", "D_READBACK_PASS"],
            "oracle": "all subjects resolve", "negative_controls": ["no hidden remaining item"],
            "rollback": "revert docs only", "budget": {"maximum_hours": 1, "maximum_files": 1},
        }
        self.plan = {
            "schema_version": "execution-planner-input@1", "run_id": "test-run", "subject_digest": subject_digest,
            "authority_ceiling": "PLANNING_ONLY", "decision": "VALIDATE", "atoms": [root_atom, child, convergence],
            "existing_gates": [{"issue": 33, "title": "market gate", "target": "other product", "relation": "EXISTING_GATE_DIFFERENT_PRODUCT_TARGET", "state": "OPEN", "required_action": "DO_NOT_DUPLICATE_OR_SUBSTITUTE"}],
            "issue_plan": [
                {"plan_id": "IP-001", "action": "CREATE_PROPOSAL", "atom_id": "PREL-C02", "title": "C", "existing_issue": None, "write_authority": "PROPOSAL_ONLY"},
                {"plan_id": "IP-002", "action": "CHILD_OF_IP-001", "atom_id": "PREL-K03", "title": "K", "existing_issue": None, "write_authority": "PROPOSAL_ONLY"},
                {"plan_id": "IP-003", "action": "CONVERGENCE_AFTER_LEAVES", "atom_id": "PREL-D02", "title": "D", "existing_issue": None, "write_authority": "PROPOSAL_ONLY"},
            ],
            "human_owned_operations": ["merge", "release", "rights admission", "customer truth", "commercial truth", "production promotion", "semantic conflict resolution"],
            "nonclaims": ["planning is not execution"],
        }

    def validate(self, plan=None):
        return validate_plan(plan or self.plan, self.stage6, self.skills)

    def test_valid_plan_compiles_dual_edge_outputs(self) -> None:
        self.validate()
        outputs = compile_outputs(self.plan, self.stage6, self.skills)
        self.assertTrue(outputs["execution-dag.json"]["laws"]["start_is_not_completion"])
        self.assertEqual("PREL-D02", outputs["stack-plan.json"]["convergence_owner"])
        self.assertEqual("ACTIVE", outputs["local-handoff-queue.json"]["items"][0]["state"])
        self.assertEqual(1, sum(i["state"] == "ACTIVE" for i in outputs["local-handoff-queue.json"]["items"]))

    def test_overlapping_writer_leases_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["atoms"][1]["owns_paths"] = ["docs/summary.md"]
        with self.assertRaisesRegex(ExecutionPlanError, "overlapping writer lease"):
            self.validate(plan)

    def test_false_child_edge_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["atoms"][1]["consumes_paths"] = ["unrelated/input.json"]
        with self.assertRaisesRegex(ExecutionPlanError, "false child edge"):
            self.validate(plan)

    def test_two_convergence_owners_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        extra = copy.deepcopy(plan["atoms"][-1])
        extra["id"] = "PREL-D03"
        extra["branch"] = "prel/d03"
        extra["owns_paths"] = ["docs/other.md"]
        plan["atoms"].append(extra)
        plan["issue_plan"].append({"plan_id": "IP-004", "action": "CONVERGENCE_AFTER_LEAVES", "atom_id": "PREL-D03", "title": "D2", "existing_issue": None, "write_authority": "PROPOSAL_ONLY"})
        with self.assertRaisesRegex(ExecutionPlanError, "exactly one convergence owner"):
            self.validate(plan)

    def test_issue_plan_cannot_gain_write_authority(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["issue_plan"][0]["write_authority"] = "WRITE"
        with self.assertRaisesRegex(ExecutionPlanError, "write authority widened"):
            self.validate(plan)

    def test_existing_gate_cannot_be_silently_recreated(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["existing_gates"][0]["required_action"] = "CREATE_DUPLICATE"
        with self.assertRaisesRegex(ExecutionPlanError, "existing gate handling invalid"):
            self.validate(plan)

    def test_human_authority_cannot_be_reduced(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["human_owned_operations"].remove("merge")
        with self.assertRaisesRegex(ExecutionPlanError, "Human-owned operation set drift"):
            self.validate(plan)

    def test_stage6_blob_drift_is_rejected(self) -> None:
        binding = copy.deepcopy(self.stage6)
        binding["matrix"]["blob_sha"] = "f" * 40
        with self.assertRaisesRegex(ExecutionPlanError, "Git blob drift"):
            validate_stage6_binding(binding, self.bytes["matrix"], self.bytes["audit"], self.bytes["delta"], self.bytes["shadow"])

    def test_stage6_ahead_of_design_closure_is_rejected(self) -> None:
        audit = copy.deepcopy(self.audit)
        audit["problems"][0]["highest_earned_level"] = "IMPLEMENTED"
        audit_bytes = canonical_json(audit).encode()
        binding = copy.deepcopy(self.stage6)
        binding["audit"]["blob_sha"] = git_blob_sha1(audit_bytes)
        binding["audit"]["canonical_digest"] = digest_json(audit)
        with self.assertRaisesRegex(ExecutionPlanError, "unexpectedly promotes closure"):
            validate_stage6_binding(binding, self.bytes["matrix"], audit_bytes, self.bytes["delta"], self.bytes["shadow"])

    def test_prompt_packets_are_zero_context_and_non_widening(self) -> None:
        prompts = compile_outputs(self.plan, self.stage6, self.skills)["prompts"]
        for prompt in prompts.values():
            self.assertIn("Do not use prior conversation as contract evidence", prompt)
            self.assertIn("no merge, permission, secret, rights, production", prompt.lower())
            self.assertIn("do not reveal private chain of thought", prompt.lower())

    def test_outputs_are_byte_stable(self) -> None:
        first = compile_outputs(self.plan, self.stage6, self.skills)
        second = compile_outputs(copy.deepcopy(self.plan), copy.deepcopy(self.stage6), copy.deepcopy(self.skills))
        for key in ("run-contract.json", "execution-dag.json", "issue-plan.json", "path-leases.json", "stack-plan.json", "local-handoff-queue.json"):
            self.assertEqual(canonical_json(first[key]), canonical_json(second[key]))
        self.assertEqual(first["prompts"], second["prompts"])

    def test_committed_canary_reproduces(self) -> None:
        canary = ROOT / "evals/execution-plan/structured-product-compiler"
        inherited = ROOT / "evals/problem-closure/modern-web-architecture"
        needed = [canary / "planner-input.json", canary / "skills-binding.json", canary / "stage6-binding.json", inherited / "problem-closure-matrix.json", inherited / "product-closure-audit.json", inherited / "issue-delta.json", inherited / "shadow-review.json"]
        if not all(p.is_file() for p in needed):
            self.skipTest("true-child inherited canary not present in isolated authoring fixture")
        outputs = compile_from_paths(canary / "planner-input.json", canary / "skills-binding.json", canary / "stage6-binding.json", inherited / "problem-closure-matrix.json", inherited / "product-closure-audit.json", inherited / "issue-delta.json", inherited / "shadow-review.json")
        for filename in ("run-contract.json", "execution-dag.json", "issue-plan.json", "path-leases.json", "stack-plan.json", "local-handoff-queue.json"):
            self.assertEqual(canonical_json(outputs[filename]), (canary / filename).read_text(encoding="utf-8"))
        for atom_id, text in outputs["prompts"].items():
            self.assertEqual(text, (canary / "prompt-packets" / f"{atom_id}.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
