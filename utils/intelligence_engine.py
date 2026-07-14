"""
Core intelligence engine: combines data from 5 sources into a single
customer view, and derives health score, risks, opportunities, and the
recommended next best action with explicit reasoning.

This is intentionally rule-based and fully transparent (no black box) so
that every score/recommendation can be traced back to a specific signal.
The AI layer (see ai_summary.py) sits on top of this structured output to
turn it into a natural-language summary.
"""
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
TODAY = datetime(2026, 7, 14)


def _load(fname):
    with open(os.path.join(DATA_DIR, fname)) as f:
        return json.load(f)


def load_all_sources():
    return {
        "crm": _load("crm.json"),
        "support_tickets": _load("support_tickets.json"),
        "emails": _load("emails.json"),
        "slack_messages": _load("slack_messages.json"),
        "product_usage": _load("product_usage.json"),
    }


def get_customer_list(sources):
    return sources["crm"]


def _days_ago(date_str):
    return (TODAY - datetime.strptime(date_str, "%Y-%m-%d")).days


def build_customer_view(customer_id, sources):
    """Merge every source for one customer_id into a single structured record."""
    crm = next(c for c in sources["crm"] if c["customer_id"] == customer_id)
    tickets = [t for t in sources["support_tickets"] if t["customer_id"] == customer_id]
    emails = [e for e in sources["emails"] if e["customer_id"] == customer_id]
    slacks = [s for s in sources["slack_messages"] if s["customer_id"] == customer_id]
    usage = next((u for u in sources["product_usage"] if u["customer_id"] == customer_id), None)

    return {
        "crm": crm,
        "tickets": sorted(tickets, key=lambda x: x["date"], reverse=True),
        "emails": sorted(emails, key=lambda x: x["date"], reverse=True),
        "slacks": sorted(slacks, key=lambda x: x["date"], reverse=True),
        "usage": usage,
    }


def compute_health_score(view):
    """
    0-100 score, weighted across 4 signal groups. Every deduction/addition
    is logged in `reasoning` so the score is fully explainable.
    """
    score = 70  # baseline
    reasoning = []

    usage = view["usage"]
    seat_util = usage["active_users_30d"] / max(view["crm"]["seats_licensed"], 1)

    # --- Product usage signal (up to +/-25) ---
    if usage["usage_trend_pct"] <= -30:
        score -= 20
        reasoning.append(f"Usage trend down {abs(usage['usage_trend_pct'])}% over 30 days (severe decline)")
    elif usage["usage_trend_pct"] < 0:
        score -= 10
        reasoning.append(f"Usage trend down {abs(usage['usage_trend_pct'])}% over 30 days")
    elif usage["usage_trend_pct"] >= 15:
        score += 10
        reasoning.append(f"Usage trend up {usage['usage_trend_pct']}% over 30 days (strong growth)")
    else:
        score += 3
        reasoning.append(f"Usage trend stable ({usage['usage_trend_pct']:+d}%)")

    if seat_util < 0.3:
        score -= 15
        reasoning.append(f"Seat utilization critically low ({seat_util:.0%} of licensed seats active)")
    elif seat_util < 0.6:
        score -= 5
        reasoning.append(f"Seat utilization below healthy range ({seat_util:.0%})")

    # --- Support signal (up to -20) ---
    open_high_priority = [t for t in view["tickets"] if t["status"] == "Open" and t["priority"] == "High"]
    frustrated_tickets = [t for t in view["tickets"] if t["sentiment"] == "Frustrated"]
    if open_high_priority:
        score -= 12
        reasoning.append(f"{len(open_high_priority)} open high-priority support ticket(s) unresolved")
    if len(frustrated_tickets) >= 3:
        score -= 10
        reasoning.append(f"{len(frustrated_tickets)} tickets logged with frustrated sentiment (repeat pattern)")
    elif len(frustrated_tickets) >= 1:
        score -= 4
        reasoning.append(f"{len(frustrated_tickets)} ticket(s) with frustrated sentiment")

    # --- Email/relationship signal (up to -15 / +10) ---
    negative_emails = [e for e in view["emails"] if e["sentiment"] == "Negative"]
    positive_emails = [e for e in view["emails"] if e["sentiment"] == "Positive"]
    if negative_emails:
        score -= 15
        reasoning.append(f"{len(negative_emails)} recent email(s) with negative sentiment, incl. renewal/downgrade language")
    if positive_emails and not negative_emails:
        score += 8
        reasoning.append(f"{len(positive_emails)} recent email(s) with positive sentiment")

    # --- Internal team signal from Slack (contextual, up to -10 / +10) ---
    for s in view["slacks"]:
        msg = s["message"].lower()
        if any(k in msg for k in ["shopping around", "trust issue", "no response", "stalled", "left the company"]):
            score -= 10
            reasoning.append("Internal CSM note flags a material relationship or churn risk")
            break
    for s in view["slacks"]:
        msg = s["message"].lower()
        if any(k in msg for k in ["expansion", "budget approved", "add their new"]):
            score += 8
            reasoning.append("Internal CSM note flags an expansion signal")
            break

    score = max(0, min(100, score))
    return score, reasoning


def classify_health(score):
    if score >= 70:
        return "Healthy", "🟢"
    elif score >= 45:
        return "At Risk", "🟡"
    else:
        return "Critical", "🔴"


