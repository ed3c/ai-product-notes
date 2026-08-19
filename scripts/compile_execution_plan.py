#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.execution_planner import (  # noqa: E402
    ExecutionPlanError,
    canonical_json,
    compile_from_paths,
)


def main() -> int:
    canary = ROOT / "evals" / "execution-plan" / "structured-product-compiler"
    parser = argparse.ArgumentParser(description="Compile exact Stage 7 execution planning artifacts.")
    parser.add_argument("--plan", type=Path, default=canary / "planner-input.json")
    parser.add_argument("--skills-binding", type=Path, default=canary / "skills-binding.json")
    parser.add_argument("--stage6-binding", type=Path, default=canary / "stage6-binding.json")
    parser.add_argument("--matrix", type=Path, default=ROOT / "evals/problem-closure/modern-web-architecture/problem-closure-matrix.json")
    parser.add_argument("--audit", type=Path, default=ROOT / "evals/problem-closure/modern-web-architecture/product-closure-audit.json")
    parser.add_argument("--delta", type=Path, default=ROOT / "evals/problem-closure/modern-web-architecture/issue-delta.json")
    parser.add_argument("--shadow", type=Path, default=ROOT / "evals/problem-closure/modern-web-architecture/shadow-review.json")
    parser.add_argument("--output-dir", type=Path, default=canary)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs = compile_from_paths(
            args.plan,
            args.skills_binding,
            args.stage6_binding,
            args.matrix,
            args.audit,
            args.delta,
            args.shadow,
        )
    except (ExecutionPlanError, OSError, json.JSONDecodeError) as exc:
        print(f"execution planning failed: {exc}", file=sys.stderr)
        return 2

    failures: list[str] = []
    for filename in (
        "run-contract.json",
        "execution-dag.json",
        "issue-plan.json",
        "path-leases.json",
        "stack-plan.json",
        "local-handoff-queue.json",
    ):
        path = args.output_dir / filename
        expected = canonical_json(outputs[filename])
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                failures.append(f"CANONICAL_DRIFT:{filename}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    prompt_dir = args.output_dir / "prompt-packets"
    for atom_id, text in outputs["prompts"].items():
        path = prompt_dir / f"{atom_id}.md"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                failures.append(f"CANONICAL_DRIFT:prompt-packets/{atom_id}.md")
        else:
            prompt_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    print(json.dumps({"status": "PASS" if not failures else "FAIL", "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
