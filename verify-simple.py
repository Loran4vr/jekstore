#!/usr/bin/env python3
"""
Product Verification System - Simple Version
"""

import json
import time
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = 8888
RATE_LIMIT = 3
RATE_PERIOD = 3 * 60 * 60

# Storage
verification_db = {}
rate_limit_db = {}

def get_client_ip(handler):
    forwarded = handler.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return handler.client_address[0]

def generate_code(product_id):
    timestamp = str(int(time.time()))
    random_part = hashlib.md5(f"{product_id}{timestamp}".encode()).hexdigest()[:8].upper()
    return f"{product_id.upper()[:8]}-{random_part}"

def check_rate_limit(ip):
    now = time.time()
    if ip not in rate_limit_db:
        rate_limit_db[ip] = {"count": 0, "reset_time": now + RATE_PERIOD}
    
    ip_data = rate_limit_db[ip]
    if now > ip_data["reset_time"]:
        ip_data["count"] = 0
        ip_data["reset_time"] = now + RATE_PERIOD
    
    return ip_data["count"] < RATE_LIMIT, ip_data["count"]

def increment_rate_limit(ip):
    if ip in rate_limit_db:
        rate_limit_db[ip]["count"] += 1
    else:
        rate_limit_db[ip] = {"count": 1, "reset_time": time.time() + RATE_PERIOD}

# Pre-generated codes for products
PRODUCTS = {
    "NOTION-P-2026-ABCD": "Notion Life Planner",
    "AIPROMPT-2026-EFGH": "500+ AI Prompts Pack",
    "EMAIL-2026-IJKL": "100 Email Templates",
    "EXCEL-2026-MNOP": "Excel Budget Tracker",
    "RESUME-2026-QRST": "Resume Templates",
    "BUNDLE-2026-YZ12": "Ultimate Bundle"
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == '/verify':
            self.handle_verify(params)
        elif path == '/status':
            self.handle_status()
        elif path == '/products':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"products": PRODUCTS}).encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Verify</title>
<style>body{font-family:sans-serif;background:#0d1117;color:#c9d1d9;padding:40px;text-align:center}
input{padding:12px;width:300px;border-radius:6px;border:1px solid #30363d;background:#161b22;color:#fff}
button{padding:12px 24px;background:#238636;color:#fff;border:none;border-radius:6px;cursor:pointer}
#r{margin-top:20px;padding:15px;border-radius:6px;display:none}
.s{background:rgba(63,185,80,0.2);border:1px solid #3fb950;color:#3fb950}
.e{background:rgba(248,81,73,0.2);border:1px solid #f85149;color:#f85149}
</style></head>
<body><h1>Verify Product</h1>
<input id="c" placeholder="Enter code"><button onclick="v()">Verify</button>
<div id="r"></div>
<script>async function v(){let code=document.getElementById("c").value.trim();
let r=document.getElementById("r");r.style.display="none";
if(!code){r.className="e";r.textContent="Enter a code";r.style.display="block";return}
let res=await fetch("/verify?code="+encodeURIComponent(code));
let d=await res.json();
r.className=d.success?"s":"e";r.textContent=d.message;r.style.display="block";
if(d.remaining!==undefined)r.textContent+=" ("+d.remaining+" left)"}</script>
</body></html>'''
            self.wfile.write(html.encode())
    
    def handle_verify(self, params):
        code = params.get('code', [''])[0].upper().strip()
        ip = get_client_ip(self)
        
        allowed, count = check_rate_limit(ip)
        if not allowed:
            self.send_json({"success": False, "message": "Rate limit exceeded", "remaining": 0})
            return
        
        increment_rate_limit(ip)
        remaining = RATE_LIMIT - rate_limit_db.get(ip, {}).get("count", 0)
        
        if code in PRODUCTS:
            self.send_json({"success": True, "message": "Verified!", "product": PRODUCTS[code], "remaining": remaining})
        else:
            self.send_json({"success": False, "message": "Invalid code", "remaining": remaining})
    
    def handle_status(self):
        ip = get_client_ip(self)
        allowed, count = check_rate_limit(ip)
        remaining = RATE_LIMIT - count if allowed else 0
        self.send_json({"remaining": remaining})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

print(f"Starting verification server on port {PORT}...")
server = HTTPServer(('0.0.0.0', PORT), Handler)
print(f"Server running! Rate limit: {RATE_LIMIT} per {RATE_PERIOD//3600}h per IP")
server.serve_forever()
