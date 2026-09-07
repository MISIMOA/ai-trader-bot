#!/usr/bin/env python3
"""
🤖 TRADING BOT IA - ULTRA SIMPLE VERSION
No crash, simple logs, 7 indicators
"""

import os
import time
import json
import random
from datetime import datetime

print("=" * 80)
print("🤖 TRADING BOT IA - ULTRA SIMPLE - DÉMARRAGE")
print("=" * 80)

# Config
API_KEY = os.getenv("ANTHROPIC_API_KEY")
ORG_ID = os.getenv("ANTHROPIC_ORG_ID")

print(f"✅ API Key: {'présent' if API_KEY else 'MANQUANT'}")
print(f"✅ Org ID: {'présent' if ORG_ID else 'MANQUANT'}")
print()

# Import Anthropic - avec gestion d'erreur
try:
    from anthropic import Anthropic
    print("✅ Anthropic imported successfully")
    
    if ORG_ID:
        client = Anthropic(
            api_key=API_KEY,
            default_headers={"anthropic-workspace-id": ORG_ID}
        )
        print("✅ Anthropic client created with org ID header")
    else:
        client = Anthropic(api_key=API_KEY)
        print("⚠️  Anthropic client created WITHOUT org ID")
except Exception as e:
    print(f"❌ Error creating Anthropic client: {e}")
    client = None

print()
print("=" * 80)
print("🚀 BOT ULTRA SIMPLE - PRÊT À TOURNER")
print("=" * 80)
print()

# Indicateurs simples
def get_indicators():
    return {
        "rsi": round(random.uniform(20, 80), 2),
        "bb_lower": round(random.uniform(100, 110), 2),
        "bb_middle": round(random.uniform(110, 115), 2),
        "bb_upper": round(random.uniform(115, 120), 2),
        "macd": round(random.uniform(0, 5), 4),
        "fvg": random.randint(0, 2),
        "volume": round(random.uniform(0.8, 1.5), 2),
        "support": round(random.uniform(110, 112), 2),
        "resistance": round(random.uniform(116, 118), 2),
        "dxy": "STRONG" if random.random() > 0.5 else "WEAK"
    }

# Boucle principale
iteration = 0
while True:
    try:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"🔄 CYCLE {iteration} - {datetime.now().isoformat()}")
        print(f"{'='*80}")
        
        # Récupérer indicateurs
        ind = get_indicators()
        
        # Afficher indicateurs
        print("\n📊 INDICATEURS:")
        print(f"  RSI: {ind['rsi']}")
        print(f"  BB: [{ind['bb_lower']} | {ind['bb_middle']} | {ind['bb_upper']}]")
        print(f"  MACD: {ind['macd']}")
        print(f"  FVG: {ind['fvg']}")
        print(f"  Volume: {ind['volume']}x")
        print(f"  Support: {ind['support']}")
        print(f"  Resistance: {ind['resistance']}")
        print(f"  DXY: {ind['dxy']}")
        
        # Appel Claude si client ok
        if client:
            print("\n🧠 Consulting Claude...")
            try:
                msg = f"RSI:{ind['rsi']} MACD:{ind['macd']} Volume:{ind['volume']} DXY:{ind['dxy']} - Decision BUY/SELL/HOLD?"
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=100,
                    messages=[{"role": "user", "content": msg}]
                )
                decision = response.content[0].text
                print(f"✅ Claude: {decision[:50]}...")
            except Exception as e:
                print(f"⚠️  Claude error: {str(e)[:80]}")
                decision = "HOLD"
        else:
            print("\n⚠️  Claude client not available - HOLD")
            decision = "HOLD"
        
        print(f"\n✅ DECISION: {decision.split()[0] if decision else 'HOLD'}")
        print(f"\n⏳ Prochain cycle dans 60 secondes...")
        
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 BOT STOPPED")
        break
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print("⏳ Retry dans 60 secondes...")
        time.sleep(60)
