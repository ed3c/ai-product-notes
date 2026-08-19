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

from ai_product_notes.problem_closure import (  # noqa: E402
    ClosureError,
    canonical_json,
    compile_outputs,
    load_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile exact-subject product closure artifacts.")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--skills-binding", type=Path, required=True)
    parser.add_argument("--stage5-binding", type=Path, required=True)
    parser.add_argument("--technical-packet", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--delta", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        packet_bytes = args.technical_packet.read_bytes()
        matrix, audit, delta = compile_outputs(
            load_json(args.plan),
            load_json(args.skills_binding),
            load_json(args.stage5_binding),
            json.loads(packet_bytes.decode("utf-8")),
            packet_bytes,
        )
    except (ClosureError, OSError, json.JSONDecodeError) as exc:
        print(f"closure compilation failed: {exc}", file=sys.stderr)
        return 2

    outputs = (
        (args.matrix, canonical_json(matrix)),
        (args.audit, canonical_json(audit)),
        (args.delta, canonical_json(delta)),
    )
    failures: list[str] = []
    for path, expected in outputs:
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                failures.append(f"CANONICAL_DRIFT:{path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    print(json.dumps({"status": "PASS" if not failures else "FAIL", "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
