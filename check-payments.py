#!/usr/bin/env python3
"""Simple payment checker - no dependencies"""

import urllib.request
import json
import sys

BTC_ADDRESS = "1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ"

def check():
    try:
        url = f"https://mempool.space/api/address/{BTC_ADDRESS}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
        
        txs = data.get("chain_stats", {}).get("tx_count", 0)
        satoshis = data.get("chain_stats", {}).get("funded_txo_sum", 0)
        btc = satoshis / 100_000_000
        
        print(f"Address: {BTC_ADDRESS}")
        print(f"Transactions: {txs}")
        print(f"Received: {btc} BTC")
        
        if txs > 0:
            print("\n PAYMENT RECEIVED!")
            return True
        else:
            print("\nNo payments yet")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check()
