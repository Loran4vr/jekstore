#!/usr/bin/env python3
"""
Product Verification System
- 3 free verifications per IP every 3 hours
- Rate limiting by IP
- Secure verification codes
"""

import json
import time
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Configuration
RATE_LIMIT = 3  # verifications per period
RATE_PERIOD = 3 * 60 * 60  # 3 hours in seconds

# In-memory storage (use Redis for production)
verification_db = {}  # {"code": {"product": "...", "valid": True, "created": ...}}
rate_limit_db = {}   # {"ip": {"count": N, "reset_time": ...}}

# Product verification codes (generated when you create products)
PRODUCT_CODES = {
    "notion-planner": "NOTION-2026-XXXX-ABCD",
    "ai-prompts": "AIPROMPT-2026-XXXX-EFGH",
    "email-templates": "EMAIL-2026-XXXX-IJKL",
    "excel-budget": "EXCEL-2026-XXXX-MNOP",
    "resume": "RESUME-2026-XXXX-QRST",
    "business-plan": "BIZPLAN-2026-XXXX-UVWX",
    "bundle": "BUNDLE-2026-XXXX-YZ12"
}

def get_client_ip(handler):
    """Get client IP from request"""
    # Check for forwarded IP (if behind proxy)
    forwarded = handler.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return handler.client_address[0]

def generate_code(product_id):
    """Generate unique verification code for a product"""
    timestamp = str(int(time.time()))
    random_part = hashlib.md5(f"{product_id}{timestamp}".encode()).hexdigest()[:8].upper()
    prefix = product_id.upper()[:8]
    return f"{prefix}-2026-{random_part}"

def check_rate_limit(ip):
    """Check if IP has exceeded rate limit"""
    now = time.time()
    
    if ip not in rate_limit_db:
        rate_limit_db[ip] = {"count": 0, "reset_time": now + RATE_PERIOD}
    
    ip_data = rate_limit_db[ip]
    
    # Reset if period expired
    if now > ip_data["reset_time"]:
        ip_data["count"] = 0
        ip_data["reset_time"] = now + RATE_PERIOD
    
    return ip_data["count"] < RATE_LIMIT, ip_data["count"]

def increment_rate_limit(ip):
    """Increment verification count for IP"""
    if ip in rate_limit_db:
        rate_limit_db[ip]["count"] += 1
    else:
        rate_limit_db[ip] = {"count": 1, "reset_time": time.time() + RATE_PERIOD}

def verify_code(code):
    """Verify a product code"""
    code = code.upper().strip()
    
    # Check if it's a valid format
    for product, valid_code in PRODUCT_CODES.items():
        if code == valid_code:
            return {"valid": True, "product": product, "message": "✓ Product verified!"}
    
    # Check custom generated codes
    if code in verification_db:
        vdata = verification_db[code]
        if vdata.get("valid", False):
            return {"valid": True, "product": vdata["product"], "message": "✓ Product verified!"}
        else:
            return {"valid": False, "product": None, "message": "✗ Code has been used/invalidated"}
    
    return {"valid": False, "product": None, "message": "✗ Invalid verification code"}

class VerificationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        
        if path == '/verify':
            self.handle_verify(params)
        elif path == '/status':
            self.handle_status(params)
        elif path == '/products':
            self.handle_products()
        elif path == '/':
            self.handle_index()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def handle_index(self):
        """Main verification page"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Product | DigitalStore</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: #161b22; padding: 40px; border-radius: 12px; max-width: 450px; width: 90%; border: 1px solid #30363d; }
        h1 { text-align: center; margin-bottom: 10px; color: #58a6ff; }
        p { text-align: center; color: #8b949e; margin-bottom: 25px; }
        input { width: 100%; padding: 14px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: white; font-size: 16px; margin-bottom: 15px; }
        input:focus { outline: none; border-color: #58a6ff; }
        button { width: 100%; padding: 14px; background: #238636; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: 600; }
        button:hover { background: #2ea043; }
        .result { margin-top: 20px; padding: 15px; border-radius: 8px; text-align: center; display: none; }
        .result.success { background: rgba(63, 185, 80, 0.2); border: 1px solid #3fb950; color: #3fb950; }
        .result.error { background: rgba(248, 81, 73, 0.2); border: 1px solid #f85149; color: #f85149; }
        .result.warning { background: rgba(210, 153, 34, 0.2); border: 1px solid #d29922; color: #d29922; }
        .info { margin-top: 20px; padding: 15px; background: rgba(88, 166, 255, 0.1); border-radius: 8px; font-size: 14px; }
        .info h3 { color: #58a6ff; margin-bottom: 10px; }
        .info ul { margin-left: 20px; }
        .info li { margin: 5px 0; }
        .remaining { text-align: center; margin-top: 15px; color: #8b949e; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Verify Product</h1>
        <p>Enter your product verification code</p>
        
        <input type="text" id="code" placeholder="e.g., NOTION-2026-XXXX-ABCD" autocomplete="off">
        <button onclick="verify()">Verify</button>
        
        <div id="result" class="result"></div>
        <div id="remaining" class="remaining"></div>
        
        <div class="info">
            <h3>How verification works:</h3>
            <ul>
                <li>3 free checks per IP every 3 hours</li>
                <li>Codes are unique to each product</li>
                <li>Verification confirms product authenticity</li>
            </ul>
        </div>
    </div>
    
    <script>
        async function verify() {
            const code = document.getElementById('code').value.trim();
            const result = document.getElementById('result');
            
            if (!code) {
                result.className = 'result error';
                result.style.display = 'block';
                result.textContent = 'Please enter a code';
                return;
            }
            
            try {
                const response = await fetch('/verify?code=' + encodeURIComponent(code));
                const data = await response.json();
                
                if (data.success) {
                    result.className = 'result success';
                    result.style.display = 'block';
                    result.innerHTML = '<strong>' + data.message + '</strong><br>' + (data.product || '');
                } else {
                    result.className = 'result ' + (data.remaining === 0 ? 'warning' : 'error');
                    result.style.display = 'block';
                    result.textContent = data.message;
                }
                
                if (data.remaining !== undefined) {
                    document.getElementById('remaining').textContent = 'Verifications remaining: ' + data.remaining;
                }
            } catch (e) {
                result.className = 'result error';
                result.style.display = 'block';
                result.textContent = 'Error checking verification';
            }
        }
        
        // Check remaining on load
        fetch('/status').then(r => r.json()).then(data => {
            document.getElementById('remaining').textContent = 'Verifications remaining: ' + data.remaining;
        });
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_verify(self, params):
        """Handle verification request"""
        code = params.get('code', [''])[0].upper().strip()
        ip = get_client_ip(self)
        
        if not code:
            self.send_json({"success": False, "message": "No code provided"})
            return
        
        # Check rate limit
        allowed, count = check_rate_limit(ip)
        
        if not allowed:
            self.send_json({
                "success": False, 
                "message": "Rate limit exceeded. Try again in 3 hours.",
                "remaining": 0
            })
            return
        
        # Verify the code
        result = verify_code(code)
        
        # Increment rate limit (even for invalid codes to prevent brute force)
        increment_rate_limit(ip)
        
        remaining = RATE_LIMIT - (rate_limit_db.get(ip, {}).get("count", 0))
        
        if result["valid"]:
            self.send_json({
                "success": True,
                "message": result["message"],
                "product": result["product"],
                "remaining": remaining
            })
        else:
            self.send_json({
                "success": False,
                "message": result["message"],
                "remaining": remaining
            })
    
    def handle_status(self, params):
        """Get remaining verifications for current IP"""
        ip = get_client_ip(self)
        allowed, count = check_rate_limit(ip)
        remaining = RATE_LIMIT - count if allowed else 0
        
        self.send_json({
            "remaining": remaining,
            "reset_in": rate_limit_db.get(ip, {}).get("reset_time", 0) - time.time()
        })
    
    def handle_products(self):
        """List available products with sample codes"""
        self.send_json({
            "products": {
                "notion-planner": {"name": "Notion Life Planner", "sample": "NOTION-2026-XXXX-ABCD"},
                "ai-prompts": {"name": "500+ AI Prompts Pack", "sample": "AIPROMPT-2026-XXXX-EFGH"},
                "bundle": {"name": "Ultimate Bundle", "sample": "BUNDLE-2026-XXXX-YZ12"}
            }
        })
    
    def send_json(self, data):
        import json
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def generate_product_code(product_id):
    """Generate a new verification code for a product"""
    code = generate_code(product_id)
    verification_db[code] = {
        "product": product_id,
        "valid": True,
        "created": time.time()
    }
    return code

def start_server(port=8080):
    """Start the verification server"""
    server = HTTPServer(('0.0.0.0', port), VerificationHandler)
    print(f"Verification server running on port {port}")
    print(f"Rate limit: {RATE_LIMIT} verifications per {RATE_PERIOD//3600} hours per IP")
    server.serve_forever()

if __name__ == "__main__":
    # Generate codes for all products
    print("Generating product verification codes...")
    for product_id in PRODUCT_CODES:
        code = generate_product_code(product_id)
        print(f"  {product_id}: {code}")
    
    print("\nStarting server...")
    start_server(8080)
