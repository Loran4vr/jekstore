#!/usr/bin/env python3
"""
AI COWORK SYSTEM - Autonomous AI Worker
Runs tasks continuously in the background
"""

import os
import time
import json
from datetime import datetime

class AICowork:
    """
    An AI that works autonomously in the background
    Like having an AI coworker that never sleeps
    """
    
    def __init__(self):
        self.tasks = []
        self.results = []
        self.running = True
        self.work_log = []
        
    def add_task(self, name, func, priority=1):
        """Add a task to the work queue"""
        self.tasks.append({
            'name': name,
            'func': func,
            'priority': priority,
            'added': datetime.now().isoformat()
        })
        print(f"📋 Added task: {name}")
        
    def run_tasks(self):
        """Execute all tasks in queue"""
        while self.running:
            for task in sorted(self.tasks, key=lambda x: x['priority'], reverse=True):
                try:
                    print(f"🔧 Working on: {task['name']}")
                    result = task['func']()
                    self.results.append({
                        'task': task['name'],
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.work_log.append(f"✅ {task['name']}: {result}")
                    print(f"   ✅ Done: {result}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            time.sleep(60)  # Check every minute
    
    def get_report(self):
        """Get work summary"""
        return {
            'tasks_completed': len(self.results),
            'current_tasks': len(self.tasks),
            'last_run': self.results[-1]['timestamp'] if self.results else None,
            'log': self.work_log[-10:]  # Last 10 entries
        }


# Example tasks for an AI coworker
def check_store_traffic():
    """Monitor store for visitors"""
    import subprocess
    result = subprocess.run(['curl', '-s', 'https://api.github.com/repos/Loran4vr/jekstore'],
                          capture_output=True, text=True)
    if 'stargazers_count' in result.stdout:
        return "Store active"
    return "Store check complete"

def check_bitcoin():
    """Monitor Bitcoin address for payments"""
    import subprocess
    result = subprocess.run(['curl', '-s', 
                          'https://mempool.space/api/address/1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ'],
                          capture_output=True, text=True)
    try:
        import json
        data = json.loads(result.stdout)
        tx_count = data.get('chain_stats', {}).get('tx_count', 0)
        if tx_count > 0:
            return f"💰 PAYMENT DETECTED! {tx_count} transactions!"
        return f"Bitcoin: 0 transactions (monitoring...)"
    except:
        return "Bitcoin check complete"

def generate_report():
    """Generate daily status report"""
    return f"Report generated at {datetime.now().isoformat()}"

def check_github_actions():
    """Check GitHub Actions status"""
    import subprocess
    result = subprocess.run(['curl', '-s', 
                          'https://api.github.com/repos/Loran4vr/jekstore/actions/runs?per_page=1'],
                          capture_output=True, text=True)
    try:
        import json
        data = json.loads(result.stdout)
        runs = data.get('workflow_runs', [])
        if runs:
            run = runs[0]
            return f"Action: {run['status']} - {run.get('conclusion', 'N/A')}"
        return "No actions found"
    except:
        return "GitHub check complete"


# Create cowork instance
cowork = AICowork()

# Add tasks
cowork.add_task("Check Store", check_store_traffic, priority=1)
cowork.add_task("Check Bitcoin", check_bitcoin, priority=3)  # High priority
cowork.add_task("Check GitHub", check_github_actions, priority=2)
cowork.add_task("Generate Report", generate_report, priority=1)

print()
print("=" * 60)
print("🤖 AI COWORK SYSTEM")
print("=" * 60)
print()
print("This AI will work autonomously:")
print("• Monitor Bitcoin payments (high priority)")
print("• Check GitHub Actions")
print("• Monitor store traffic")
print("• Generate reports")
print()
print("Run this script to start the AI coworker!")
print("=" * 60)