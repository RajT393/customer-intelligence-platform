"""
AI summarization layer.

If a Gemini API key is provided (via Streamlit sidebar / env var), this
calls Gemini to turn the structured customer view into a natural-language
account summary. If no key is provided, it falls back to a deterministic
template summary built from the same structured signals, so the app is
fully functional and demo-able without any credentials.
"""
import os


def _fallback_summary(company, health_label, score, risks, opportunities, usage, tickets):
    top_risk = risks[0] if risks else None
    
    status = f"**Current Status:** {company} is currently rated {health_label} ({score}/100)."
    
    primary_risk = "**Primary Risk:** "
    if top_risk:
        primary_risk += f"{top_risk['risk']}."
    else:
        primary_risk += "No immediate risks identified."
        
    supporting_signals = "**Supporting Signals:** "
    if top_risk:
        supporting_signals += f"{top_risk['evidence']} "
    
    open_tix = [t for t in tickets if t["status"] == "Open"]
    if open_tix:
        supporting_signals += f"{len(open_tix)} open support ticket(s)."
        
    supporting_signals += f" Seat utilization at {usage['active_users_30d']} active, usage trend {usage['usage_trend_pct']:+d}%."
    
    impact = "**Business Impact:** "
    if health_label == "Critical":
        impact += "High risk of churn if unaddressed."
    elif top_risk:
        impact += "Potential friction during next renewal or expansion cycle."
    else:
        impact += "Account is stable and positioned for continued growth."
        
    recommended_step = "**Recommended Next Step:** "
    if top_risk:
        recommended_step += "Engage directly with the customer to address the primary risk."
    else:
        recommended_step += "Maintain current engagement cadence."

    return f"{status}\n\n{primary_risk}\n\n{supporting_signals}\n\n{impact}\n\n{recommended_step}"


def generate_ai_summary(company, health_label, score, risks, opportunities, usage, tickets, api_key=None):
    api_key = api_key or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return _fallback_summary(company, health_label, score, risks, opportunities, usage, tickets), "template"

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        risk_text = "\n".join(f"- {r['risk']}: {r['evidence']}" for r in risks) or "None identified."
        opp_text = "\n".join(f"- {o['opportunity']}: {o['evidence']}" for o in opportunities) or "None identified."

        prompt = f"""You are a customer success analyst preparing an executive briefing for an internal CSM/sales dashboard.
Format your response exactly using these bold headers:
**Current Status:**
**Primary Risk:**
**Supporting Signals:**
**Business Impact:**
**Recommended Next Step:**

Company: {company}
Health score: {score}/100 ({health_label})
Seat utilization: {usage['active_users_30d']} active of licensed seats
Usage trend (30d): {usage['usage_trend_pct']:+d}%

Risks:
{risk_text}

Opportunities:
{opp_text}

Write the briefing now. Be highly professional, data-driven, and concise. No conversational filler, no emojis, no AI tone."""

        response = model.generate_content(prompt)
        text = response.text
        return text.strip(), "gemini"
    except Exception as e:
        # Never let a missing/invalid key or network issue break the demo
        return _fallback_summary(company, health_label, score, risks, opportunities, usage, tickets), f"template (API error: {e})"
