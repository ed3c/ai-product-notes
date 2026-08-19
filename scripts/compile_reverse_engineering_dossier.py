#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.reverse_engineering import (  # noqa: E402
    DossierError,
    canonical_json,
    compile_dossier,
    load_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a source-constrained reverse-engineering dossier")
    parser.add_argument("--product-signal", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--hypotheses", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        signal_bytes = args.product_signal.read_bytes()
        dossier = compile_dossier(
            load_json(args.product_signal),
            load_json(args.binding),
            load_json(args.hypotheses),
            snapshot_bytes=signal_bytes,
        )
    except (OSError, DossierError) as exc:
        print(f"reverse-engineering dossier rejected: {exc}", file=sys.stderr)
        return 2

    rendered = canonical_json(dossier)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            print("reverse-engineering dossier drift", file=sys.stderr)
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")

    print(f"decision={dossier['decision']}")
    print(f"authority_ceiling={dossier['authority_ceiling']}")
    print(f"dossier_digest={dossier['dossier_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
