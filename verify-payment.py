#!/usr/bin/env python3
"""
Bitcoin Payment Verification System
Checks blockchain for payments to your address
"""

import requests
import json
import time

# Your Bitcoin address
BTC_ADDRESS = "1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ"

# Product prices in BTC (approximate)
PRODUCT_PRICES = {
    "notion": 0.0005,      # ~$19
    "ai-prompts": 0.00035, # ~$14
    "email-templates": 0.0003, # ~$12
    "excel-budget": 0.00025,   # ~$10
    "resume": 0.00025,        # ~$10
    "business-plan": 0.00038,  # ~$15
    "social-media": 0.0002,   # ~$8
    "copywriting": 0.00028,   # ~$11
    "goals": 0.00023,         # ~$9
    "bundle": 0.00063          # ~$25
}

def check_payment():
    """Check for incoming payments"""
    try:
        url = f"https://mempool.space/api/address/{BTC_ADDRESS}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Check chain stats (confirmed transactions)
        chain_tx_count = data.get("chain_stats", {}).get("tx_count", 0)
        chain_funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
        
        # Check mempool (unconfirmed)
        mempool_tx_count = data.get("mempool_stats", {}).get("tx_count", 0)
        
        return {
            "confirmed_txs": chain_tx_count,
            "confirmed_satoshis": chain_funded,
            "unconfirmed_txs": mempool_tx_count,
            "total_received_btc": chain_funded / 100000000
        }
    except Exception as e:
        return {"error": str(e)}

def check_transaction_details(tx_hash):
    """Get details of a specific transaction"""
    try:
        url = f"https://mempool.space/api/tx/{tx_hash}"
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

def verify_payment_for_product(product_name, expected_btc=None):
    """Verify payment for specific product"""
    if expected_btc is None:
        expected_btc = PRODUCT_PRICES.get(product_name, 0.0001)
    
    payment_info = check_payment()
    
    if "error" in payment_info:
        return {"status": "error", "message": payment_info["error"]}
    
    # Check if any payment received
    if payment_info["confirmed_txs"] > 0 or payment_info["unconfirmed_txs"] > 0:
        received = payment_info["total_received_btc"]
        
        if received >= expected_btc:
            return {
                "status": "paid",
                "received_btc": received,
                "message": "Payment confirmed!"
            }
        else:
            return {
                "status": "partial",
                "received_btc": received,
                "expected_btc": expected_btc,
                "message": f"Received {received} BTC, expected {expected_btc} BTC"
            }
    
    return {
        "status": "no_payment",
        "message": "No payment detected"
    }

def get_payment_link(amount_usd):
    """Generate payment link for amount"""
    # Approximate BTC amount (should use real-time price)
    btc_price_approx = 38000  # You'll want to fetch real price
    btc_amount = amount_usd / btc_price_approx
    
    return f"bitcoin:{BTC_ADDRESS}?amount={btc_amount:.8f}"

# Manual check function
if __name__ == "__main__":
    print("🔍 Checking payments...")
    result = check_payment()
    print(json.dumps(result, indent=2))
