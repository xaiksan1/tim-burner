"""
x402 Payment Handler — machine-to-machine USDC payments.
Implements the x402 protocol (HTTP 402 Payment Required).
Defaults to Ethereum mainnet (chain 1). Override via EGN_CHAIN_ID env var.
"""

import os

PRICE_USD_PER_KWH = 0.047  # USD
CHAIN_ID = int(os.environ.get("EGN_CHAIN_ID", "1"))  # 1 = Ethereum mainnet

# USDC addresses by chain
_USDC = {
    1: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # Ethereum mainnet
    137: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # Polygon mainnet
}
USDC_CONTRACT = os.environ.get("USDC_CONTRACT", _USDC.get(CHAIN_ID, _USDC[1]))
USDC_DECIMALS = 6

# keccak256("Transfer(address,address,uint256)") — standard ERC-20 Transfer topic
_TRANSFER_SIG = "Transfer(address,address,uint256)"


def build_invoice(kwh: float, recipient_wallet: str) -> dict:
    """Build a 402 invoice for the given kWh amount."""
    amount_usdc = round(kwh * PRICE_USD_PER_KWH, 6)
    return {
        "payment_required": {
            "currency": "USDC",
            "amount_usdc": amount_usdc,
            "chain_id": CHAIN_ID,
            "token_contract": USDC_CONTRACT,
            "recipient": recipient_wallet,
            "memo": f"Energon EGN {kwh:.0f} kWh — Alexandria",
            "thirdweb_gasless": True,
        }
    }


def verify_eth_payment(
    tx_hash: str, expected_amount_eth: float, recipient_wallet: str
) -> bool:
    """Verify a native ETH transfer (not USDC) to recipient_wallet.

    Checks tx.to == recipient AND tx.value >= expected_amount_wei AND receipt.status == 1.
    Use when sponsor pays in ETH directly instead of USDC.
    """
    try:
        from web3 import Web3

        rpc = os.environ.get("ETH_RPC", "https://eth.llamarpc.com")
        w3 = Web3(Web3.HTTPProvider(rpc))
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if not receipt or receipt["status"] != 1:
            return False
        tx = w3.eth.get_transaction(tx_hash)
        recipient_checksum = Web3.to_checksum_address(recipient_wallet)
        expected_wei = int(expected_amount_eth * 10**18)
        return (
            tx["to"] is not None
            and Web3.to_checksum_address(tx["to"]) == recipient_checksum
            and tx["value"] >= expected_wei
        )
    except Exception:
        return False


def verify_payment(
    tx_hash: str, expected_amount_usdc: float, recipient_wallet: str
) -> bool:
    """
    Verify that tx_hash contains a confirmed USDC Transfer to recipient_wallet
    of at least expected_amount_usdc.

    Decodes the ERC-20 Transfer(from, to, value) event:
    - topics[0] = event signature hash
    - topics[1] = indexed `from` address (32-byte padded)
    - topics[2] = indexed `to`   address (32-byte padded)
    - data      = uint256 value (32 bytes, big-endian), USDC has 6 decimals

    Returns True only if:
      receipt.status == 1 (success)
      AND a USDC Transfer log exists where to == recipient AND value >= expected_raw
    """
    try:
        from web3 import Web3

        rpc = os.environ.get(
            "ETH_RPC", os.environ.get("POLYGON_RPC", "https://eth.llamarpc.com")
        )
        w3 = Web3(Web3.HTTPProvider(rpc))
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if not receipt or receipt["status"] != 1:
            return False

        transfer_topic = w3.keccak(text=_TRANSFER_SIG)
        recipient_checksum = Web3.to_checksum_address(recipient_wallet)
        expected_raw = int(expected_amount_usdc * 10**USDC_DECIMALS)

        for log in receipt["logs"]:
            if (
                log["address"].lower() == USDC_CONTRACT.lower()
                and len(log["topics"]) == 3
                and log["topics"][0] == transfer_topic
            ):
                # topics[2]: 32-byte padded address → last 20 bytes = actual address
                to_addr = Web3.to_checksum_address(log["topics"][2][-20:])
                # data: 32-byte big-endian uint256
                value = int.from_bytes(log["data"], "big")
                if to_addr == recipient_checksum and value >= expected_raw:
                    return True
        return False
    except Exception:
        return False
