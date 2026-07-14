# Customer Intelligence Platform

Built for Volopay Growth Squad Assessment — Task 2.

A single account view that merges signals from **5 systems** — CRM, Support
Tickets, Email, Slack (internal CSM notes), and Product Usage — into a
health score, risk/opportunity breakdown, activity timeline, and a
recommended next best action with explicit reasoning.

## Why this design

Customer risk rarely shows up in one system. A renewal risk usually looks
like: a support ticket (product problem) + an email (customer says so
explicitly) + a Slack note (CSM already knows, hasn't escalated) + a usage
dip (behavior confirms it). Looking at any single source misses the
pattern. This tool's only real job is correlating those four things into
one view a CSM can act on in 30 seconds instead of five tabs.

## What it does

- Loads 6 dummy customer accounts, each with realistic multi-source data
- Computes a **0–100 health score** using fully transparent, rule-based
  logic (every point added/subtracted is shown to the user — no black box)
- Surfaces **risks** and **opportunities** with the exact evidence behind each
- Builds a merged **activity timeline** across support/email/Slack
- Recommends a **Next Best Action** with a priority level and a one-line
  "why" — not just a suggestion, a reason a CSM would trust enough to act on
- Generates an **AI summary** — calls Claude live if you provide an API
  key in the sidebar; otherwise falls back to a deterministic template
  summary built from the same structured data, so the app is fully
  functional with zero credentials

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| UI | Streamlit | Fastest path to a clean, deployable internal tool; no frontend build step |
| Logic | Plain Python, rule-based scoring | Explainability was prioritized over ML sophistication — CSMs need to trust and override scores, not guess why they moved |
| AI Model | Claude (Sonnet), optional | Used specifically for natural-language summarization, not for scoring/classification — the parts that benefit from language generation, not the parts that need to be auditable |
| Data | Static JSON, dummy | Swappable for live CRM/Zoho/Slack API calls without touching the logic or UI layer |

## Project structure

```
volopay-intel/
├── app.py                       # Streamlit UI
├── generate_data.py             # Generates the dummy dataset (already run — data/ is populated)
├── requirements.txt
├── utils/
│   ├── intelligence_engine.py   # Data merging, health score, risks, opportunities, next action
│   └── ai_summary.py            # Claude API call + template fallback
├── data/
│   ├── crm.json
│   ├── support_tickets.json
│   ├── emails.json
│   ├── slack_messages.json
│   └── product_usage.json
└── .streamlit/config.toml       # Theming
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501. No API key required — the AI Summary panel
will use the template fallback. To see live Claude-generated summaries,
paste an Anthropic API key into the sidebar field (kept in-session only,
never written to disk).

## Deploy publicly (free, ~5 minutes) — Streamlit Community Cloud

1. Create a free GitHub account if you don't have one: https://github.com/signup
2. Create a new **public** repository (e.g. `volopay-customer-intel`)
3. Upload this entire folder's contents to that repository (drag-and-drop
   via GitHub's web UI works fine — no git CLI required)
4. Go to https://share.streamlit.io and sign in with GitHub (free)
5. Click **"Create app"** → select your repo → set main file path to `app.py`
   → **Deploy**
6. Wait ~2–3 minutes for the build. You'll get a public URL like
   `https://your-app-name.streamlit.app` — that's the link to submit.

No API key is required for the deployed app to work end-to-end.

## Sample input / output

**Input (excerpt, Northwind Logistics):**
- CRM: Scale plan, 60 seats licensed, 34 active, renewal in ~6 months
- Support: 1 open high-priority ticket (payout decline errors)
- Email: "We're evaluating two other vendors before renewal"
- Slack (CSM note): "Renewal is in 6 months and they're already shopping around"
- Usage: -18% trend over 30 days

**Output:**
- Health score: 14/100 — Critical
- Risks: 3 (unresolved high-priority ticket, negative-sentiment email,
  low seat utilization, declining usage, renewal-at-risk)
- Recommended action: *Urgent* — escalate to CSM lead, executive check-in
  within 3 business days, with reasoning tied to the specific concurrent
  signals

## Security considerations

- No credentials are stored — the Anthropic API key field is session-only
  and never persisted or logged
- In a production version, source data (CRM/Slack/email) would be pulled
  via OAuth-scoped read-only API tokens, not stored raw; PII (email
  snippets, contact names) would be redacted before being sent to any LLM
- Role-based access would restrict which CSM sees which accounts

## Scalability considerations

- Current version loads all data into memory from JSON — fine for a
  demo, not for scale. Production version: swap `data_loader` calls for a
  Postgres/warehouse query layer, keep `intelligence_engine.py` logic
  unchanged (it's already decoupled from the data source)
- Health score computation is O(n) per customer and independent across
  customers — trivially parallelizable / cacheable per account with a
  nightly or event-triggered recompute rather than on page load
- AI summary calls are the main cost/latency driver at scale — would move
  to async batch generation (e.g. regenerate summaries nightly or on
  significant signal change) rather than generating on every page view

## Error handling & edge cases handled

- Missing/invalid Anthropic API key → silently falls back to template
  summary rather than crashing the app (see `ai_summary.py`)
- Customer with no tickets/emails/Slack notes → empty states render
  cleanly ("No active risk signals detected" / "No expansion signals")
- Division-by-zero guarded in seat utilization calc (`max(seats, 1)`)
- Data merge is by `customer_id` join, not array position, so partial or
  out-of-order source data doesn't misattribute records

## Future improvements (given more time)

With one more sprint, the highest-leverage addition would be a **feedback
loop on the recommendations**: letting CSMs mark a Next Best Action as
"actioned" or "not relevant," and using that signal to tune the rule
thresholds (or eventually train a lightweight model) per industry/segment,
since a healthy usage trend for a 5-person SaaS account and a 140-seat
enterprise account shouldn't be graded on the same curve — right now the
thresholds are uniform across all accounts, which is the biggest
simplification in this prototype.

Other improvements: live source integrations (Zoho CRM, Slack, Gmail,
Freshdesk APIs) behind the same `data_loader` interface; a "why did this
score change" diff view week-over-week; Slack/email digest delivery of
Urgent-priority accounts each morning instead of requiring a dashboard visit.
