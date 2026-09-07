#!/usr/bin/env python3
"""
🤖 TRADING BOT IA v2 FINAL CLEAN - CLAUDE API + 7 INDICATEURS
RSI | Bollinger Bands | MACD | FVG | Volume | Order Blocks | DXY
Mode: DÉMO (affichage des décisions, pas de vrai trading)
"""

import os
import time
import json
from datetime import datetime
from anthropic import Anthropic

print("=" * 80)
print("🤖 TRADING BOT IA v2 FINAL CLEAN - DÉMARRAGE")
print("=" * 80)
print(f"⏰ {datetime.now()}")
print()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_ORG_ID = os.getenv("ANTHROPIC_ORG_ID")

print(f"✅ API Key found: {len(ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else 0} chars")
print(f"✅ Workspace ID found: {ANTHROPIC_ORG_ID}")
print()

# Initialiser Anthropic
try:
    if ANTHROPIC_ORG_ID:
        client = Anthropic(
            api_key=ANTHROPIC_API_KEY,
            default_headers={"anthropic-workspace-id": ANTHROPIC_ORG_ID}
        )
        print("✅ Anthropic client initialized with workspace ID header")
    else:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✅ Anthropic client initialized (no workspace ID)")
except Exception as e:
    print(f"❌ Anthropic client error: {e}")
    client = None

conversation_history = []

def calculate_rsi(prices, period=14):
    """RSI - Relative Strength Index"""
    if len(prices) < period + 1:
        return 50
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    seed = deltas[:period]
    up = sum(x for x in seed if x > 0) / period
    down = sum(-x for x in seed if x < 0) / period
    rs = up / down if down > 0 else 0
    rsi = 100 - (100 / (1 + rs)) if down > 0 else 50
    return rsi

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Bollinger Bands"""
    if len(prices) < period:
        return None, None, None
    sma = sum(prices[-period:]) / period
    variance = sum((x - sma) ** 2 for x in prices[-period:]) / period
    std = variance ** 0.5
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return lower, sma, upper

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """MACD"""
    if len(prices) < slow:
        return 0, 0, 0
    ema_fast = sum(prices[-fast:]) / fast
    ema_slow = sum(prices[-slow:]) / slow
    macd_line = ema_fast - ema_slow
    signal_line = macd_line
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_fvg(prices, lookback=5):
    """Fair Value Gap"""
    if len(prices) < lookback:
        return {"count": 0, "strength": 0}
    high = max(prices[-lookback:])
    low = min(prices[-lookback:])
    gap = high - low
    return {"count": 1 if gap > 0 else 0, "strength": round(gap, 2)}

def analyze_volume(volumes, threshold=1.5):
    """Volume Analysis"""
    if len(volumes) < 10:
        return 1.0
    avg = sum(volumes[-10:]) / 10
    current = volumes[-1]
    spike = current / avg if avg > 0 else 1.0
    return round(spike, 2)

def detect_order_blocks(prices, lookback=10):
    """Order Blocks"""
    if len(prices) < lookback:
        return {"support": None, "resistance": None}
    recent = prices[-lookback:]
    return {
        "support": round(min(recent), 2),
        "resistance": round(max(recent), 2)
    }

def get_dxy_trend(current=101.5, previous=101.3):
    """DXY"""
    change = ((current - previous) / previous * 100) if previous > 0 else 0
    trend = "STRONG_DOLLAR" if change > 0 else "WEAK_DOLLAR"
    return trend, round(change, 2)

def ask_claude(market_data):
    """Ask Claude"""
    if not client:
        return {"action": "HOLD", "confidence": 0, "reason": "Client not initialized"}
    
    analysis_prompt = f"""
Vous êtes un trader IA expert. Analysez ces données et décidez:

📊 DONNÉES MARCHÉ:
{json.dumps(market_data, indent=2)}

🎯 DÉCISION (UNE SEULE):
- BUY: RSI < 30 + confluence 5+ indicateurs + volume spike
- SELL: RSI > 70 + confluence 5+ indicateurs + volume spike  
- HOLD: sinon

⚠️ MICRO positions: $3-5 max, SL 5%

RÉPONDEZ EN JSON UNIQUEMENT:
{{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "reason": "courte explication"
}}
"""
    
    conversation_history.append({
        "role": "user",
        "content": analysis_prompt
    })
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=conversation_history
        )
        
        ai_text = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": ai_text
        })
        
        try:
            decision = json.loads(ai_text)
            return decision
        except:
            return {"action": "HOLD", "confidence": 0, "reason": "Parse error"}
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return {"action": "HOLD", "confidence": 0, "reason": f"Error: {e}"}

def main_loop():
    """Main loop"""
    iteration = 0
    
    while True:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"🔄 CYCLE {iteration} - {datetime.now()}")
        print(f"{'='*80}")
        
        try:
            import random
            prices = [100 + i*0.3 + (i % 5)*0.5 + random.uniform(-0.5, 0.5) for i in range(50)]
            volumes = [1000000 + i*5000 + random.randint(-50000, 50000) for i in range(50)]
            
            rsi = calculate_rsi(prices)
            lower, sma, upper = calculate_bollinger_bands(prices)
            macd_line, signal, histogram = calculate_macd(prices)
            fvg = calculate_fvg(prices)
            vol_spike = analyze_volume(volumes)
            ob = detect_order_blocks(prices)
            dxy_trend, dxy_pct = get_dxy_trend()
            
            market_data = {
                "timestamp": datetime.now().isoformat(),
                "rsi": round(rsi, 2),
                "rsi_level": "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL",
                "bollinger": {
                    "lower": round(lower, 2),
                    "middle": round(sma, 2),
                    "upper": round(upper, 2),
                    "price": round(prices[-1], 2)
                },
                "macd": {
                    "line": round(macd_line, 4),
                    "signal": round(signal, 4),
                    "histogram": round(histogram, 4)
                },
                "fvg": fvg,
                "volume_spike": vol_spike,
                "order_blocks": ob,
                "dxy": {
                    "trend": dxy_trend,
                    "change_pct": dxy_pct
                }
            }
            
            print("\n📊 INDICATEURS:")
            print(f"  RSI: {rsi:.2f} ({market_data['rsi_level']})")
            print(f"  BB: [{lower:.2f} | {sma:.2f} | {upper:.2f}]")
            print(f"  MACD: {macd_line:.4f}")
            print(f"  FVG: {fvg['count']}")
            print(f"  Volume: {vol_spike}x")
            print(f"  OB: S:{ob['support']} R:{ob['resistance']}")
            print(f"  DXY: {dxy_trend} ({dxy_pct:+.2f}%)")
            
            print("\n🧠 Consulting Claude...")
            decision = ask_claude(market_data)
            
            print(f"\n✅ DECISION:")
            print(f"  Action: {decision.get('action', 'N/A')}")
            print(f"  Confidence: {decision.get('confidence', 0)}%")
            print(f"  Reason: {decision.get('reason', 'N/A')}")
            
            print(f"\n⏳ Next cycle in 60 seconds...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\n🛑 BOT STOPPED")
            break
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            print("⏳ Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    print("✅ Bot v2 FINAL CLEAN avec 7 indicateurs PRÊT!")
    print("🚀 Starting main loop...\n")
    main_loop()
