#!/usr/bin/env python3
"""
🤖 TRADING BOT IA v2 - CLAUDE API + 7 INDICATEURS
RSI | Bollinger Bands | MACD | FVG | Volume | Order Blocks | DXY
Mode: DÉMO (affichage des décisions, pas de vrai trading)
"""

import os
import time
import json
from datetime import datetime
from anthropic import Anthropic

print("=" * 80)
print("🤖 TRADING BOT IA v2 - DÉMARRAGE")
print("=" * 80)
print(f"⏰ {datetime.now()}")
print()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_ORG_ID = os.getenv("ANTHROPIC_ORG_ID")

# Initialiser Anthropic
client = Anthropic(api_key=ANTHROPIC_API_KEY)
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
    return {"count": 1 if gap > 0 else 0, "strength": gap}

def analyze_volume(volumes, threshold=1.5):
    """Volume Analysis - détecte pics (institutions)"""
    if len(volumes) < 10:
        return 1.0
    avg = sum(volumes[-10:]) / 10
    current = volumes[-1]
    spike = current / avg if avg > 0 else 1.0
    return spike

def detect_order_blocks(prices, lookback=10):
    """Order Blocks"""
    if len(prices) < lookback:
        return {"support": None, "resistance": None}
    recent = prices[-lookback:]
    return {
        "support": min(recent),
        "resistance": max(recent)
    }

def get_dxy_trend(current=101.5, previous=101.3):
    """DXY - Dollar Index"""
    change = ((current - previous) / previous * 100) if previous > 0 else 0
    trend = "STRONG_DOLLAR" if change > 0 else "WEAK_DOLLAR"
    return trend, round(change, 2)

def ask_claude(market_data):
    """Envoyer les données à Claude pour décision"""
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
    """Boucle principale"""
    iteration = 0
    
    while True:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"🔄 CYCLE {iteration} - {datetime.now()}")
        print(f"{'='*80}")
        
        try:
            # Mock data (en production: récupérer des APIs réelles)
            prices = [100 + i*0.3 + (i % 5)*0.5 for i in range(50)]
            volumes = [1000000 + i*5000 for i in range(50)]
            
            # Calculer les indicateurs
            rsi = calculate_rsi(prices)
            lower, sma, upper = calculate_bollinger_bands(prices)
            macd_line, signal, histogram = calculate_macd(prices)
            fvg = calculate_fvg(prices)
            vol_spike = analyze_volume(volumes)
            ob = detect_order_blocks(prices)
            dxy_trend, dxy_pct = get_dxy_trend()
            
            # Préparer les données pour Claude
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
                "volume_spike": round(vol_spike, 2),
                "order_blocks": {
                    "support": round(ob["support"], 2),
                    "resistance": round(ob["resistance"], 2)
                },
                "dxy": {
                    "trend": dxy_trend,
                    "change_pct": dxy_pct
                }
            }
            
            # Afficher les indicateurs
            print("\n📊 INDICATEURS:")
            print(f"  RSI: {rsi:.2f} ({market_data['rsi_level']})")
            print(f"  BB: [{lower:.2f} | {sma:.2f} | {upper:.2f}]")
            print(f"  MACD: {macd_line:.4f} (signal: {signal:.4f})")
            print(f"  FVG: {fvg['count']} detected")
            print(f"  Volume: {vol_spike:.2f}x (spike)")
            print(f"  Order Blocks: S:{ob['support']:.2f} R:{ob['resistance']:.2f}")
            print(f"  DXY: {dxy_trend} ({dxy_pct:+.2f}%)")
            
            # Demander à Claude
            print("\n🧠 Consultation Claude...")
            decision = ask_claude(market_data)
            
            print(f"\n✅ DÉCISION:")
            print(f"  Action: {decision.get('action', 'N/A')}")
            print(f"  Confiance: {decision.get('confidence', 0)}%")
            print(f"  Raison: {decision.get('reason', 'N/A')}")
            
            # Attendre avant le prochain cycle
            print(f"\n⏳ Prochain cycle dans 60 secondes...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\n🛑 BOT ARRÊTÉ")
            break
        except Exception as e:
            print(f"\n❌ ERREUR: {e}")
            print("⏳ Retry dans 60 secondes...")
            time.sleep(60)

if __name__ == "__main__":
    print("✅ Bot v2 avec 7 indicateurs PRÊT!")
    print("🚀 Démarrage de la boucle principale...\n")
    main_loop()
