"""Duck tools. All maths is done in code, not by the model, so numbers are never made up."""
from collections import defaultdict
from datetime import datetime, timezone
from .admd_client import fetch


def _period(start: str, end: str) -> dict:
    return {k: v for k, v in {"start": start, "end": end}.items() if v}


def get_workspace_summary(workspace_id: str) -> dict:
    """Get the ADMD workspace name, currency, date range and real store totals."""
    return fetch(workspace_id, "summary")


def get_orders(workspace_id: str, start: str = "", end: str = "") -> dict:
    """Get real store orders (from the client's store/CRM) with UTM fields. Dates are YYYY-MM-DD."""
    return fetch(workspace_id, "orders", _period(start, end))


def get_spend(workspace_id: str, start: str = "", end: str = "") -> dict:
    """Get ad spend and platform-claimed conversions/revenue by platform and campaign."""
    return fetch(workspace_id, "spend", _period(start, end))


def get_search_terms(workspace_id: str, start: str = "", end: str = "") -> dict:
    """Get paid search terms with campaign and campaign_type (brand / non-brand)."""
    return fetch(workspace_id, "search-terms", _period(start, end))


def check_claimed_vs_real(workspace_id: str, start: str = "", end: str = "") -> dict:
    """Compare what ad platforms claim against real ADMD orders. Returns claimed vs true CPA and ROAS per platform."""
    orders = get_orders(workspace_id, start, end)
    spend = get_spend(workspace_id, start, end)
    if "error" in orders or "error" in spend:
        return {"error": orders.get("error") or spend.get("error")}

    real = defaultdict(lambda: {"orders": 0, "revenue": 0.0})
    total_rev = 0.0
    for o in orders.get("orders", []):
        src = (o.get("utm_source") or "direct/unknown").lower()
        real[src]["orders"] += 1
        real[src]["revenue"] += float(o.get("revenue", 0))
        total_rev += float(o.get("revenue", 0))

    plat = defaultdict(lambda: {"spend": 0.0, "claimed_conversions": 0.0, "claimed_revenue": 0.0})
    for s in spend.get("rows", []):
        p = plat[(s.get("platform") or "").lower()]
        p["spend"] += float(s.get("spend", 0))
        p["claimed_conversions"] += float(s.get("claimed_conversions", 0))
        p["claimed_revenue"] += float(s.get("claimed_revenue", 0))

    rows, tot_spend, tot_claimed, tot_real = [], 0.0, 0.0, 0
    for name, p in plat.items():
        r = real.get(name, {"orders": 0, "revenue": 0.0})
        tot_spend += p["spend"]; tot_claimed += p["claimed_conversions"]; tot_real += r["orders"]
        rows.append({
            "platform": name,
            "spend": round(p["spend"], 2),
            "claimed_conversions": p["claimed_conversions"],
            "real_orders": r["orders"],
            "claimed_cpa": round(p["spend"] / p["claimed_conversions"], 2) if p["claimed_conversions"] else None,
            "true_cpa": round(p["spend"] / r["orders"], 2) if r["orders"] else None,
            "claimed_roas": round(p["claimed_revenue"] / p["spend"], 2) if p["spend"] else None,
            "true_roas": round(r["revenue"] / p["spend"], 2) if p["spend"] else None,
            "over_claim_pct": round((p["claimed_conversions"] - r["orders"]) / r["orders"] * 100, 1) if r["orders"] else None,
        })
    return {
        "platforms": rows,
        "total_platform_claimed_conversions": tot_claimed,
        "total_real_paid_orders": tot_real,
        "total_real_store_orders": len(orders.get("orders", [])),
        "blended_roas_all_revenue": round(total_rev / tot_spend, 2) if tot_spend else None,
        "note": "Blended ROAS uses ALL store revenue (incl. organic/direct). It is not paid media performance.",
    }


def check_brand_leakage(workspace_id: str, brand_terms: str, start: str = "", end: str = "") -> dict:
    """Find brand search terms (comma separated in brand_terms) appearing in non-brand campaigns."""
    terms = get_search_terms(workspace_id, start, end)
    if "error" in terms:
        return terms
    brands = [b.strip().lower() for b in brand_terms.split(",") if b.strip()]
    leaks, cost, conv = [], 0.0, 0.0
    for t in terms.get("rows", []):
        if (t.get("campaign_type") or "").lower() == "brand":
            continue
        st = (t.get("search_term") or "").lower()
        if any(b in st for b in brands):
            leaks.append(t)
            cost += float(t.get("cost", 0)); conv += float(t.get("conversions", 0))
    return {
        "leaking_terms": leaks[:25],
        "leak_count": len(leaks),
        "leak_cost": round(cost, 2),
        "leak_conversions": conv,
        "note": "These conversions make non-brand campaigns look better than they are.",
    }


PROPOSALS: list[dict] = []


def propose_action(workspace_id: str, action_type: str, target: str, detail: str, reason: str) -> dict:
    """Draft a fix (e.g. budget_shift, add_negative_keyword, pause_campaign). DRY RUN ONLY: nothing is executed. Needs human approval."""
    p = {
        "id": len(PROPOSALS) + 1,
        "workspace_id": workspace_id,
        "action_type": action_type,
        "target": target,
        "detail": detail,
        "reason": reason,
        "status": "pending_approval",
        "mode": "dry_run",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    PROPOSALS.append(p)
    return p


def approve_action(proposal_id: int) -> dict:
    """Mark a proposal approved. Dry run: logs only, never changes any ad account."""
    for p in PROPOSALS:
        if p["id"] == proposal_id:
            p["status"] = "approved_dry_run"
            return {**p, "message": "Approved in dry-run mode. No ad account was changed."}
    return {"error": f"No proposal with id {proposal_id}"}
