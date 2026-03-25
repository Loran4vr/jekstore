# DigitalStore - Current Status

## What We Have

### 1. Main Store Files
Located at: `/root/.openclaw/workspace/money-system/`
- index.html (main store)
- sample-order.html (free test order)
- admin-dashboard.py (admin panel)
- verify-simple.py (product verification)

### 2. Bitcoin Payment
Address: `1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ`

### 3. Products (10 total)
Notion Planner $19 | AI Prompts $14 | Email Templates $12 | Excel Budget $10 | Resume Templates $10 | Business Plan $15 | Social Media $8 | Copywriting $11 | Goals $9 | Study Guides $8

---

## How to Access (With Agent Running)

The agent can start tunnels when active. To use:

1. Ask the agent to start the servers
2. Use the temporary tunnel URLs provided
3. When agent stops, URLs stop working

---

## How to Get Permanent Site (Without Agent)

The ONLY permanent solution is Netlify Drop:
1. Go to https://app.netlify.com/drop
2. Upload index.html
3. Get permanent URL

---

## Quick Start (For Agent)

```bash
# Kill old processes
pkill -9 -f python3
pkill -9 -f cloudflared

# Start servers
python3 -m http.server 8080 --directory /root/.openclaw/workspace/money-system &
python3 /root/.openclaw/workspace/money-system/admin-dashboard.py &

# Create tunnels
npx -y cloudflared tunnel --url http://localhost:8080 &
npx -y cloudflared tunnel --url http://localhost:8889 &
```

---

## Next Steps

1. **Share store link** to get sales
2. **Check payments** with python3 check-payments.py
3. **Monitor admin panel** for orders

## To Make $200/Day
- Share the store everywhere
- Each sale = $8-25
- Need 8-25 sales/day
