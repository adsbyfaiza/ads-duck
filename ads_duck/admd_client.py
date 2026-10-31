"""Read-only client for the ADMD Duck API. Demo workspaces only."""
import os
import requests

ADMD_API_URL = os.getenv("ADMD_API_URL", "").rstrip("/")
DUCK_API_KEY = os.getenv("DUCK_API_KEY", "")
ALLOWED = {w.strip() for w in os.getenv("DUCK_ALLOWED_WORKSPACES", "").split(",") if w.strip()}


def fetch(workspace_id: str, resource: str, params: dict | None = None) -> dict:
    # Second safety lock: ADMD blocks non-demo workspaces too.
    if ALLOWED and workspace_id not in ALLOWED:
        return {"error": f"Workspace '{workspace_id}' is not a demo workspace. Duck only reads demo data."}
    try:
        r = requests.get(
            f"{ADMD_API_URL}/api/duck/workspaces/{workspace_id}/{resource}",
            headers={"X-Duck-Key": DUCK_API_KEY},
            params=params or {},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": f"ADMD API call failed: {e}"}
