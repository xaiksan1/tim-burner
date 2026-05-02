"""
Buyer Router — classifies a lead and routes to the correct sales rail.
Rail A: Fiat/Stripe (small buyers, retail)
Rail B: ERC-20 token on Polygon (crypto buyers)
Rail C: Enterprise API + contract (large volumes, B2B)
Rail D: x402 machine-to-machine (AI agents)
"""

from typing import Literal

Rail = Literal["A", "B", "C", "D"]

ENTERPRISE_KWH_THRESHOLD = 1_000_000  # 1M kWh → enterprise contract
ENTERPRISE_DOMAINS = {
    "datacenter",
    "aws",
    "google",
    "microsoft",
    "azure",
    "hpc",
    "corp",
}


class BuyerRouter:
    def classify(self, context: dict) -> Rail:
        """
        Classify a buyer context and return the appropriate rail.

        context keys (all optional):
          - wallet: str             → crypto buyer
          - stripe_session: str     → already in Stripe flow
          - email: str              → contact email
          - kwh: float              → purchase size
          - headers: dict           → HTTP headers (checks x-agent-type)
        """
        headers = context.get("headers", {})

        # Rail D: AI agent signal
        if (
            headers.get("x-agent-type") == "ai"
            or headers.get("x-payment-context") == "agent"
        ):
            return "D"

        # Rail B: wallet present → crypto buyer
        wallet = context.get("wallet", "")
        if wallet and wallet.startswith("0x") and len(wallet) >= 40:
            return "B"

        # Rail A: already in Stripe
        if context.get("stripe_session"):
            return "A"

        # Rail C: large volume OR enterprise email domain
        kwh = float(context.get("kwh", 0))
        email = context.get("email", "")
        is_enterprise_email = any(d in email.lower() for d in ENTERPRISE_DOMAINS)

        if kwh >= ENTERPRISE_KWH_THRESHOLD or is_enterprise_email:
            return "C"

        # Default: fiat / Stripe
        return "A"
