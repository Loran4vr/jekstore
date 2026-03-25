#!/bin/bash
# Payment monitoring script - runs every 5 minutes
# Checks Bitcoin address for new payments

BTC_ADDRESS="1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ"
LAST_CHECK_FILE="/root/.openclaw/workspace/money-system/last-tx-check.txt"

echo "Checking Bitcoin payments..."

# Get transactions
TXS=$(curl -s "https://mempool.space/api/address/${BTC_ADDRESS}/txs" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")

echo "Found $TXS transactions"

if [ "$TXS" -gt "0" ]; then
    echo "💰 PAYMENT DETECTED!"
    # In production, would trigger delivery
fi
