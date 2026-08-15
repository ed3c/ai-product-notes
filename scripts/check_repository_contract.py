#!/usr/bin/env python3
"""Fail-closed static contract checker for repository governance surfaces."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

BEGIN = "<!-- BEGIN SKILLS-SHARED INSTRUCTION PROJECTION -->"
END = "<!-- END SKILLS-SHARED INSTRUCTION PROJECTION -->"
EXPECTED_MANAGED_BLOCK_SHA256 = "6e1f2d31b9dab7078fbfc057ef8fde056c89e44ae50d4178d32e644acdb5fd9e"

REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "docs/ARCHITECTURE.md",
    "docs/STATE_MACHINES.md",
    "docs/MARKET_SIGNAL_CONTRACT.md",
    "docs/MVP_ROADMAP.md",
    "docs/CONFIG.md",
    "docs/DAILY_MONITOR_PROMPT.md",
    "docs/git/README.md",
    "docs/git/REPO_PROFILE.md",
    "docs/git/STACKED_PRS.md",
    "docs/git/WORKER_PROTOCOL.md",
    "docs/git/GIT_TOWN_ADMISSION.md",
)

REQUIRED_STATES = (
    "DISCOVERED",
    "FRESHNESS_VERIFIED",
    "DEMAND_EVIDENCE_BOUND",
    "STACK_DECOMPOSED",
    "LICENSE_GATED",
    "PORTFOLIO_MATCHED",
    "GAP_CLASSIFIED",
    "OPPORTUNITY_SCORED",
    "MVP_PACKETED",
    "EXPERIMENT_RUNNING",
    "OUTCOME_VERIFIED",
    "ADMITTED_TO_ROADMAP",
)


def _read(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"ABSENT required file: {relative}")

    if errors:
        return errors

    readme = _read(root, "README.md")
    agents = _read(root, "AGENTS.md")
    config = _read(root, "docs/CONFIG.md")
    git_readme = _read(root, "docs/git/README.md")
    admission = _read(root, "docs/git/GIT_TOWN_ADMISSION.md")

    for state in REQUIRED_STATES:
        if state not in readme:
            errors.append(f"README missing State Machine owner: {state}")

    boundary_phrases = (
        "Git-ignored private overlay",
        "Private repository content is never an input to committed public artifacts",
        "repo names / paths / URLs / code / raw traces / customer data / credentials",
    )
    for phrase in boundary_phrases:
        if phrase not in readme:
            errors.append(f"README missing public/private boundary: {phrase}")

    if "| Live `git town sync` | `NOT_EXERCISED` |" not in readme:
        errors.append("README must keep live Git Town sync at NOT_EXERCISED")
    if "exact Git Town admission: ABSENT / BLOCKED_POLICY" not in git_readme:
        errors.append("Git governance must keep exact Git Town admission ABSENT / BLOCKED_POLICY")
    if "Repository config | `ABSENT_BY_POLICY`" not in admission:
        errors.append("Git Town config must remain ABSENT_BY_POLICY until admission")
    for candidate in (".git-town.toml", "git-town.toml", ".git-branches.toml"):
        if (root / candidate).exists():
            errors.append(f"Unadmitted Git Town config present: {candidate}")

    if agents.count(BEGIN) != 1 or agents.count(END) != 1:
        errors.append("AGENTS managed projection markers must exist exactly once")
    else:
        start = agents.index(BEGIN)
        finish = agents.index(END, start) + len(END)
        managed = agents[start:finish]
        digest = hashlib.sha256(managed.encode("utf-8")).hexdigest()
        if digest != EXPECTED_MANAGED_BLOCK_SHA256:
            errors.append(
                "AGENTS managed projection drift: "
                f"expected {EXPECTED_MANAGED_BLOCK_SHA256}, observed {digest}"
            )

    required_config = (
        "DATA_INCREMENT_LANE",
        "PRODUCT_CHANGE_LANE",
        "Interactive Agents do not use this lane to bypass review",
        "Issue-first reviewable branches are mandatory",
    )
    for phrase in required_config:
        if phrase not in config:
            errors.append(f"CONFIG missing delivery guard: {phrase}")

    forbidden_claims = (
        "live Git Town sync: PASS",
        "exact Git Town admission: PASS",
        "market validated: PASS",
    )
    for relative in REQUIRED_FILES:
        text = _read(root, relative)
        for claim in forbidden_claims:
            if claim in text:
                errors.append(f"Forbidden unsupported claim in {relative}: {claim}")

    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("repository-contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
