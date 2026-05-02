"""
Alexandria Commerce Server — runs all 4 rails on port 5050.
Serves the storefront at / and the API at /api/*

Rails:
  A: POST /api/rail-a/checkout  → Stripe fiat
  B: ERC-20 EGN (Polygon) — via smart contract (future)
  C: POST /api/energon/sell     → Enterprise API
  D: POST /api/energon/sell     → x402 AI agent (header: x-agent-type: ai)
"""

import sys
from pathlib import Path

# Ensure ADAM root is on the path when running as __main__
_ADAM_ROOT = Path(__file__).resolve().parents[1]
if str(_ADAM_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADAM_ROOT))

from flask import send_file, jsonify

from dwallstreet.energon_api import create_app

app = create_app()


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "service": "tim-burner"}), 200


@app.route("/")
def storefront():
    # Tim-Burner hot-rod UI at repo root, fallback to Next.js build
    tim_burner = Path(__file__).parents[1] / "tim-burner.html"
    if tim_burner.exists():
        return send_file(tim_burner)
    return send_file(Path(__file__).parent / "storefront" / "out" / "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files from the out directory."""
    static_dir = Path(__file__).parent / "storefront" / "out"
    requested = static_dir / path
    if requested.is_file():
        return send_file(requested)
    # Fallback for SPA routing
    return send_file(static_dir / "index.html")


@app.route("/deploy")
def deploy_page():
    """MetaMask deployment page for EGN token — served over HTTP so MetaMask injects."""
    return send_file(Path(__file__).parent / "egn_token" / "deploy.html")


@app.route("/shop")
def shop_page():
    """Catalogue de produits digitaux — scripts Python, prompts IA, énergie."""
    return send_file(Path(__file__).parent / "storefront" / "shop.html")


@app.route("/liquidity")
def liquidity_page():
    """Uniswap V2 liquidity page — Mint EGN + addLiquidityETH via MetaMask."""
    return send_file(Path(__file__).parent / "egn_token" / "liquidity.html")


if __name__ == "__main__":
    print("⚡ Alexandria Commerce OS")
    print("   http://localhost:5050        → Storefront (Rail A fiat)")
    print("   POST /api/energon/sell       → Rail C (enterprise) / Rail D (x402)")
    print("   POST /api/rail-a/checkout    → Stripe checkout")
    print("   GET  /api/energon/stock      → Live stock")
    app.run(host="0.0.0.0", port=5050, debug=False)
