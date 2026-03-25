#!/usr/bin/env python3
"""
Admin Dashboard - View orders/transactions
Auto-deletes data older than 3 hours
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Storage file
DATA_FILE = "/root/.openclaw/workspace/money-system/admin-data.json"

# Load data
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"orders": [], "transactions": [], "verifications": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def cleanup_old_data():
    """Delete data older than 3 hours"""
    data = load_data()
    now = time.time()
    cutoff = 3 * 60 * 60  # 3 hours
    
    # Filter orders
    data["orders"] = [o for o in data["orders"] if now - o.get("time", 0) < cutoff]
    
    # Filter transactions  
    data["transactions"] = [t for t in data["transactions"] if now - t.get("time", 0) < cutoff]
    
    # Filter verifications
    data["verifications"] = [v for v in data["verifications"] if now - v.get("time", 0) < cutoff]
    
    save_data(data)
    return len(data["orders"]), len(data["transactions"]), len(data["verifications"])

# Run cleanup on startup
cleanup_old_data()

class AdminHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/":
            self.show_dashboard()
        elif path == "/api/data":
            self.get_data()
        elif path == "/api/clear":
            self.clear_data()
        elif path == "/api/cleanup":
            self.run_cleanup()
        else:
            self.send_response(404)
            self.end_headers()
    
    def show_dashboard(self):
        data = load_data()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard | DigitalStore</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #58a6ff; margin-bottom: 10px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px; }}
        .stat {{ background: #161b22; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat h3 {{ color: #8b949e; font-size: 0.9rem; }}
        .stat .num {{ font-size: 2rem; font-weight: bold; color: #58a6ff; }}
        .btn {{ background: #238636; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; }}
        .btn-danger {{ background: #da3633; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #30363d; }}
        th {{ background: #161b22; color: #8b949e; }}
        .empty {{ text-align: center; color: #8b949e; padding: 40px; }}
        .refresh {{ background: #1f6feb; margin-right: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Admin Dashboard</h1>
            <div>
                <button class="btn refresh" onclick="location.reload()">Refresh</button>
                <button class="btn btn-danger" onclick="clearAll()">Clear All</button>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <h3>Orders</h3>
                <div class="num">{len(data.get('orders', []))}</div>
            </div>
            <div class="stat">
                <h3>Transactions</h3>
                <div class="num">{len(data.get('transactions', []))}</div>
            </div>
            <div class="stat">
                <h3>Verifications</h3>
                <div class="num">{len(data.get('verifications', []))}</div>
            </div>
        </div>
        
        <h2>📦 Recent Orders</h2>
        {self.render_table(data.get('orders', []), ['Order ID', 'Product', 'Amount', 'Status', 'Time'])}
        
        <h2 style="margin-top: 30px;">💰 Transactions</h2>
        {self.render_table(data.get('transactions', []), ['TX Hash', 'Amount', 'Confirmations', 'Time'])}
        
        <h2 style="margin-top: 30px;">🔐 Verifications</h2>
        {self.render_table(data.get('verifications', []), ['Code', 'IP', 'Result', 'Time'])}
    </div>
    
    <script>
        function clearAll() {{
            if(confirm('Delete all data?')) {{
                fetch('/api/clear').then(() => location.reload());
            }}
        }}
        
        // Auto refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def render_table(self, data, headers):
        if not data:
            return '<div class="empty">No data yet</div>'
        
        rows = ""
        for item in data[-10:]:  # Last 10
            row_data = []
            for h in headers:
                key = h.lower().replace(" ", "_")
                row_data.append(str(item.get(key, "")))
            rows += f"<tr><td>{'</td><td>'.join(row_data)}</td></tr>"
        
        return f"<table><tr><th>{'</th><th>'.join(headers)}</th></tr>{rows}</table>"
    
    def get_data(self):
        data = load_data()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def clear_data(self):
        save_data({"orders": [], "transactions": [], "verifications": []})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "cleared"}).encode())
    
    def run_cleanup(self):
        o, t, v = cleanup_old_data()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "cleaned", "orders": o, "transactions": t, "verifications": v}).encode())

# API to add data (called by other services)
def add_order(order_data):
    data = load_data()
    order_data["time"] = time.time()
    data["orders"].append(order_data)
    save_data(data)

def add_transaction(tx_data):
    data = load_data()
    tx_data["time"] = time.time()
    data["transactions"].append(tx_data)
    save_data(data)

def add_verification(verify_data):
    data = load_data()
    verify_data["time"] = time.time()
    data["verifications"].append(verify_data)
    save_data(data)

if __name__ == "__main__":
    print("Starting admin dashboard on port 8889...")
    server = HTTPServer(('0.0.0.0', 8889), AdminHandler)
    print("Admin dashboard running!")
    server.serve_forever()
