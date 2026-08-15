from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when input would weaken the decision, rights, or privacy contract."""


RIGHT_TYPES = (
    "code",
    "model_weights",
    "datasets",
    "trajectories",
    "hosted_service",
    "third_party_content",
)
RIGHT_STATES = {"PASS", "CONDITIONAL", "UNKNOWN", "REJECT", "NOT_APPLICABLE", "STALE"}
PORTFOLIO_STATES = {
    "ABSENT",
    "PLANNED",
    "MATERIALIZED",
    "TESTED",
    "VERIFIED",
    "ADMITTED",
    "BLOCKED",
    "NOT_EXERCISED",
}
STRONG_PORTFOLIO_STATES = {"TESTED", "VERIFIED", "ADMITTED"}
WEAK_PORTFOLIO_STATES = {"MATERIALIZED"}
EVIDENCE_LABELS = {"technical_equivalent", "candidate", "inference", "human_required"}
PAID_KINDS = {"paid_pilot", "preorder", "signed_loi"}
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,127}$")
SHA256_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
SAFE_PRIVATE_KEYS = {
    "capability_id",
    "contract_version",
    "state",
    "evidence_label",
    "receipt_digest",
    "exportable",
    "limitations",
}
FORBIDDEN_PRIVATE_KEY_PARTS = {
    "repository",
    "repo",
    "url",
    "path",
    "owner",
    "code",
    "trace",
    "customer",
    "credential",
    "secret",
    "token",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot load JSON {path}: {exc}") from exc


def _object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{where} must be an object")
    return value


def _array(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{where} must be an array")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{where} must be a non-empty string")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], where: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        raise ValidationError(f"{where} missing keys: {', '.join(missing)}")
    if unknown:
        raise ValidationError(f"{where} has unknown keys: {', '.join(unknown)}")


def _id(value: Any, where: str) -> str:
    text = _text(value, where)
    if not SAFE_ID.fullmatch(text):
        raise ValidationError(f"{where} has an invalid identifier")
    return text


def _score(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{where} must be a number from 1 to 10")
    result = float(value)
    if not 1 <= result <= 10:
        raise ValidationError(f"{where} must be between 1 and 10")
    return result


def validate_signal(raw: Any) -> dict[str, Any]:
    signal = _object(raw, "signal")
    _exact_keys(
        signal,
        {
            "schema_version",
            "id",
            "title",
            "observed_at",
            "freshness",
            "target_segment",
            "problem",
            "wedge",
            "metrics",
            "demand_evidence",
            "required_capabilities",
            "constraints",
            "mvp",
        },
        "signal",
    )
    if signal["schema_version"] != "market-signal.v1":
        raise ValidationError("signal.schema_version must be market-signal.v1")
    _id(signal["id"], "signal.id")
    for key in ("title", "observed_at", "target_segment", "problem", "wedge"):
        _text(signal[key], f"signal.{key}")

    freshness = _object(signal["freshness"], "signal.freshness")
    _exact_keys(freshness, {"event_date", "source_date", "window_hours", "status"}, "signal.freshness")
    _text(freshness["event_date"], "signal.freshness.event_date")
    _text(freshness["source_date"], "signal.freshness.source_date")
    if not isinstance(freshness["window_hours"], int) or freshness["window_hours"] <= 0:
        raise ValidationError("signal.freshness.window_hours must be positive")
    if freshness["status"] not in {"PASS", "FAIL", "UNKNOWN"}:
        raise ValidationError("signal.freshness.status is invalid")

    metric_keys = {
        "pain_intensity",
        "wtp_evidence",
        "recurrence",
        "distribution_reach",
        "market_timing",
        "competition_pressure",
        "evidence_confidence",
    }
    metrics = _object(signal["metrics"], "signal.metrics")
    _exact_keys(metrics, metric_keys, "signal.metrics")
    for key in metric_keys:
        _score(metrics[key], f"signal.metrics.{key}")

    evidence_keys = {
        "id",
        "kind",
        "source_class",
        "observed_at",
        "claim",
        "strength",
        "independent_group",
        "source_url",
        "direct_paid_demand",
    }
    for index, raw_item in enumerate(_array(signal["demand_evidence"], "signal.demand_evidence")):
        item = _object(raw_item, f"signal.demand_evidence[{index}]")
        _exact_keys(item, evidence_keys, f"signal.demand_evidence[{index}]")
        _id(item["id"], f"signal.demand_evidence[{index}].id")
        for key in ("kind", "source_class", "observed_at", "claim", "independent_group", "source_url"):
            _text(item[key], f"signal.demand_evidence[{index}].{key}")
        if not item["source_url"].startswith(("https://", "http://")):
            raise ValidationError("demand evidence source_url must be HTTP(S)")
        if isinstance(item["strength"], bool) or not isinstance(item["strength"], int) or not 1 <= item["strength"] <= 5:
            raise ValidationError("demand evidence strength must be an integer from 1 to 5")
        if not isinstance(item["direct_paid_demand"], bool):
            raise ValidationError("direct_paid_demand must be boolean")
        if item["direct_paid_demand"] and item["kind"] not in PAID_KINDS:
            raise ValidationError("only paid_pilot, preorder, or signed_loi can prove direct paid demand")

    requirement_keys = {
        "id",
        "importance",
        "asset_types",
        "accepted_asset_capabilities",
        "portfolio_capabilities",
        "description",
    }
    seen: set[str] = set()
    for index, raw_item in enumerate(_array(signal["required_capabilities"], "signal.required_capabilities")):
        item = _object(raw_item, f"signal.required_capabilities[{index}]")
        _exact_keys(item, requirement_keys, f"signal.required_capabilities[{index}]")
        capability_id = _id(item["id"], f"signal.required_capabilities[{index}].id")
        if capability_id in seen:
            raise ValidationError(f"duplicate capability id: {capability_id}")
        seen.add(capability_id)
        if item["importance"] not in {"must", "should", "could"}:
            raise ValidationError("capability importance is invalid")
        _text(item["description"], "capability description")
        asset_types = _array(item["asset_types"], "capability asset_types")
        if not asset_types or any(asset_type not in RIGHT_TYPES for asset_type in asset_types):
            raise ValidationError("capability asset_types are invalid")
        for list_key in ("accepted_asset_capabilities", "portfolio_capabilities"):
            for value in _array(item[list_key], f"capability {list_key}"):
                _id(value, f"capability {list_key}[]")

    constraints = _object(signal["constraints"], "signal.constraints")
    _exact_keys(
        constraints,
        {"public_output", "maximum_days", "budget_usd", "durable_owner_state", "hard_blockers"},
        "signal.constraints",
    )
    if constraints["public_output"] is not True:
        raise ValidationError("public_output must be true for this public repository")
    for key in ("maximum_days", "budget_usd"):
        if isinstance(constraints[key], bool) or not isinstance(constraints[key], (int, float)) or constraints[key] <= 0:
            raise ValidationError(f"signal.constraints.{key} must be positive")
    if constraints["maximum_days"] > 30:
        raise ValidationError("maximum_days must remain bounded to 30")
    _text(constraints["durable_owner_state"], "durable_owner_state")
    for blocker in _array(constraints["hard_blockers"], "hard_blockers"):
        _text(blocker, "hard_blockers[]")

    mvp = _object(signal["mvp"], "signal.mvp")
    _exact_keys(mvp, {"hypothesis", "price_test_usd_month", "success_metrics", "stop_loss", "non_goals"}, "signal.mvp")
    _text(mvp["hypothesis"], "signal.mvp.hypothesis")
    if isinstance(mvp["price_test_usd_month"], bool) or not isinstance(mvp["price_test_usd_month"], (int, float)) or mvp["price_test_usd_month"] <= 0:
        raise ValidationError("price_test_usd_month must be positive")
    for key in ("success_metrics", "stop_loss", "non_goals"):
        values = _array(mvp[key], f"signal.mvp.{key}")
        if not values:
            raise ValidationError(f"signal.mvp.{key} must not be empty")
        for value in values:
            _text(value, f"signal.mvp.{key}[]")
    return signal


def validate_assets(raw: Any) -> dict[str, Any]:
    registry = _object(raw, "asset_registry")
    _exact_keys(registry, {"schema_version", "assets"}, "asset_registry")
    if registry["schema_version"] != "asset-registry.v1":
        raise ValidationError("asset_registry.schema_version must be asset-registry.v1")
    seen: set[str] = set()
    for index, raw_asset in enumerate(_array(registry["assets"], "asset_registry.assets")):
        asset = _object(raw_asset, f"asset_registry.assets[{index}]")
        _exact_keys(
            asset,
            {"id", "name", "source_url", "verified_commit", "capabilities", "maturity", "rights", "limitations"},
            f"asset_registry.assets[{index}]",
        )
        asset_id = _id(asset["id"], "asset.id")
        if asset_id in seen:
            raise ValidationError(f"duplicate asset id: {asset_id}")
        seen.add(asset_id)
        _text(asset["name"], "asset.name")
        if not _text(asset["source_url"], "asset.source_url").startswith("https://github.com/"):
            raise ValidationError("asset.source_url must be GitHub")
        if not re.fullmatch(r"[0-9a-f]{40}", _text(asset["verified_commit"], "asset.verified_commit")):
            raise ValidationError("asset.verified_commit must be a full SHA")
        for capability in _array(asset["capabilities"], "asset.capabilities"):
            _id(capability, "asset.capabilities[]")
        _score(asset["maturity"], "asset.maturity")
        for limitation in _array(asset["limitations"], "asset.limitations"):
            _text(limitation, "asset.limitations[]")
        rights = _object(asset["rights"], "asset.rights")
        _exact_keys(rights, set(RIGHT_TYPES), "asset.rights")
        for right_type in RIGHT_TYPES:
            right = _object(rights[right_type], f"asset.rights.{right_type}")
            _exact_keys(
                right,
                {"status", "license", "evidence_url", "scope", "commercial_use", "source_disclosure_required"},
                f"asset.rights.{right_type}",
            )
            if right["status"] not in RIGHT_STATES:
                raise ValidationError(f"invalid right state: {right['status']}")
            for key in ("license", "evidence_url", "scope"):
                if not isinstance(right[key], str):
                    raise ValidationError(f"asset.rights.{right_type}.{key} must be a string")
            if not isinstance(right["commercial_use"], bool) or not isinstance(right["source_disclosure_required"], bool):
                raise ValidationError("right booleans are invalid")
            if right["status"] == "PASS" and (
                not right["license"]
                or not right["evidence_url"].startswith("https://github.com/")
                or right["commercial_use"] is not True
                or right["source_disclosure_required"] is not False
            ):
                raise ValidationError(f"PASS right lacks direct permissive evidence: {asset_id}/{right_type}")
    return registry


def validate_public_portfolio(raw: Any) -> dict[str, Any]:
    portfolio = _object(raw, "public_portfolio")
    _exact_keys(portfolio, {"schema_version", "capabilities"}, "public_portfolio")
    if portfolio["schema_version"] != "public-portfolio.v1":
        raise ValidationError("public_portfolio.schema_version must be public-portfolio.v1")
    seen: set[str] = set()
    for index, raw_item in enumerate(_array(portfolio["capabilities"], "public_portfolio.capabilities")):
        item = _object(raw_item, f"public_portfolio.capabilities[{index}]")
        _exact_keys(item, {"id", "contract_version", "state", "evidence_label", "source_url", "limitations"}, "public capability")
        capability_id = _id(item["id"], "public capability id")
        if capability_id in seen:
            raise ValidationError(f"duplicate public capability id: {capability_id}")
        seen.add(capability_id)
        _text(item["contract_version"], "public capability contract_version")
        if item["state"] not in PORTFOLIO_STATES or item["evidence_label"] not in EVIDENCE_LABELS:
            raise ValidationError("public capability state/evidence_label is invalid")
        if not _text(item["source_url"], "public capability source_url").startswith("https://github.com/"):
            raise ValidationError("public capability source_url must be GitHub")
        for limitation in _array(item["limitations"], "public capability limitations"):
            _text(limitation, "public capability limitations[]")
    return portfolio


def _scan_private(value: Any, where: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower().replace("-", "_")
            if any(part in lowered for part in FORBIDDEN_PRIVATE_KEY_PARTS):
                raise ValidationError(f"private overlay forbidden key at {where}: {key}")
            _scan_private(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_private(child, f"{where}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in ("http://", "https://", "github.com", "git@", "/users/", "/home/", "c:\\", "@")):
            raise ValidationError(f"private overlay contains URL/path/account-like value at {where}")


def validate_private_overlay(raw: Any | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    overlay = _object(raw, "private_overlay")
    _exact_keys(overlay, {"schema_version", "capabilities"}, "private_overlay")
    if overlay["schema_version"] != "private-capability-overlay.v1":
        raise ValidationError("private overlay schema is invalid")
    seen: set[str] = set()
    for index, raw_item in enumerate(_array(overlay["capabilities"], "private_overlay.capabilities")):
        item = _object(raw_item, f"private_overlay.capabilities[{index}]")
        _exact_keys(item, SAFE_PRIVATE_KEYS, f"private_overlay.capabilities[{index}]")
        capability_id = _id(item["capability_id"], "private capability id")
        if capability_id in seen:
            raise ValidationError(f"duplicate private capability id: {capability_id}")
        seen.add(capability_id)
        _text(item["contract_version"], "private contract_version")
        if item["state"] not in PORTFOLIO_STATES or item["evidence_label"] not in EVIDENCE_LABELS:
            raise ValidationError("private capability state/evidence_label is invalid")
        if not SHA256_ID.fullmatch(_text(item["receipt_digest"], "private receipt_digest")):
            raise ValidationError("private receipt_digest must be sha256:<64 hex>")
        if not isinstance(item["exportable"], bool):
            raise ValidationError("private exportable must be boolean")
        for limitation in _array(item["limitations"], "private limitations"):
            _text(limitation, "private limitations[]")
        _scan_private(item, f"private_overlay.capabilities[{index}]")
    return overlay


def _right_passes(asset: Mapping[str, Any], required_types: list[str]) -> tuple[bool, list[str]]:
    failures = [
        f"{right_type}:{asset['rights'][right_type]['status']}"
        for right_type in required_types
        if asset["rights"][right_type]["status"] != "PASS"
    ]
    return not failures, failures


def _analyze_capabilities(
    signal: Mapping[str, Any],
    registry: Mapping[str, Any],
    public_portfolio: Mapping[str, Any],
    private_overlay: Mapping[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[str], list[str], float, float]:
    public_by_id = {item["id"]: item for item in public_portfolio["capabilities"]}
    private_by_id = {
        item["capability_id"]: item
        for item in (private_overlay or {}).get("capabilities", [])
        if item["exportable"] is True
    }
    analyses: list[dict[str, Any]] = []
    must_gaps: list[str] = []
    hard_rights_gaps: list[str] = []
    must_total = asset_covered = portfolio_covered = 0

    for requirement in signal["required_capabilities"]:
        accepted = set(requirement["accepted_asset_capabilities"])
        passing_assets: list[dict[str, Any]] = []
        rejected_assets: list[dict[str, Any]] = []
        matching_asset_count = 0
        for asset in registry["assets"]:
            matched = sorted(accepted.intersection(asset["capabilities"]))
            if not matched:
                continue
            matching_asset_count += 1
            summary = {"asset_id": asset["id"], "matched_capabilities": matched, "maturity": asset["maturity"]}
            passes, failures = _right_passes(asset, requirement["asset_types"])
            if passes:
                passing_assets.append(summary)
            else:
                rejected_assets.append({**summary, "right_failures": failures})

        public_matches: list[dict[str, Any]] = []
        private_matches: list[dict[str, Any]] = []
        strong_portfolio = weak_portfolio = False
        for capability_id in requirement["portfolio_capabilities"]:
            public = public_by_id.get(capability_id)
            if public:
                public_matches.append(
                    {
                        "capability_id": capability_id,
                        "contract_version": public["contract_version"],
                        "evidence_label": public["evidence_label"],
                        "source": "public",
                        "state": public["state"],
                    }
                )
                strong_portfolio |= public["state"] in STRONG_PORTFOLIO_STATES
                weak_portfolio |= public["state"] in WEAK_PORTFOLIO_STATES
            private = private_by_id.get(capability_id)
            if private:
                private_matches.append({**{key: private[key] for key in sorted(SAFE_PRIVATE_KEYS)}, "source": "private-envelope"})
                strong_portfolio |= private["state"] in STRONG_PORTFOLIO_STATES
                weak_portfolio |= private["state"] in WEAK_PORTFOLIO_STATES

        covered = bool(passing_assets) or strong_portfolio
        candidate = bool(matching_asset_count) or weak_portfolio
        gap_state = "covered" if covered else "candidate" if candidate else "gap"
        if requirement["importance"] == "must":
            must_total += 1
            asset_covered += int(bool(passing_assets))
            portfolio_covered += int(strong_portfolio)
            if not covered:
                must_gaps.append(requirement["id"])
            if matching_asset_count and not passing_assets and not strong_portfolio:
                hard_rights_gaps.append(requirement["id"])

        analyses.append(
            {
                "accepted_asset_candidates": passing_assets,
                "description": requirement["description"],
                "gap_state": gap_state,
                "id": requirement["id"],
                "importance": requirement["importance"],
                "private_portfolio_matches": private_matches,
                "public_portfolio_matches": public_matches,
                "rejected_asset_candidates": rejected_assets,
                "required_asset_types": requirement["asset_types"],
            }
        )

    denominator = max(must_total, 1)
    return (
        analyses,
        must_gaps,
        hard_rights_gaps,
        round(10 * portfolio_covered / denominator, 2),
        round(10 * asset_covered / denominator, 2),
    )


def _demand(signal: Mapping[str, Any]) -> dict[str, Any]:
    qualified = [item for item in signal["demand_evidence"] if item["strength"] >= 3]
    groups = sorted({item["independent_group"] for item in qualified})
    paid = [item["id"] for item in qualified if item["direct_paid_demand"] and item["kind"] in PAID_KINDS]
    customer = [item["id"] for item in qualified if item["source_class"] == "CUSTOMER"]
    return {
        "customer_origin_evidence": customer,
        "direct_paid_demand": bool(paid),
        "direct_paid_evidence_ids": paid,
        "independent_evidence_groups": groups,
        "qualified": signal["freshness"]["status"] == "PASS" and len(groups) >= 2,
        "qualified_evidence_count": len(qualified),
    }


def _opportunity_score(signal: Mapping[str, Any], portfolio_fit: float, substitution: float) -> float:
    metrics = signal["metrics"]
    positive = (
        0.20 * metrics["pain_intensity"]
        + 0.18 * metrics["wtp_evidence"]
        + 0.12 * metrics["recurrence"]
        + 0.10 * metrics["distribution_reach"]
        + 0.10 * metrics["market_timing"]
        + 0.15 * metrics["evidence_confidence"]
        + 0.08 * portfolio_fit
        + 0.07 * substitution
    )
    return round(max(0.0, min(100.0, 10 * positive - 1.5 * metrics["competition_pressure"])), 2)


def compile_opportunity(
    signal_raw: Any,
    assets_raw: Any,
    public_portfolio_raw: Any,
    private_overlay_raw: Any | None = None,
) -> dict[str, Any]:
    signal = validate_signal(signal_raw)
    registry = validate_assets(assets_raw)
    public_portfolio = validate_public_portfolio(public_portfolio_raw)
    private_overlay = validate_private_overlay(private_overlay_raw)
    analyses, must_gaps, rights_gaps, portfolio_fit, substitution = _analyze_capabilities(
        signal, registry, public_portfolio, private_overlay
    )
    demand = _demand(signal)
    score = _opportunity_score(signal, portfolio_fit, substitution)
    blockers = []
    if signal["freshness"]["status"] != "PASS":
        blockers.append("freshness-not-pass")
    blockers.extend(f"declared:{item}" for item in signal["constraints"]["hard_blockers"])
    blockers.extend(f"rights:{item}" for item in rights_gaps)
    if blockers:
        decision = "BLOCKED"
    elif score >= 75 and demand["qualified"] and demand["direct_paid_demand"] and not must_gaps and signal["metrics"]["evidence_confidence"] >= 7:
        decision = "BUILD"
    elif score >= 60 and demand["qualified"]:
        decision = "VALIDATE"
    elif score >= 40:
        decision = "WATCH"
    else:
        decision = "REJECT"

    market_gaps = [] if demand["direct_paid_demand"] else ["No direct paid demand receipt for this product"]
    evidence_gaps = []
    if not demand["customer_origin_evidence"]:
        evidence_gaps.append("No customer-origin evidence; current evidence proves recurrence/competition only")
    if len(demand["independent_evidence_groups"]) < 2:
        evidence_gaps.append("Fewer than two qualified independent evidence groups")
    delivery_gaps = []
    if signal["constraints"]["durable_owner_state"] != "SELECTED":
        delivery_gaps.append("Durable implementation owner not selected")
    delivery_gaps.append("Hosted CI, live Git Town sync and market pilot are not exercised by compilation")

    packet: dict[str, Any] = {
        "schema_version": "opportunity-packet.v1",
        "source_identity": {
            "asset_registry_digest": digest_json(registry),
            "private_overlay_digest": digest_json(private_overlay) if private_overlay is not None else None,
            "public_portfolio_digest": digest_json(public_portfolio),
            "signal_digest": digest_json(signal),
            "signal_id": signal["id"],
        },
        "decision": decision,
        "score": {
            "competition_penalty": round(1.5 * signal["metrics"]["competition_pressure"], 2),
            "portfolio_fit_1_10": portfolio_fit,
            "score_0_100": score,
            "substitution_coverage_1_10": substitution,
        },
        "gates": {
            "blockers": sorted(blockers),
            "demand": demand,
            "freshness": signal["freshness"],
            "hard_rights_gaps": sorted(rights_gaps),
            "uncovered_must_capabilities": sorted(must_gaps),
        },
        "opportunity": {
            "id": signal["id"],
            "problem": signal["problem"],
            "target_segment": signal["target_segment"],
            "title": signal["title"],
            "wedge": signal["wedge"],
        },
        "capability_analysis": analyses,
        "gaps": {
            "delivery": delivery_gaps,
            "evidence": evidence_gaps,
            "market": market_gaps,
            "portfolio": [f"No admitted portfolio capability for {item}" for item in sorted(must_gaps)],
            "rights_privacy": [f"Required capability has only non-PASS matching assets: {item}" for item in sorted(rights_gaps)],
            "stack": [f"Uncovered must capability: {item}" for item in sorted(must_gaps)],
        },
        "mvp_experiment": {
            "budget_usd": signal["constraints"]["budget_usd"],
            "hypothesis": signal["mvp"]["hypothesis"],
            "maximum_days": signal["constraints"]["maximum_days"],
            "non_goals": signal["mvp"]["non_goals"],
            "price_test_usd_month": signal["mvp"]["price_test_usd_month"],
            "stop_loss": signal["mvp"]["stop_loss"],
            "success_metrics": signal["mvp"]["success_metrics"],
        },
        "handoff": {
            "durable_owner_state": signal["constraints"]["durable_owner_state"],
            "private_data_export": "FORBIDDEN",
            "required_next_state": "EXPERIMENT_RUNNING" if decision in {"BUILD", "VALIDATE"} else decision,
            "shared_index_owner": "convergence-leaf",
        },
        "non_claims": [
            "A compiler result is not paid demand or market validation.",
            "A PASS code license does not grant rights to unrelated models, data, trajectories, services, patents, trademarks, or third-party content.",
            "Portfolio matches are candidates until the owning runtime produces subject-bound equivalence evidence.",
            "This packet does not prove hosted CI, live Git Town synchronization, merge, ship, production safety, or Human Admit.",
        ],
    }
    packet["packet_digest"] = digest_json(packet)
    return validate_packet(packet)


def validate_packet(raw: Any) -> dict[str, Any]:
    packet = _object(raw, "opportunity_packet")
    expected = {
        "schema_version",
        "source_identity",
        "decision",
        "score",
        "gates",
        "opportunity",
        "capability_analysis",
        "gaps",
        "mvp_experiment",
        "handoff",
        "non_claims",
        "packet_digest",
    }
    _exact_keys(packet, expected, "opportunity_packet")
    if packet["schema_version"] != "opportunity-packet.v1":
        raise ValidationError("opportunity packet schema is invalid")
    if packet["decision"] not in {"BUILD", "VALIDATE", "WATCH", "REJECT", "BLOCKED"}:
        raise ValidationError("opportunity packet decision is invalid")
    digest = _text(packet["packet_digest"], "opportunity_packet.packet_digest")
    if not SHA256_ID.fullmatch(digest):
        raise ValidationError("packet_digest must be sha256:<64 hex>")
    unsigned = dict(packet)
    unsigned.pop("packet_digest")
    observed = digest_json(unsigned)
    if observed != digest:
        raise ValidationError(f"opportunity packet digest mismatch: expected {digest}, observed {observed}")
    if packet["decision"] == "BUILD" and not packet["gates"]["demand"]["direct_paid_demand"]:
        raise ValidationError("BUILD packet requires direct paid demand")
    return packet
