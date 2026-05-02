"""
Enterprise Onboarder — Rail C
Generates API keys for enterprise clients and tracks their contracts.
"""

import json
import secrets
import time
from pathlib import Path

CONTRACTS_PATH = Path(__file__).resolve().parent / "acquisition_data" / "contracts.json"


class EnterpriseOnboarder:
    def __init__(self):
        CONTRACTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not CONTRACTS_PATH.exists():
            CONTRACTS_PATH.write_text(json.dumps({"contracts": []}))

    def onboard_lead(self, lead: dict) -> dict:
        """Generate API key and contract record for a new enterprise client."""
        api_key = secrets.token_urlsafe(32)
        monthly_kwh = float(lead.get("kwh_requested", 0))

        contract = {
            "prospect_id": lead.get("prospect_id", ""),
            "email": lead.get("email", ""),
            "api_key": api_key,
            "monthly_kwh": monthly_kwh,
            "monthly_cad": round(monthly_kwh * 0.065, 2),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "active",
        }

        data = json.loads(CONTRACTS_PATH.read_text())
        data["contracts"].append(contract)
        CONTRACTS_PATH.write_text(json.dumps(data, indent=2))

        return contract

    def get_contracts(self) -> list:
        """Return all active contracts."""
        return json.loads(CONTRACTS_PATH.read_text()).get("contracts", [])
