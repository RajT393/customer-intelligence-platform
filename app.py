import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from utils.intelligence_engine import (
    load_all_sources, get_customer_list, build_customer_view,
    compute_health_score, classify_health, identify_risks,
    identify_opportunities, build_timeline, recommend_next_action,
)
from utils.ai_summary import generate_ai_summary

st.set_page_config(page_title="Customer Intelligence", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #202124;
    }
    
    /* Main App Background */
    .stApp {
        background-color: #F7F6F4;
    }
    
    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #F2F1EE !important;
        border-right: 1px solid #E8E6E2;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Typography Scale */
    .h1-title { font-size: 48px; font-weight: 700; color: #202124; margin-bottom: 8px; line-height: 1.2; letter-spacing: -1px; }
    .h2-title { font-size: 22px; font-weight: 600; color: #202124; margin-bottom: 24px; letter-spacing: -0.5px; }
    .card-title { font-size: 16px; font-weight: 500; color: #6B7280; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .metric-val { font-size: 34px; font-weight: 600; color: #202124; margin-bottom: 4px; letter-spacing: -1px; }
    .body-text { font-size: 15px; color: #202124; line-height: 1.6; }
    .metadata { font-size: 13px; color: #6B7280; margin-top: 8px; display: flex; align-items: center; gap: 4px; }
    
    /* Cards */
    .dashboard-card {
        background: #FFFFFF;
        border: 1px solid #E8E6E2;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,.04);
        height: 100%;
    }
    
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E8E6E2;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,.04);
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }
    
    /* Badge */
    .badge-critical { background: #FEF2F2; color: #B91C1C; padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 600; border: 1px solid #FEE2E2;}
    .badge-warning { background: #FFFBEB; color: #C05621; padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 600; border: 1px solid #FEF3C7;}
    .badge-success { background: #F0FDF4; color: #2F855A; padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 600; border: 1px solid #DCFCE7;}
    .badge-info { background: #F3F4F6; color: #374151; padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 600; border: 1px solid #E5E7EB;}
    
    /* Meta Row */
    .meta-row {
        display: flex;
        gap: 32px;
        align-items: center;
        margin-bottom: 48px;
        border-bottom: 1px solid #E8E6E2;
        padding-bottom: 32px;
        flex-wrap: wrap;
    }
    .meta-item {
        display: flex;
        flex-direction: column;
    }
    .meta-label { font-size: 13px; color: #9CA3AF; font-weight: 500; margin-bottom: 6px; }
    .meta-value { font-size: 15px; color: #202124; font-weight: 500; }
    
    /* Alert Card */
    .alert-card {
        background: #FFFFFF;
        border: 1px solid #FCA5A5;
        border-left: 4px solid #B91C1C;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 4px 12px rgba(185,28,28,.06);
    }
    
    /* Timeline */
    .timeline-container { position: relative; padding-left: 24px; margin-top: 16px; }
    .timeline-container::before {
        content: ''; position: absolute; left: 0; top: 8px; bottom: 0; width: 2px; background: #E8E6E2;
    }
    .timeline-item { position: relative; margin-bottom: 32px; }
    .timeline-item::before {
        content: ''; position: absolute; left: -28.5px; top: 4px; width: 11px; height: 11px; border-radius: 50%; background: #FFFFFF; border: 2px solid #6B7280;
    }
    .timeline-date { font-size: 12px; color: #9CA3AF; font-weight: 600; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
    .timeline-content { font-size: 15px; color: #202124; }
    
    /* Buttons */
    .primary-btn {
        background: #202124; color: #FFFFFF !important; border: none; border-radius: 8px; padding: 0 16px; font-size: 14px; font-weight: 500; cursor: pointer; height: 40px; display: inline-flex; align-items: center; justify-content: center; text-decoration: none; transition: background 0.15s;
    }
    .primary-btn:hover { background: #374151; }
    
    /* Sidebar Navigation */
    .sidebar-logo { font-size: 16px; font-weight: 600; color: #202124; display: flex; align-items: center; gap: 12px; margin-bottom: 48px; padding: 0 12px; }
    .sidebar-section { font-size: 12px; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; padding: 0 12px; margin-top: 32px;}
    a.nav-item {
        display: flex; align-items: center; gap: 12px; padding: 10px 12px; color: #6B7280 !important; font-size: 15px; font-weight: 500; border-radius: 8px; margin-bottom: 4px; cursor: pointer; transition: all 0.15s; text-decoration: none;
    }
    a.nav-item.active, a.nav-item:hover { background: #E8E6E2; color: #202124 !important; }
    
    /* Exec Summary Format */
    .exec-summary p { margin-bottom: 16px; font-size: 15px; line-height: 1.6; color: #202124; }
    .exec-summary strong { color: #202124; font-weight: 600; }
    
</style>
""", unsafe_allow_html=True)

# SVG Icons
ICONS = {
    "building": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>',
    "activity": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
    "users": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
    "calendar": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
    "alert": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "trending-down": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>',
    "trending-up": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>',
    "settings": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
    "sparkles": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"></path></svg>',
    "dollar": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
    "briefcase": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>',
    "target": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>',
    "message": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>'
}

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
sources = load_all_sources()
customers = get_customer_list(sources)
company_names = {c["customer_id"]: c["company"] for c in customers}

# ---------------------------------------------------------------------------
# Sidebar Redesign
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f'<div class="sidebar-logo">{ICONS["target"]} Customer Intelligence</div>', unsafe_allow_html=True)
    
    selected_id = st.selectbox("Workspace Account", options=list(company_names.keys()), format_func=lambda cid: company_names[cid], label_visibility="collapsed")
    
    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)
    st.markdown(f'<a href="#overview" class="nav-item active">{ICONS["activity"]} Overview</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="#overview" class="nav-item">{ICONS["building"]} Accounts</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="#timeline" class="nav-item">{ICONS["calendar"]} Timeline</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="#analytics" class="nav-item">{ICONS["message"]} Support</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="#analytics" class="nav-item">{ICONS["users"]} Usage</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="#overview" class="nav-item">{ICONS["dollar"]} Renewals</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="#ai-insights" class="nav-item">{ICONS["sparkles"]} AI Insights</a>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">System</div>', unsafe_allow_html=True)
    st.markdown(f'<a href="#" class="nav-item">{ICONS["settings"]} Settings</a>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter key for live AI", label_visibility="collapsed")

# ---------------------------------------------------------------------------
# Business Logic
# ---------------------------------------------------------------------------
view = build_customer_view(selected_id, sources)
crm = view["crm"]
score, score_reasoning = compute_health_score(view)
label, _ = classify_health(score)
risks = identify_risks(view)
opportunities = identify_opportunities(view)
timeline = build_timeline(view)
action, priority, action_reasoning = recommend_next_action(score, risks, opportunities, view)
summary_text, summary_source = generate_ai_summary(
    crm["company"], label, score, risks, opportunities, view["usage"], view["tickets"], api_key=api_key,
)

# ---------------------------------------------------------------------------
# Main Content Layout
# ---------------------------------------------------------------------------
# 1. Header Row
st.markdown(f'<div id="overview" class="h1-title" style="padding-top: 16px;">{crm["company"]}</div>', unsafe_allow_html=True)

meta_html = f"""
<div class="meta-row">
    <div class="meta-item"><span class="meta-label">Industry</span><span class="meta-value">{crm['industry']}</span></div>
    <div class="meta-item"><span class="meta-label">Region</span><span class="meta-value">{crm['country']}</span></div>
    <div class="meta-item"><span class="meta-label">Subscription Plan</span><span class="meta-value">{crm['plan']}</span></div>
    <div class="meta-item"><span class="meta-label">Owner</span><span class="meta-value">{crm['owner']}</span></div>
    <div class="meta-item"><span class="meta-label">Customer Since</span><span class="meta-value">{crm['contract_start']}</span></div>
    <div class="meta-item"><span class="meta-label">Renewal Date</span><span class="meta-value">{crm['contract_end']}</span></div>
    <div class="meta-item"><span class="meta-label">Last Synced</span><span class="meta-value">Just now</span></div>
</div>
"""
st.markdown(meta_html, unsafe_allow_html=True)

# 2. KPI Grid (4 columns)
kpi_cols = st.columns(4)

# Health Score
badge_class = "badge-success" if score >= 70 else "badge-warning" if score >= 45 else "badge-critical"
trend_icon = ICONS["trending-up"] if score >= 70 else ICONS["trending-down"]
trend_color = "#2F855A" if score >= 70 else "#B91C1C"
with kpi_cols[0]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="card-title">{ICONS["activity"]} Health Score</div>
        <div class="metric-val">{score}</div>
        <div class="metadata" style="color:{trend_color};">{trend_icon} <span class="{badge_class}">{label}</span> &nbsp; <span style="color:#9CA3AF;">Current rating</span></div>
    </div>
    """, unsafe_allow_html=True)

# MRR
with kpi_cols[1]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="card-title">{ICONS["dollar"]} Monthly Recurring Revenue</div>
        <div class="metric-val">${crm['mrr_usd']:,}</div>
        <div class="metadata" style="color:#2F855A;">{ICONS["trending-up"]} Stable &nbsp; <span style="color:#9CA3AF;">Since contract start</span></div>
    </div>
    """, unsafe_allow_html=True)

# Renewal
days_to_renewal = (datetime.strptime(crm["contract_end"], "%Y-%m-%d") - datetime(2026, 7, 14)).days
renewal_color = "#B91C1C" if days_to_renewal < 90 else "#374151"
with kpi_cols[2]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="card-title">{ICONS["calendar"]} Days to Renewal</div>
        <div class="metric-val">{days_to_renewal}</div>
        <div class="metadata" style="color:{renewal_color};">Next cycle: {crm['contract_end']}</div>
    </div>
    """, unsafe_allow_html=True)

# Usage Trend
usage_trend = view["usage"]["usage_trend_pct"]
ut_icon = ICONS["trending-up"] if usage_trend >= 0 else ICONS["trending-down"]
ut_color = "#2F855A" if usage_trend >= 0 else "#B91C1C"
with kpi_cols[3]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="card-title">{ICONS["users"]} 30d Usage Trend</div>
        <div class="metric-val">{usage_trend:+} %</div>
        <div class="metadata" style="color:{ut_color};">{ut_icon} {view['usage']['active_users_30d']} active users</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3. AI Recommendation Alert Card
st.markdown('<div id="ai-insights" class="h2-title" style="padding-top: 24px;">Recommended Action</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="alert-card">
    <div class="alert-header">
        {ICONS["alert"]}
        <span class="card-title" style="margin-bottom:0; font-size:18px; color:#B91C1C; font-weight:600;">Action Required</span>
        <span class="badge-critical">{priority} Priority</span>
    </div>
    <div class="body-text" style="font-size: 16px; margin-bottom: 12px; font-weight: 500;">
        {action}
    </div>
    <div class="body-text" style="color: #6B7280; margin-bottom: 24px;">
        <strong>Why this matters:</strong> {action_reasoning}
    </div>
    <div style="display:flex; gap:16px;">
        <a href="#" class="primary-btn">Schedule Executive Review</a>
        <a href="#" class="primary-btn" style="background:#FFFFFF; color:#202124!important; border:1px solid #E8E6E2;">Notify Account Owner</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. Two-Column Layout: Executive Summary & Timeline
col_exec, col_time = st.columns([6, 6], gap="large")

with col_exec:
    st.markdown('<div class="h2-title">Executive Briefing</div>', unsafe_allow_html=True)
    
    # Parse basic markdown to HTML so it renders correctly inside the custom div
    html_summary = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', summary_text)
    html_summary = html_summary.replace('\n', '<br>')
    
    st.markdown(f"""
    <div class="dashboard-card exec-summary">
        <div class="card-title" style="margin-bottom: 24px;">{ICONS["sparkles"]} AI Generated Summary ({summary_source})</div>
        <p>{html_summary}</p>
    </div>
    """, unsafe_allow_html=True)

with col_time:
    st.markdown('<div id="timeline" class="h2-title" style="padding-top: 24px;">Customer Timeline</div>', unsafe_allow_html=True)
    
    timeline_html = '<div class="dashboard-card"><div class="timeline-container">'
    for i, ev in enumerate(timeline[:5]): # Show top 5
        date_str = ev['date']
        # Convert date to relative time for realistic dashboard feel
        days_ago = (datetime(2026, 7, 14) - datetime.strptime(date_str, "%Y-%m-%d")).days
        if days_ago == 0: relative = "Today"
        elif days_ago == 1: relative = "Yesterday"
        else: relative = f"{days_ago} days ago"
        
        timeline_html += f'<div class="timeline-item"><div class="timeline-date">{relative} &nbsp;·&nbsp; {ev["source"]}</div><div class="timeline-content">{ev["detail"]}</div></div>'
    timeline_html += '</div></div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# 5. Charts Section
st.markdown('<div id="analytics" class="h2-title" style="padding-top: 24px;">Analytics</div>', unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2, gap="large")

# Dummy data for charts based on aggregate stats
dates = pd.date_range(end=datetime(2026, 7, 14), periods=30)
np.random.seed(len(crm['company'])) # deterministic per company
base_usage = view["usage"]["logins_30d"] / 30
usage_data = base_usage + np.random.normal(0, base_usage*0.2, 30)
# apply trend
trend_factor = np.linspace(1, 1 + (view["usage"]["usage_trend_pct"]/100), 30)
usage_data = usage_data * trend_factor
df_usage = pd.DataFrame({'Logins': usage_data}, index=dates)

with col_chart1:
    st.markdown("""
    <div class="dashboard-card" style="padding-bottom: 0;">
        <div class="card-title">Product Usage Trend (30 Days)</div>
    </div>
    """, unsafe_allow_html=True)
    st.line_chart(df_usage, color=["#2F855A"], height=250)

# Ticket volume dummy data
tickets_data = np.random.poisson(lam=len(view["tickets"])/30, size=30)
df_tickets = pd.DataFrame({'Tickets': tickets_data}, index=dates)

with col_chart2:
    st.markdown("""
    <div class="dashboard-card" style="padding-bottom: 0;">
        <div class="card-title">Support Ticket Volume</div>
    </div>
    """, unsafe_allow_html=True)
    st.bar_chart(df_tickets, color=["#374151"], height=250)
