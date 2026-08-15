#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_product_notes.compiler import (  # noqa: E402
    ValidationError,
    canonical_json,
    compile_opportunity,
    load_json,
    validate_packet,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile or validate an opportunity packet")
    parser.add_argument("signal", nargs="?", type=Path)
    parser.add_argument("--assets", type=Path)
    parser.add_argument("--public-portfolio", type=Path)
    parser.add_argument("--private-overlay", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path, help="validate an existing canonical packet")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.check:
            packet = load_json(args.check)
            validate_packet(packet)
            canonical = canonical_json(packet)
            observed = args.check.read_text(encoding="utf-8")
            if observed != canonical:
                raise ValidationError(f"{args.check} is valid JSON but not canonical")
            print(f"opportunity-packet: PASS {packet['packet_digest']}")
            return 0

        missing = [
            name
            for name, value in (
                ("signal", args.signal),
                ("--assets", args.assets),
                ("--public-portfolio", args.public_portfolio),
                ("--output", args.output),
            )
            if value is None
        ]
        if missing:
            raise ValidationError("missing required compile arguments: " + ", ".join(missing))
        packet = compile_opportunity(
            load_json(args.signal),
            load_json(args.assets),
            load_json(args.public_portfolio),
            load_json(args.private_overlay) if args.private_overlay else None,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(canonical_json(packet), encoding="utf-8")
        print(f"opportunity-compiler: {packet['decision']} {packet['score']['score_0_100']} {packet['packet_digest']}")
        return 0
    except ValidationError as exc:
        print(f"opportunity-compiler: FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
