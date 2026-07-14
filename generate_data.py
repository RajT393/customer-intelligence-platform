"""
Generates realistic dummy data across 5 business systems for 6 customer accounts.
Run once: python generate_data.py
Writes JSON files into ./data/
"""
import json
import os
from datetime import datetime, timedelta

OUT = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT, exist_ok=True)

TODAY = datetime(2026, 7, 14)

def d(days_ago):
    return (TODAY - timedelta(days=days_ago)).strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# 1. CRM (Zoho-style account records)
# ---------------------------------------------------------------------------
crm = [
    {
        "customer_id": "CUST-001", "company": "Northwind Logistics", "industry": "Logistics",
        "plan": "Scale", "mrr_usd": 4200, "seats_licensed": 60, "seats_active": 34,
        "contract_start": "2025-01-10", "contract_end": "2026-01-10",
        "owner": "Priya Nair", "account_stage": "Renewal Risk", "country": "India"
    },
    {
        "customer_id": "CUST-002", "company": "Bluepeak Studios", "industry": "Media & Design",
        "plan": "Growth", "mrr_usd": 1800, "seats_licensed": 25, "seats_active": 23,
        "contract_start": "2025-11-02", "contract_end": "2026-11-02",
        "owner": "Arjun Mehta", "account_stage": "Healthy", "country": "Singapore"
    },
    {
        "customer_id": "CUST-003", "company": "Farro & Co", "industry": "F&B / Retail",
        "plan": "Growth", "mrr_usd": 2100, "seats_licensed": 30, "seats_active": 11,
        "contract_start": "2025-08-15", "contract_end": "2026-08-15",
        "owner": "Priya Nair", "account_stage": "At Risk", "country": "Australia"
    },
    {
        "customer_id": "CUST-004", "company": "Klarion Biotech", "industry": "Healthcare",
        "plan": "Enterprise", "mrr_usd": 9800, "seats_licensed": 140, "seats_active": 128,
        "contract_start": "2024-06-01", "contract_end": "2027-06-01",
        "owner": "Sana Iqbal", "account_stage": "Expansion Candidate", "country": "UAE"
    },
    {
        "customer_id": "CUST-005", "company": "Tidal Freight Co", "industry": "Logistics",
        "plan": "Scale", "mrr_usd": 3600, "seats_licensed": 45, "seats_active": 41,
        "contract_start": "2025-03-20", "contract_end": "2026-09-20",
        "owner": "Arjun Mehta", "account_stage": "Healthy", "country": "India"
    },
    {
        "customer_id": "CUST-006", "company": "Verdant Labs", "industry": "SaaS",
        "plan": "Growth", "mrr_usd": 1500, "seats_licensed": 20, "seats_active": 4,
        "contract_start": "2025-12-01", "contract_end": "2026-12-01",
        "owner": "Sana Iqbal", "account_stage": "Onboarding Stalled", "country": "Singapore"
    },
]

# ---------------------------------------------------------------------------
# 2. Support tickets
# ---------------------------------------------------------------------------
support_tickets = [
    {"ticket_id": "T-1042", "customer_id": "CUST-001", "date": d(4), "subject": "Card decline errors during batch payouts", "priority": "High", "status": "Open", "sentiment": "Frustrated"},
    {"ticket_id": "T-1039", "customer_id": "CUST-001", "date": d(11), "subject": "Approval workflow not routing to correct manager", "priority": "Medium", "status": "Resolved", "sentiment": "Neutral"},
    {"ticket_id": "T-1044", "customer_id": "CUST-001", "date": d(19), "subject": "Export to Tally failing for multi-currency", "priority": "High", "status": "Resolved", "sentiment": "Frustrated"},
    {"ticket_id": "T-1030", "customer_id": "CUST-002", "date": d(30), "subject": "Question about adding a new department budget", "priority": "Low", "status": "Resolved", "sentiment": "Positive"},
    {"ticket_id": "T-1051", "customer_id": "CUST-003", "date": d(2), "subject": "Unable to reconcile May invoices, third escalation", "priority": "High", "status": "Open", "sentiment": "Frustrated"},
    {"ticket_id": "T-1048", "customer_id": "CUST-003", "date": d(9), "subject": "Reconciliation mismatch in expense report", "priority": "High", "status": "Resolved", "sentiment": "Frustrated"},
    {"ticket_id": "T-1046", "customer_id": "CUST-003", "date": d(16), "subject": "Card not delivered to new hire", "priority": "Medium", "status": "Resolved", "sentiment": "Neutral"},
    {"ticket_id": "T-1020", "customer_id": "CUST-004", "date": d(25), "subject": "Interested in API access for custom reporting", "priority": "Low", "status": "Resolved", "sentiment": "Positive"},
    {"ticket_id": "T-1005", "customer_id": "CUST-005", "date": d(45), "subject": "Bulk upload template question", "priority": "Low", "status": "Resolved", "sentiment": "Positive"},
    {"ticket_id": "T-1053", "customer_id": "CUST-006", "date": d(1), "subject": "How do I add my finance team as users?", "priority": "Medium", "status": "Open", "sentiment": "Neutral"},
]

