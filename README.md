# Ads Duck: the marketing truth agent

**Problem:** ad platforms mark their own homework. Google and Meta often claim the same sale, and business owners make budget calls on inflated ROAS and CPA.

**Duck** is a Google ADK multi-agent system that lives inside ADMD (Ads Duck Master Dashboard). It reads a workspace's real store orders and ad spend, shows what really happened, and proposes fixes that a human must approve.

## Agents
- **duck (root):** routes the question.
- **data_agent:** fetches and summarises workspace performance.
- **truth_checker:** claimed vs true CPA/ROAS per platform, over-claim %, blended-metric warnings, brand terms leaking into non-brand campaigns. All maths runs in Python tools, so the model never invents numbers.
- **action_agent:** drafts fixes (budget shifts, brand negatives). **Dry run only** with a human approval gate. Nothing touches an ad account.

## Architecture
```
ADMD dashboard (duck button) -> Duck API (ADK, Cloud Run) -> ADMD read-only Duck API (demo workspaces only)
```
ADMD's code is private and not in this repo. Duck only reads **demo workspaces with made-up data**, enforced twice: an allowlist in ADMD and `DUCK_ALLOWED_WORKSPACES` here.

## Run
```bash
pip install -r requirements.txt
cp .env.example ads_duck/.env   # fill in keys
adk web          # dev UI
adk api_server   # HTTP API for ADMD
```
Deploy: `adk deploy cloud_run --project YOUR_PROJECT --region europe-west2 ./ads_duck`

## ADMD API contract (header `X-Duck-Key`)
- `GET /api/duck/workspaces/:id/summary` -> `{workspace_id, name, currency, start, end, total_orders, total_revenue}`
- `GET .../orders?start&end` -> `{orders: [{order_id, date, revenue, utm_source, utm_medium, utm_campaign, utm_term}]}`
- `GET .../spend?start&end` -> `{rows: [{date, platform, campaign, campaign_type, spend, claimed_conversions, claimed_revenue}]}`
- `GET .../search-terms?start&end` -> `{rows: [{campaign, campaign_type, search_term, clicks, cost, conversions}]}`

Built at GDG London AI DevCamp Agentic Hackathon, 31 Oct 2026.
