import streamlit as st
from utils.intelligence_engine import (
    load_all_sources, get_customer_list, build_customer_view,
    compute_health_score, classify_health, identify_risks,
    identify_opportunities, build_timeline, recommend_next_action,
)
from utils.ai_summary import generate_ai_summary

st.set_page_config(page_title="Customer Intelligence Platform", page_icon="🧭", layout="wide")

SEVERITY_COLOR = {"High": "#e5484d", "Medium": "#f5a623", "Low": "#12b76a"}
PRIORITY_COLOR = {"Urgent": "#e5484d", "High": "#f5a623", "Medium": "#3b82f6", "Low": "#12b76a"}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🧭 Customer Intel")
    st.caption("Unified view across CRM, Support, Email, Slack & Product Usage")

    sources = load_all_sources()
    customers = get_customer_list(sources)
    company_names = {c["customer_id"]: c["company"] for c in customers}

    selected_id = st.selectbox(
        "Select account",
        options=list(company_names.keys()),
        format_func=lambda cid: company_names[cid],
    )

    st.divider()
    st.subheader("⚙️ AI Settings")
    api_key = st.text_input(
        "Anthropic API key (optional)", type="password",
        help="If provided, the AI Summary is generated live by Claude. "
             "If left blank, a deterministic template summary is used instead "
             "so the app works fully without any credentials.",
    )
    st.caption("No key needed to demo — falls back to rule-based summary.")

    st.divider()
    st.caption("Data sources connected:")
    for src in ["CRM (Zoho-style)", "Support Tickets", "Emails", "Slack notes", "Product Usage"]:
        st.markdown(f"✅ {src}")

# ---------------------------------------------------------------------------
# Build the unified customer view
# ---------------------------------------------------------------------------
view = build_customer_view(selected_id, sources)
crm = view["crm"]
score, score_reasoning = compute_health_score(view)
label, emoji = classify_health(score)
risks = identify_risks(view)
opportunities = identify_opportunities(view)
timeline = build_timeline(view)
action, priority, action_reasoning = recommend_next_action(score, risks, opportunities, view)
summary_text, summary_source = generate_ai_summary(
    crm["company"], label, score, risks, opportunities, view["usage"], view["tickets"], api_key=api_key,
)

# ---------------------------------------------------------------------------
# Header / Profile
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown(f"## {crm['company']}")
    st.caption(f"{crm['industry']} · {crm['country']} · {crm['plan']} plan · Owner: {crm['owner']}")
with col2:
    st.metric("Health Score", f"{score}/100")
    st.caption(f"{emoji} {label}")
with col3:
    st.metric("MRR", f"${crm['mrr_usd']:,}")

st.markdown(
    f"""<div style="padding:10px 14px;border-radius:8px;background-color:#1e293b0d;border-left:4px solid {PRIORITY_COLOR[priority]};">
    <b>🎯 Recommended Next Best Action</b> &nbsp;
    <span style="background-color:{PRIORITY_COLOR[priority]};color:white;padding:2px 8px;border-radius:10px;font-size:0.8em;">{priority} priority</span>
    <br>{action}
    <br><i style="color:#666;font-size:0.9em;">Why: {action_reasoning}</i>
    </div>""",
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# AI Summary
# ---------------------------------------------------------------------------
badge = "🤖 Live Claude summary" if summary_source == "claude" else "📋 Template summary (no API key set)"
with st.expander(f"🧠 AI Account Summary · {badge}", expanded=True):
    st.write(summary_text)

# ---------------------------------------------------------------------------
# Risks / Opportunities
# ---------------------------------------------------------------------------
col_risk, col_opp = st.columns(2)
with col_risk:
    with st.expander(f"⚠️ Risks ({len(risks)})", expanded=True):
        if not risks:
            st.success("No active risk signals detected.")
        for r in risks:
            st.markdown(
                f"<span style='color:{SEVERITY_COLOR[r['severity']]};font-weight:600;'>● {r['severity']}</span> — "
                f"**{r['risk']}**<br><span style='color:#666;font-size:0.9em;'>{r['evidence']}</span>",
                unsafe_allow_html=True,
            )
            st.write("")

with col_opp:
    with st.expander(f"🚀 Opportunities ({len(opportunities)})", expanded=True):
        if not opportunities:
            st.info("No expansion signals detected this cycle.")
        for o in opportunities:
            st.markdown(
                f"<span style='color:#12b76a;font-weight:600;'>● {o['value']}</span> — "
                f"**{o['opportunity']}**<br><span style='color:#666;font-size:0.9em;'>{o['evidence']}</span>",
                unsafe_allow_html=True,
            )
            st.write("")

# ---------------------------------------------------------------------------
# Health score reasoning (transparency)
# ---------------------------------------------------------------------------
with st.expander("🔍 How this health score was calculated"):
    for line in score_reasoning:
        st.markdown(f"- {line}")
    st.caption("Score is fully rule-based and traceable — no black-box ML model, by design, so CSMs can trust and override it.")

# ---------------------------------------------------------------------------
# Product usage snapshot
# ---------------------------------------------------------------------------
with st.expander("📊 Product Usage Snapshot"):
    u = view["usage"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active users (30d)", u["active_users_30d"])
    m2.metric("Logins (30d)", u["logins_30d"])
    m3.metric("Feature adoption", f"{u['feature_adoption_pct']}%")
    m4.metric("Usage trend", f"{u['usage_trend_pct']:+d}%")

# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------
with st.expander(f"🕒 Recent Activity Timeline ({len(timeline)} events)", expanded=False):
    for ev in timeline:
        icon = {"Support": "🎫", "Email": "✉️", "Slack": "💬"}.get(ev["source"], "•")
        st.markdown(f"**{ev['date']}** {icon} *{ev['source']}* — {ev['detail']}")

st.divider()
st.caption("Volopay Growth Squad Assessment — Task 2 prototype · Dummy data, illustrative only.")