# ---------------------------------------------------------------------------
# 3. Emails (customer-facing thread summaries)
# ---------------------------------------------------------------------------
emails = [
    {"email_id": "E-501", "customer_id": "CUST-001", "date": d(6), "subject": "Re: Contract renewal terms", "snippet": "We're evaluating two other vendors before renewal. Need to see the payout issue resolved first.", "sentiment": "Negative"},
    {"email_id": "E-495", "customer_id": "CUST-001", "date": d(20), "subject": "Q3 usage review", "snippet": "Finance team flagged that only half our licensed seats are being used.", "sentiment": "Neutral"},
    {"email_id": "E-480", "customer_id": "CUST-002", "date": d(12), "subject": "Loved the new approval mobile flow", "snippet": "Our AP lead specifically called out how much faster approvals are now.", "sentiment": "Positive"},
    {"email_id": "E-510", "customer_id": "CUST-003", "date": d(3), "subject": "Escalation: still unresolved after 3 tickets", "snippet": "This is our third message on the same reconciliation issue. Considering downgrade if unresolved by month end.", "sentiment": "Negative"},
    {"email_id": "E-470", "customer_id": "CUST-004", "date": d(14), "subject": "Multi-entity rollout for APAC subsidiaries", "snippet": "Leadership wants to expand to 3 new entities in Q3, asking about enterprise multi-entity pricing.", "sentiment": "Positive"},
    {"email_id": "E-460", "customer_id": "CUST-005", "date": d(28), "subject": "Great quarter", "snippet": "Smooth quarter, no major issues, happy with support responsiveness.", "sentiment": "Positive"},
    {"email_id": "E-515", "customer_id": "CUST-006", "date": d(5), "subject": "Following up on onboarding", "snippet": "We've been slow to roll this out internally, still only using it for one team.", "sentiment": "Neutral"},
]

# ---------------------------------------------------------------------------
# 4. Slack messages (internal team notes / customer channel mirrors)
# ---------------------------------------------------------------------------
slack_messages = [
    {"message_id": "S-201", "customer_id": "CUST-001", "date": d(5), "channel": "#csm-northwind", "author": "Priya Nair", "message": "Payout decline bug is a big deal for them, ops team is manually processing payouts as workaround. Renewal is in 6 months and they're already shopping around."},
    {"message_id": "S-198", "customer_id": "CUST-001", "date": d(22), "channel": "#csm-northwind", "author": "Priya Nair", "message": "Seat utilization is only 57%. Worth a QBR to understand if scope changed or if it's an adoption problem."},
    {"message_id": "S-215", "customer_id": "CUST-002", "date": d(10), "channel": "#csm-bluepeak", "author": "Arjun Mehta", "message": "Bluepeak's finance lead mentioned in passing they might add their new LA office to the account next year."},
    {"message_id": "S-220", "customer_id": "CUST-003", "date": d(2), "channel": "#csm-farro", "author": "Priya Nair", "message": "Third reconciliation ticket in a month from Farro. This is becoming a trust issue, not just a bug. Need eng escalation today."},
    {"message_id": "S-190", "customer_id": "CUST-004", "date": d(13), "channel": "#csm-klarion", "author": "Sana Iqbal", "message": "Klarion CFO confirmed multi-entity expansion budget approved internally, just waiting on our pricing proposal."},
    {"message_id": "S-225", "customer_id": "CUST-006", "date": d(4), "channel": "#csm-verdant", "author": "Sana Iqbal", "message": "Verdant onboarding stalled at week 6. Only 4 of 20 seats activated. Champion (ops lead) may have left the company, no response to last 2 outreach attempts."},
]

# ---------------------------------------------------------------------------
# 5. Product usage (aggregated snapshot, last 30 days)
# ---------------------------------------------------------------------------
product_usage = [
    {"customer_id": "CUST-001", "active_users_30d": 34, "logins_30d": 210, "feature_adoption_pct": 48, "transactions_30d": 890, "usage_trend_pct": -18},
    {"customer_id": "CUST-002", "active_users_30d": 23, "logins_30d": 340, "feature_adoption_pct": 81, "transactions_30d": 1220, "usage_trend_pct": 12},
    {"customer_id": "CUST-003", "active_users_30d": 11, "logins_30d": 60, "feature_adoption_pct": 29, "transactions_30d": 340, "usage_trend_pct": -34},
    {"customer_id": "CUST-004", "active_users_30d": 128, "logins_30d": 1890, "feature_adoption_pct": 74, "transactions_30d": 6100, "usage_trend_pct": 22},
    {"customer_id": "CUST-005", "active_users_30d": 41, "logins_30d": 480, "feature_adoption_pct": 68, "transactions_30d": 1510, "usage_trend_pct": 6},
    {"customer_id": "CUST-006", "active_users_30d": 4, "logins_30d": 15, "feature_adoption_pct": 9, "transactions_30d": 22, "usage_trend_pct": -40},
]

data = {
    "crm.json": crm,
    "support_tickets.json": support_tickets,
    "emails.json": emails,
    "slack_messages.json": slack_messages,
    "product_usage.json": product_usage,
}

for fname, payload in data.items():
    with open(os.path.join(OUT, fname), "w") as f:
        json.dump(payload, f, indent=2)

print(f"Wrote {len(data)} data files to {OUT}")
