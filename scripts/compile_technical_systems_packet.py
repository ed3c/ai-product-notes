from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.technical_systems import (  # noqa: E402
    TechnicalSystemsError,
    canonical_json,
    compile_from_paths,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a bounded Stage 5 technical systems packet")
    parser.add_argument("--dossier", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        packet = compile_from_paths(args.dossier, args.binding, args.plan)
    except (OSError, ValueError, TechnicalSystemsError) as exc:
        print(f"technical systems packet rejected: {exc}", file=sys.stderr)
        return 2

    rendered = canonical_json(packet)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            print("technical systems packet drift", file=sys.stderr)
            return 1
        print(f"PASS {packet['packet_digest']}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"PASS {packet['packet_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
