import os
from pathlib import Path
from flask import Flask, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ROOT = Path(__file__).parent


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "service": "tim-burner"}), 200


@app.route("/api/energon/stock")
def stock():
    return jsonify({
        "sealed_kwh": 8025803600.51,
        "price_usd_per_kwh": 0.047,
        "price_cad_per_kwh": 0.064,
    })


@app.route("/api/energon/sell", methods=["POST"])
def sell():
    from flask import request
    data = request.get_json(silent=True) or {}
    kwh = float(data.get("kwh", 100000))
    buyer = data.get("buyer", "unknown")
    recipient = os.environ.get("ALEXANDRIA_WALLET", "0x4B9F37c926cC1cF0b4B7037b97a55332414CABDD")
    amount_usdc = round(kwh * 0.047, 2)
    return jsonify({
        "rail": "D",
        "invoice": {
            "kwh": kwh,
            "amount_usd": amount_usdc,
            "recipient": recipient,
            "buyer": buyer,
            "protocol": "x402",
        }
    })


@app.route("/")
def index():
    return send_file(ROOT / "tim-burner.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
