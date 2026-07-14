"""
AI summarization layer.

If an Anthropic API key is provided (via Streamlit sidebar / env var), this
calls Claude to turn the structured customer view into a natural-language
account summary. If no key is provided, it falls back to a deterministic
template summary built from the same structured signals, so the app is
fully functional and demo-able without any credentials.
"""
import os


def _fallback_summary(company, health_label, score, risks, opportunities, usage, tickets):
    lines = [f"{company} is currently rated **{health_label}** ({score}/100)."]

    if risks:
        top = risks[0]
        lines.append(f"The most pressing concern is {top['risk'].lower()} — {top['evidence']}.")
    if opportunities:
        top_o = opportunities[0]
        lines.append(f"On the upside, there's a live opportunity: {top_o['opportunity'].lower()}.")

    open_tix = [t for t in tickets if t["status"] == "Open"]
    if open_tix:
        lines.append(f"{len(open_tix)} support ticket(s) currently open, including \"{open_tix[0]['subject']}\".")

    lines.append(
        f"Seat utilization is {usage['active_users_30d']} active of the licensed total, "
        f"with usage trending {usage['usage_trend_pct']:+d}% over the last 30 days."
    )
    if not risks and not opportunities:
        lines.append("No urgent signals in either direction this cycle — account is tracking normally.")

    return " ".join(lines)


def generate_ai_summary(company, health_label, score, risks, opportunities, usage, tickets, api_key=None):
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        return _fallback_summary(company, health_label, score, risks, opportunities, usage, tickets), "template"

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        risk_text = "\n".join(f"- {r['risk']}: {r['evidence']}" for r in risks) or "None identified."
        opp_text = "\n".join(f"- {o['opportunity']}: {o['evidence']}" for o in opportunities) or "None identified."

        prompt = f"""You are a customer success analyst. Write a concise 3-4 sentence account summary for an internal CSM/sales dashboard. Be direct and specific, no filler, no marketing tone.

Company: {company}
Health score: {score}/100 ({health_label})
Seat utilization: {usage['active_users_30d']} active of licensed seats
Usage trend (30d): {usage['usage_trend_pct']:+d}%

Risks:
{risk_text}

Opportunities:
{opp_text}

Write the summary now, plain prose, no headers or bullet points."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))
        return text.strip(), "claude"
    except Exception as e:
        # Never let a missing/invalid key or network issue break the demo
        return _fallback_summary(company, health_label, score, risks, opportunities, usage, tickets), f"template (API error: {e})"
