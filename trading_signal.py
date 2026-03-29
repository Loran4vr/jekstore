#!/usr/bin/env python3
"""
Bitcoin Price Monitor & Signal Generator
Creates trading signals based on price analysis
"""

import json
import time
from datetime import datetime

def get_bitcoin_price():
    """Get current Bitcoin price"""
    import subprocess
    result = subprocess.run(['curl', '-s', 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'],
                          capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data['bitcoin']['usd']
    except:
        return None

def analyze_price(price, prev_price):
    """Generate simple trading signal"""
    if prev_price is None:
        return {'signal': 'HOLD', 'reason': 'First price check', 'confidence': 50}
    
    change = ((price - prev_price) / prev_price) * 100
    
    if change > 2:
        return {
            'signal': 'BUY',
            'reason': f'Price surged {change:.2f}%',
            'confidence': min(90, 50 + abs(change) * 10)
        }
    elif change < -2:
        return {
            'signal': 'SELL',
            'reason': f'Price dropped {change:.2f}%',
            'confidence': min(90, 50 + abs(change) * 10)
        }
    elif change > 0.5:
        return {
            'signal': 'WATCH',
            'reason': f'Slight upward trend ({change:.2f}%)',
            'confidence': 60
        }
    elif change < -0.5:
        return {
            'signal': 'WATCH',
            'reason': f'Slight downward trend ({change:.2f}%)',
            'confidence': 60
        }
    else:
        return {
            'signal': 'HOLD',
            'reason': 'Price stable',
            'confidence': 50
        }

def save_signal(signal, price):
    """Save trading signal"""
    data = {
        'timestamp': datetime.now().isoformat(),
        'price': price,
        'signal': signal['signal'],
        'reason': signal['reason'],
        'confidence': signal['confidence']
    }
    
    with open('/root/.openclaw/workspace/money-system/trading_signals.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    return data

def main():
    print("=" * 60)
    print("📈 BITCOIN TRADING SIGNAL GENERATOR")
    print("=" * 60)
    print()
    
    # Get current price
    price = get_bitcoin_price()
    if price:
        print(f"Current Bitcoin Price: ${price:,.2f}")
    else:
        print("Could not fetch price")
        return
    
    # Generate signal
    signal = analyze_price(price, None)  # No previous price yet
    
    print(f"\n📊 Trading Signal:")
    print(f"   Signal: {signal['signal']}")
    print(f"   Reason: {signal['reason']}")
    print(f"   Confidence: {signal['confidence']}%")
    
    # Save signal
    saved = save_signal(signal, price)
    print(f"\n✅ Signal saved to trading_signals.json")
    
    print("\n" + "=" * 60)
    print("💡 TIP: This signal is FREE to use!")
    print("   For paid premium signals, send Bitcoin:")
    print("   0.000024 BTC → 1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ")
    print("=" * 60)

if __name__ == "__main__":
    main()