"""
Rail B — ERC-20 EGN token minting on Polygon.
Uses Thirdweb Engine REST API for gasless (sponsored) transactions.
1 EGN = 1 kWh sealed in Hashgraph Phase 3 of Alexandria.
"""

import os

import requests


def is_valid_wallet(wallet: str) -> bool:
    """Minimal Ethereum address validation: must start with 0x and be at least 10 chars."""
    return bool(wallet and wallet.startswith("0x") and len(wallet) >= 10)


def mint_egn_tokens(buyer_wallet: str, kwh: int) -> dict:
    """
    Mint EGN tokens to buyer_wallet via Thirdweb Engine gasless REST API.
    1 kWh → 1 EGN (the contract converts kwh → kwh * 10^18 internally).

    Environment variables:
        THIRDWEB_ENGINE_URL   — Engine base URL (default: https://engine.thirdweb.com)
        THIRDWEB_ENGINE_KEY   — Engine access token
        EGN_CONTRACT_ADDRESS  — Deployed EGN contract on Polygon
        POLYGON_CHAIN_ID      — Chain ID (default: 137)

    Returns: {"tx_hash": "<queue_id>", "status": "submitted"}
    """
    engine_url = os.environ.get("THIRDWEB_ENGINE_URL", "https://engine.thirdweb.com")
    engine_key = os.environ.get("THIRDWEB_ENGINE_KEY", "")
    contract_addr = os.environ.get("EGN_CONTRACT_ADDRESS", "")
    chain_id = os.environ.get("POLYGON_CHAIN_ID", "137")

    resp = requests.post(
        f"{engine_url}/contract/{chain_id}/{contract_addr}/write",
        headers={
            "Authorization": f"Bearer {engine_key}",
            "Content-Type": "application/json",
        },
        json={
            "functionName": "mint",
            "args": [buyer_wallet, str(kwh)],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    queue_id = data.get("result", {})
    if isinstance(queue_id, dict):
        queue_id = queue_id.get("queueId", "")
    return {"tx_hash": str(queue_id), "status": "submitted"}
