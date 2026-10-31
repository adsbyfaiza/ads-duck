import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from . import tools as t

MODEL = LiteLlm(model=os.getenv("DUCK_MODEL", "anthropic/claude-sonnet-4-5"))

RULES = (
    "Only use numbers returned by tools. Never estimate or invent figures. "
    "Never present blended ROAS/CPA as paid media performance. "
    "Use short, plain sentences a business owner can act on."
)

data_agent = LlmAgent(
    name="data_agent",
    model=MODEL,
    description="Fetches and summarises ADMD workspace performance.",
    instruction="You read ADMD workspace data and summarise performance. " + RULES,
    tools=[t.get_workspace_summary, t.get_orders, t.get_spend, t.get_search_terms],
)

truth_agent = LlmAgent(
    name="truth_checker",
    model=MODEL,
    description="Checks whether ad platform numbers are inflated versus real orders.",
    instruction=(
        "You audit ad platform claims. Run check_claimed_vs_real and, when brand terms are known, "
        "check_brand_leakage. Lead with the biggest gap: claimed vs true CPA/ROAS and over-claim %. " + RULES
    ),
    tools=[t.check_claimed_vs_real, t.check_brand_leakage, t.get_workspace_summary],
)

action_agent = LlmAgent(
    name="action_agent",
    model=MODEL,
    description="Proposes fixes as dry-run plans that need human approval.",
    instruction=(
        "You turn findings into concrete fixes using propose_action (budget shifts, brand negatives, pauses). "
        "Everything is DRY RUN. Never say an action was executed. Ask the user to approve each proposal by id, "
        "and only call approve_action when the user clearly says yes. " + RULES
    ),
    tools=[t.propose_action, t.approve_action],
)

root_agent = LlmAgent(
    name="duck",
    model=MODEL,
    description="Duck, the ADMD marketing truth agent.",
    instruction=(
        "You are Duck, the analyst inside ADMD (Ads Duck Master Dashboard). The user's message includes a workspace_id. "
        "Route: performance questions -> data_agent; 'is this real / inflated / true ROAS / brand leak' -> truth_checker; "
        "'what should I do / fix it' -> action_agent. For a full review, go truth_checker then action_agent. " + RULES
    ),
    sub_agents=[data_agent, truth_agent, action_agent],
)
