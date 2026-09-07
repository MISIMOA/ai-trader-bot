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
import sys
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
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
    
    # Récupérer les credentials Anthropic
WORKSPACE_ID = os.getenv("ANTHROPIC_WORKSPACE_ID")
print(f"🔍 WORKSPACE_ID: {WORKSPACE_ID}")
if WORKSPACE_ID:
    import httpx
    http_client = httpx.Client(
        headers={"anthropic-workspace-id": WORKSPACE_ID}
    )
    client = Anthropic(
        api_key=API_KEY,
        httpx_client=http_client
    )
    print("✅ Anthropic client created with workspace ID via httpx")
else:
    client = Anthropic(api_key=API_KEY)
    print("⚠️ Anthropic client created WITHOUT workspace ID")
    
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
    
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": msg}],
    extra_headers={"anthropic-workspace-id": WORKSPACE_ID}
)
        
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

# ===== BOUCLE PRINCIPALE =====
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 RUNNING TRADING BOT")
    print("=" * 80 + "\n")
    
    while True:
        try:
            get_indicators()
        except KeyboardInterrupt:
            print("\n\n🛑 BOT STOPPED")
            break
        except Exception as e:
            print(f"❌ MAIN ERROR: {e}")
            time.sleep(60)
