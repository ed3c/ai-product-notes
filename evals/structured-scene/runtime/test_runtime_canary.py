from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "scripts" / "run_structured_scene_canary.py"


class StructuredSceneRuntimeCanaryTests(unittest.TestCase):
    def _codex_env(self, **updates: str) -> dict[str, str]:
        env = dict(os.environ)
        for name in ("GITHUB_ACTIONS", "CLAUDECODE", "CLAUDE_PROJECT_DIR"):
            env.pop(name, None)
        env["CODEX_THREAD_ID"] = "test-thread"
        env.update(updates)
        return env

    def _git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            check=True,
        )

    def _prepare_candidate(self, root: Path, *, outside_lease: bool = False) -> dict[str, object]:
        self._git(root, "init", "-q", "-b", "fixture/runtime")
        self._git(root, "config", "user.name", "Runtime Canary Test")
        self._git(root, "config", "user.email", "runtime-canary@example.invalid")
        package = root / "src" / "ai_product_notes"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        shutil.copy2(ROOT / "src" / "ai_product_notes" / "scene_spec.py", package)
        shutil.copy2(ROOT / "src" / "ai_product_notes" / "constraint_validator.py", package)
        self._git(root, "add", "src")
        self._git(root, "commit", "-q", "-m", "deterministic parent")
        base = self._git(root, "rev-parse", "HEAD").stdout.strip()

        script = root / "scripts" / RUNNER.name
        script.parent.mkdir()
        shutil.copy2(RUNNER, script)
        runtime = root / "evals" / "structured-scene" / "runtime"
        runtime.mkdir(parents=True)
        input_packet = json.loads(
            (ROOT / "evals" / "structured-scene" / "runtime" / "input.json").read_text(
                encoding="utf-8"
            )
        )
        input_path = runtime / "input.json"
        input_path.write_text(
            json.dumps(input_packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        contract = {
            "schema_version": "structured-scene-runtime-contract@1",
            "atom": "PREL-X02",
            "repository": "ed3c/ai-product-notes",
            "expected_base": base,
            "expected_branch": "fixture/runtime",
            "runtime_identities": ["CODEX_CLI_LOCAL", "CLAUDE_CODE_LOCAL"],
            "input_path": "evals/structured-scene/runtime/input.json",
            "receipt_path": "evals/structured-scene/runtime/receipt.json",
            "allowed_paths": [
                "scripts/run_structured_scene_canary.py",
                "evals/structured-scene/runtime/**",
            ],
            "authority_ceiling": "LOCAL_RUNTIME_ATOM_ONLY",
        }
        contract_path = runtime / "contract.json"
        contract_path.write_text(
            json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if outside_lease:
            (root / "outside-lease.txt").write_text("forbidden\n", encoding="utf-8")
        self._git(root, "add", "scripts", "evals")
        if outside_lease:
            self._git(root, "add", "outside-lease.txt")
        self._git(root, "commit", "-q", "-m", "runtime candidate")
        return {
            "base": base,
            "candidate": self._git(root, "rev-parse", "HEAD").stdout.strip(),
            "tree": self._git(root, "rev-parse", "HEAD^{tree}").stdout.strip(),
            "script": script,
            "runtime": runtime,
            "input": input_path,
        }

    def test_public_cli_selftest_closes_required_negative_controls(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "--selftest"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(
            "SELFTEST PASS controls=authority-ceiling,hosted-ci,path-lease,receipt-digest\n",
            completed.stdout,
        )

    def test_check_refuses_a_dirty_workspace_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._git(root, "init", "-q")
            self._git(root, "config", "user.name", "Runtime Canary Test")
            self._git(root, "config", "user.email", "runtime-canary@example.invalid")
            (root / "tracked.txt").write_text("clean\n", encoding="utf-8")
            self._git(root, "add", "tracked.txt")
            self._git(root, "commit", "-q", "-m", "fixture")
            (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--check",
                    "--repo-root",
                    str(root),
                    "--runtime-identity",
                    "CODEX_CLI_LOCAL",
                ],
                cwd=ROOT,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

        self.assertEqual(2, completed.returncode)
        self.assertIn("BLOCK dirty workspace", completed.stderr)

    def test_hosted_actions_cannot_impersonate_the_local_runtime_lane(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._git(root, "init", "-q")
            self._git(root, "config", "user.name", "Runtime Canary Test")
            self._git(root, "config", "user.email", "runtime-canary@example.invalid")
            (root / "tracked.txt").write_text("clean\n", encoding="utf-8")
            self._git(root, "add", "tracked.txt")
            self._git(root, "commit", "-q", "-m", "fixture")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--check",
                    "--repo-root",
                    str(root),
                    "--runtime-identity",
                    "CODEX_CLI_LOCAL",
                ],
                cwd=ROOT,
                env=self._codex_env(GITHUB_ACTIONS="true"),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

        self.assertEqual(2, completed.returncode)
        self.assertIn("BLOCK hosted CI cannot satisfy the local runtime lane", completed.stderr)

    def test_clean_checkout_executes_workflow_and_persists_exact_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self._prepare_candidate(root)

            completed = subprocess.run(
                [sys.executable, str(fixture["script"]), "--check", "--repo-root", str(root)],
                cwd=root,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            receipt_path = Path(fixture["runtime"]) / "receipt.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        self.assertIn("PASS receipt created", completed.stdout)
        self.assertEqual(fixture["base"], receipt["subject"]["base_sha"])
        self.assertEqual(fixture["candidate"], receipt["subject"]["head_sha"])
        self.assertEqual(fixture["tree"], receipt["subject"]["tree_sha"])
        self.assertEqual("PASS", receipt["evidence_state"]["local_runtime"])
        self.assertEqual("ABSENT", receipt["evidence_state"]["user"])
        self.assertEqual("ABSENT", receipt["evidence_state"]["paid"])
        self.assertEqual("HUMAN_ADMIT_REQUIRED", receipt["evidence_state"]["rights"])
        self.assertEqual("CLEAN", receipt["cleanup"]["pre_run"])
        self.assertEqual(
            "RECEIPT_ONLY_PENDING_COMMIT", receipt["cleanup"]["post_run"]
        )
        self.assertEqual(0, receipt["command_receipt"]["exit_code"])
        self.assertTrue(receipt["command_receipt"]["bounded"])
        self.assertEqual(
            "ABSENT", receipt["queue_reconciliation"]["stage7_predecessor_receipt"]
        )

    def test_candidate_with_an_out_of_lease_write_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self._prepare_candidate(root, outside_lease=True)
            completed = subprocess.run(
                [sys.executable, str(fixture["script"]), "--check", "--repo-root", str(root)],
                cwd=root,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

        self.assertEqual(2, completed.returncode)
        self.assertIn("BLOCK write escaped runtime lease: outside-lease.txt", completed.stderr)

    def test_committed_receipt_becomes_stale_after_input_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self._prepare_candidate(root)
            command = [
                sys.executable,
                str(fixture["script"]),
                "--check",
                "--repo-root",
                str(root),
            ]
            created = subprocess.run(
                command,
                cwd=root,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(0, created.returncode, created.stderr)
            self._git(root, "add", "evals/structured-scene/runtime/receipt.json")
            self._git(root, "commit", "-q", "-m", "persist runtime receipt")
            verified = subprocess.run(
                command,
                cwd=root,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(0, verified.returncode, verified.stderr)

            input_path = Path(fixture["input"])
            mutated = json.loads(input_path.read_text(encoding="utf-8"))
            mutated["nodes"][0]["x"] = 41
            input_path.write_text(
                json.dumps(mutated, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self._git(root, "add", str(input_path.relative_to(root)))
            self._git(root, "commit", "-q", "-m", "mutate runtime input")
            stale = subprocess.run(
                command,
                cwd=root,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

        self.assertEqual(
            "PASS receipt verified workspace=CLEAN cleanup=PASS\n", verified.stdout
        )
        self.assertEqual(2, stale.returncode)
        self.assertIn(
            "BLOCK current HEAD is not the single receipt commit over its subject",
            stale.stderr,
        )

    def test_missing_runtime_provenance_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._git(root, "init", "-q")
            env = self._codex_env()
            env.pop("CODEX_THREAD_ID")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--check",
                    "--repo-root",
                    str(root),
                    "--runtime-identity",
                    "CODEX_CLI_LOCAL",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

        self.assertEqual(2, completed.returncode)
        self.assertIn("BLOCK CODEX_CLI_LOCAL requires current Codex thread evidence", completed.stderr)

    def test_worker_exit_zero_without_durable_receipt_is_not_runtime_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self._prepare_candidate(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(fixture["script"]),
                    "--execute-worker",
                    "--repo-root",
                    str(root),
                    "--input",
                    "evals/structured-scene/runtime/input.json",
                ],
                cwd=root,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            receipt_exists = (Path(fixture["runtime"]) / "receipt.json").exists()

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertFalse(receipt_exists)

    def test_receipt_path_cannot_escape_the_runtime_lease(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self._prepare_candidate(root)
            contract_path = Path(fixture["runtime"]) / "contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["receipt_path"] = "../escaped-receipt.json"
            contract_path.write_text(
                json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self._git(root, "add", str(contract_path.relative_to(root)))
            self._git(root, "commit", "-q", "-m", "attempt receipt escape")
            escaped = root / "evals" / "structured-scene" / "escaped-receipt.json"
            completed = subprocess.run(
                [sys.executable, str(fixture["script"]), "--check", "--repo-root", str(root)],
                cwd=root,
                env=self._codex_env(),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

        self.assertEqual(2, completed.returncode)
        self.assertIn("BLOCK receipt_path must be a normalized", completed.stderr)
        self.assertFalse(escaped.exists())


if __name__ == "__main__":
    unittest.main()
