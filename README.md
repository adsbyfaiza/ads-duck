# Duck: the truth agent inside ADMD 🦆

[![10th of 32](https://img.shields.io/badge/%F0%9F%8F%86_10th_of_32-GDG_London_AI_DevCamp_2026-F5B800?style=for-the-badge)](https://youtu.be/iU12QE6p_Nc)

**Ad platforms mark their own homework. Duck checks it.**

Built with **Google ADK + Gemini** at the GDG London AI DevCamp 2026 Agentic Hackathon.

▶️ **Demo video (real live Gemini answers):** https://youtu.be/iU12QE6p_Nc

---

## The problem

Google, Meta and Klaviyo each claim credit for the same sale. Add up what the platforms report and you have sold more than your store actually took. Business owners then make budget decisions on inflated ROAS and CPA.

## What Duck does

Duck is a multi-agent analyst that lives inside **ADMD (Ads Duck Master Dashboard)**. A business owner presses the duck button, asks a question, and Duck compares what each ad platform claims with the real orders from the store.

| Agent | Job |
|---|---|
| **Coordinator** | Routes each question to the right agent |
| **Data agent** | Reads the workspace through a locked, read-only ADMD API |
| **Truth checker** | Claimed vs real orders, claimed vs true CPA and ROAS, over-claim %, blended metrics flagged, brand terms leaking into non-brand campaigns |
| **Action agent** | Proposes fixes as dry-run cards behind a human Approve gate. Nothing touches an ad account |

**Design rule:** all maths runs in Python tools, never in the model. Gemini explains; code calculates. Duck cannot invent a number.

## Real results from the live demo

Fernhill Coffee Co. is a **sample store with made-up data**.

| Platform | Claimed orders | Real orders | Over-claim |
|---|---|---|---|
| Meta | 116.59 | 84 | **+38.8%** |
| Google Ads | 206.34 | 167 | **+23.6%** |
| Klaviyo | 96 | 70 | **+37.1%** |

- Meta's true CPA is **£22.86**, not the £16.47 it reports. True ROAS **1.30**, not 1.77.
- **132 brand-name clicks (£53.31)** were paid for by non-brand campaigns.

Every figure Duck quoted matched the code.

## Safety

- Demo workspaces only, enforced by a hard-coded allowlist. Real client workspaces return **403**.
- API key header required on every call.
- Approvals only through the button, once each. A typed "approve" is refused.
- Sample data only. No personal data.

## About this repo

This repo holds **Duck's first standalone ADK build** (`ads_duck/`), written at the start of the hackathon. The **full integrated version** (Gemini model fallback, ADMD API, dashboard panel, tests) lives in ADMD's private repository, because that dashboard holds real client data. Happy to walk judges through it.

### Run this version

```bash
pip install -r requirements.txt
cp .env.example ads_duck/.env   # add your keys
adk web
```

---

Built by **Faiza Khan**, founder of [Ads Duck](https://adsduck.co.uk).
