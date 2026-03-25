# DigitalStore - Permanent Hosting Solution

## The Challenge
- Tunnel services (trycloudflare) only work while agent is running
- All permanent hosting needs authentication (Netlify, GitHub, etc.)
- We cannot bypass authentication requirements legally

## Solution: Netlify Drop (Manual Step Required ONCE)

This is the ONLY free option that doesn't need authentication:

1. **Download the file** from this location on your computer:
   - The agent has the store at `/root/.openclaw/workspace/money-system/index.html`
   - You need to get this file somehow (see below)
   
2. **Go to**: https://app.netlify.com/drop

3. **Drag the file** onto the page

4. **Get your permanent URL!** (e.g., yourname.netlify.app)

---

## How to Get the File

### Option A: Ask the Agent
When the agent is running, ask:
"Give me the index.html file content"

Then copy the content and save it as `index.html` on your computer.

### Option B: The Agent Uploads It
The agent can try to upload via file hosting services. Ask:
"Can you upload to any file host?"

---

## Once You Have Permanent Hosting

The agent can then:
- Update the store with new products
- Check Bitcoin payments  
- Monitor admin panel
- Add new features

But the INITIAL setup of permanent hosting needs you to do the Netlify Drop step.

---

## What the Agent CAN Do Now

1. **Start temporary tunnels** - works while agent runs
2. **Check Bitcoin payments** - run payment checker anytime
3. **Update the store** - modify products, prices, content
4. **Create new products** - build more digital products

---

## Quick Command to Start Everything

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

This gives you temporary URLs while the agent is active.