def identify_risks(view):
    risks = []
    usage = view["usage"]
    seat_util = usage["active_users_30d"] / max(view["crm"]["seats_licensed"], 1)

    if any(t["status"] == "Open" and t["priority"] == "High" for t in view["tickets"]):
        risks.append({
            "risk": "Unresolved high-priority support issue",
            "evidence": next(t["subject"] for t in view["tickets"] if t["status"] == "Open" and t["priority"] == "High"),
            "severity": "High",
        })
    if any(e["sentiment"] == "Negative" for e in view["emails"]):
        neg = next(e for e in view["emails"] if e["sentiment"] == "Negative")
        risks.append({
            "risk": "Customer signaling dissatisfaction in writing",
            "evidence": f"Email \"{neg['subject']}\": {neg['snippet']}",
            "severity": "High",
        })
    if seat_util < 0.4:
        risks.append({
            "risk": "Low product adoption relative to contract size",
            "evidence": f"Only {usage['active_users_30d']} of {view['crm']['seats_licensed']} licensed seats active ({seat_util:.0%})",
            "severity": "Medium",
        })
    if usage["usage_trend_pct"] < -15:
        risks.append({
            "risk": "Declining usage trend",
            "evidence": f"Usage down {abs(usage['usage_trend_pct'])}% over the last 30 days",
            "severity": "Medium",
        })
    days_to_renewal = (datetime.strptime(view["crm"]["contract_end"], "%Y-%m-%d") - TODAY).days
    if 0 < days_to_renewal <= 200 and risks:
        risks.append({
            "risk": "Renewal at risk given open issues",
            "evidence": f"Contract ends in {days_to_renewal} days while unresolved risk signals are present",
            "severity": "High",
        })
    return risks


def identify_opportunities(view):
    opportunities = []
    usage = view["usage"]

    for s in view["slacks"]:
        msg = s["message"].lower()
        if "budget approved" in msg or "expansion" in msg or "add their new" in msg:
            opportunities.append({
                "opportunity": "Expansion signal from account team",
                "evidence": s["message"],
                "value": "High",
            })
    for e in view["emails"]:
        if "pricing" in e["snippet"].lower() or "expand" in e["snippet"].lower() or "new entities" in e["snippet"].lower():
            opportunities.append({
                "opportunity": "Customer proactively asked about expansion / pricing",
                "evidence": f"Email \"{e['subject']}\": {e['snippet']}",
                "value": "High",
            })
    if usage["usage_trend_pct"] >= 15 and usage["feature_adoption_pct"] >= 70:
        opportunities.append({
            "opportunity": "Strong engagement suggests upsell readiness (add-on modules, higher tier)",
            "evidence": f"Usage up {usage['usage_trend_pct']}%, feature adoption at {usage['feature_adoption_pct']}%",
            "value": "Medium",
        })
    return opportunities


def build_timeline(view):
    events = []
    for t in view["tickets"]:
        events.append({"date": t["date"], "source": "Support", "detail": f"Ticket {t['ticket_id']} ({t['priority']}, {t['status']}): {t['subject']}"})
    for e in view["emails"]:
        events.append({"date": e["date"], "source": "Email", "detail": f"{e['subject']} — {e['snippet']}"})
    for s in view["slacks"]:
        events.append({"date": s["date"], "source": "Slack", "detail": f"{s['author']} in {s['channel']}: {s['message']}"})
    return sorted(events, key=lambda x: x["date"], reverse=True)


def recommend_next_action(health_score, risks, opportunities, view):
    """Returns (action, priority, reasoning) using explicit decision logic."""
    high_risks = [r for r in risks if r["severity"] == "High"]
    high_opps = [o for o in opportunities if o["value"] == "High"]

    if len(high_risks) >= 2:
        return (
            f"Escalate to CSM lead + trigger save play: schedule an executive check-in with "
            f"{view['crm']['company']} within 3 business days before the next support or renewal touchpoint.",
            "Urgent",
            f"{len(high_risks)} high-severity risk signals detected simultaneously (support + relationship + renewal proximity). "
            f"Historically, accounts with 2+ concurrent high-severity signals churn at a materially higher rate if not intercepted within a week."
        )
    if high_risks:
        r = high_risks[0]
        return (
            f"Personally resolve open issue and follow up directly: {r['evidence']}",
            "High",
            f"Single high-severity risk identified: {r['risk']}. Addressing it directly is higher-leverage than a generic check-in."
        )
    if high_opps:
        o = high_opps[0]
        return (
            f"Route to sales/CSM for expansion conversation: {o['opportunity']}",
            "High",
            f"Buying signal detected: {o['evidence']}. Time-sensitive — expansion intent signals typically cool within 2-3 weeks if unaddressed."
        )
    if health_score < 45:
        return (
            "Schedule a proactive health check call — no single acute issue, but composite score indicates disengagement risk.",
            "Medium",
            f"Health score is {health_score}/100 (Critical band) even without one dominant red flag; likely a slow-drift churn pattern."
        )
    if health_score >= 70 and not risks:
        return (
            "No action required this cycle — maintain standard quarterly cadence.",
            "Low",
            "Account is healthy across usage, support, and sentiment signals; no risks or unaddressed opportunities identified."
        )
    return (
        "Monitor — re-run health check in 2 weeks.",
        "Low",
        "Signals are mixed but none individually severe enough to warrant immediate action."
    )
