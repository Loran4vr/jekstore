#!/bin/bash
# Payment Checker - Run this to check for new payments
# Usage: ./payment-checker.sh

BTC_ADDRESS="1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ"

echo "🔍 Checking Bitcoin payments to: $BTC_ADDRESS"
echo "============================================"

# Get address info
RESPONSE=$(curl -s "https://mempool.space/api/address/$BTC_ADDRESS")

TX_COUNT=$(echo "$RESPONSE" | grep -o '"tx_count":[0-9]*' | head -1 | cut -d':' -f2)
FUNDED_SATOSHIS=$(echo "$RESPONSE" | grep -o '"funded_txo_sum":[0-9]*' | head -1 | cut -d':' -f2)

BTC_RECEIVED=$(echo "scale=8; $FUNDED_SATOSHIS / 100000000" | bc)

echo "📊 Total Transactions: $TX_COUNT"
echo "💰 Total Received: $BTC_RECEIVED BTC"
echo ""

if [ "$TX_COUNT" -gt 0 ]; then
    echo "✅ PAYMENT DETECTED!"
    echo ""
    echo "Run: python3 verify-payment.py"
    echo "To verify specific payment amounts."
else
    echo "❌ No payments yet"
fi
