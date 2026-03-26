#!/usr/bin/env python3
"""
AUTONOMOUS AI WORKER - Continuous Background Tasks
This runs like a cron job or daemon
"""

import time
import json
import os
from datetime import datetime
import subprocess

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def check_bitcoin():
    """Monitor Bitcoin address for payments"""
    output = run_command([
        'curl', '-s', 
        'https://mempool.space/api/address/1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ'
    ])
    try:
        data = json.loads(output)
        tx_count = data.get('chain_stats', {}).get('tx_count', 0)
        balance = data.get('chain_stats', {}).get('funded_txo_sum', 0) / 100000000
        
        if tx_count > 0:
            print(f"🎉 PAYMENT DETECTED! {balance} BTC ({tx_count} transactions)!")
            return True
        return False
    except:
        return False

def check_store():
    """Check store status"""
    output = run_command([
        'curl', '-s', 'https://api.github.com/repos/Loran4vr/jekstore'
    ])
    try:
        data = json.loads(output)
        return {
            'stars': data.get('stargazers_count', 0),
            'watchers': data.get('watchers_count', 0),
            'open_issues': data.get('open_issues_count', 0)
        }
    except:
        return None

def check_training():
    """Check if AI training completed"""
    output = run_command([
        'curl', '-s', 
        'https://api.github.com/repos/Loran4vr/jekstore/actions/runs?per_page=1'
    ])
    try:
        data = json.loads(output)
        runs = data.get('workflow_runs', [])
        if runs:
            return {
                'status': runs[0].get('status'),
                'conclusion': runs[0].get('conclusion')
            }
        return None
    except:
        return None

def generate_status():
    """Generate status report"""
    now = datetime.now()
    
    # Check all systems
    bitcoin_ok = check_bitcoin()
    store = check_store()
    training = check_training()
    
    # Create status report
    status = {
        'timestamp': now.isoformat(),
        'bitcoin_payment': bitcoin_ok,
        'store': store,
        'training': training,
        'message': 'AI coworker is monitoring everything'
    }
    
    # Save status to file
    with open('/root/.openclaw/workspace/money-system/ai_status.json', 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"[{now.strftime('%H:%M:%S')}] Status update:")
    print(f"  Bitcoin: {'💰 Payment received!' if bitcoin_ok else 'Monitoring...'}")
    print(f"  Store: {store}")
    print(f"  Training: {training}")
    
    return status

def continuous_monitor(interval=60):
    """Run continuous monitoring loop"""
    print("=" * 60)
    print("🤖 AUTONOMOUS AI WORKER")
    print("=" * 60)
    print(f"Monitoring every {interval} seconds...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            status = generate_status()
            
            # Alert on payment
            if status['bitcoin_payment']:
                print("🚨 PAYMENT ALERT! Check Bitcoin wallet immediately!")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped monitoring")


if __name__ == "__main__":
    # Start continuous monitoring
    continuous_monitor(interval=60)  # Check every minute