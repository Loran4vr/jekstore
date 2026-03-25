#!/bin/bash
# DigitalStore Startup Script
# Run this to start the entire system

echo "🧹 Cleaning up old processes..."
pkill -9 -f python3 2>/dev/null
pkill -9 -f cloudflared 2>/dev/null
sleep 2

echo "📦 Starting servers..."
cd /root/.openclaw/workspace/money-system

# Start main store
python3 -m http.server 8080 --directory /root/.openclaw/workspace/money-system > /dev/null 2>&1 &
echo "   Store server started on port 8080"

# Start admin dashboard
python3 admin-dashboard.py > /dev/null 2>&1 &
echo "   Admin server started on port 8889"

sleep 3

echo "🔗 Creating tunnels..."
# Store tunnel
npx -y cloudflared tunnel --url http://localhost:8080 > /tmp/store-tunnel.log 2>&1 &
TUNNEL1=$!

# Admin tunnel
npx -y cloudflared tunnel --url http://localhost:8889 > /tmp/admin-tunnel.log 2>&1 &
TUNNEL2=$!

sleep 15

echo ""
echo "🎉 SYSTEM READY!"
echo "================"
echo ""
echo "📍 Store: Check the tunnel logs for the URL"
echo "📍 Admin: Check the tunnel logs for the URL"
echo ""
echo "To check tunnels:"
echo "  tail /tmp/store-tunnel.log"
echo "  tail /tmp/admin-tunnel.log"
echo ""
echo "To check payments:"
echo "  python3 check-payments.py"
