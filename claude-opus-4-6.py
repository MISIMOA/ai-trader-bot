#!/usr/bin/env python3
"""
AI Trading Bot avec Claude API
Version avec logs de debugging pour Render
"""

import os
import sys
import time

# ============ DEBUGGING ============
print("=" * 60)
print("🤖 DÉMARRAGE DU BOT - DEBUG MODE")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Environment variables: {list(os.environ.keys())}")

# ============ IMPORTS ============
print("\n📦 Importing modules...")
try:
    from anthropic import Anthropic
    print("✅ Anthropic imported successfully")
except ImportError as e:
    print(f"❌ ERROR importing Anthropic: {e}")
    sys.exit(1)

try:
    import time
    print("✅ time imported successfully")
except ImportError as e:
    print(f"❌ ERROR importing time: {e}")
    sys.exit(1)

# ============ CONFIG ============
print("\n🔑 Checking API Key...")
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ ANTHROPIC_API_KEY not found in environment!")
    print("Available env vars:", list(os.environ.keys()))
    sys.exit(1)
else:
    print(f"✅ API Key found (length: {len(api_key)})")

# ============ INITIALIZE CLIENT ============
print("\n🌐 Initializing Anthropic client...")
try:
    client = Anthropic(api_key=api_key)
    print("✅ Anthropic client initialized")
except Exception as e:
    print(f"❌ ERROR initializing client: {e}")
    sys.exit(1)

# ============ BOT LOGIC ============
def run_trading_bot():
    """Fonction principale du bot de trading"""
    print("\n" + "=" * 60)
    print("🚀 RUNNING TRADING BOT")
    print("=" * 60)
    
    conversation_history = []
    
    try:
        print("\n💬 Starting conversation loop...")
        
        # Premier message
        user_message = "Bonjour! Peux-tu m'expliquer ta stratégie de trading?"
        print(f"\n📤 User: {user_message}")
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Appel Claude API
        print("\n🔄 Calling Claude API...")
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                system="You are a trading assistant. Respond in French.",
                messages=conversation_history
            )
            print("✅ API response received")
        except Exception as e:
            print(f"❌ ERROR calling API: {e}")
            sys.exit(1)
        
        assistant_message = response.content[0].text
        print(f"\n📥 Assistant: {assistant_message}")
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        print("\n✅ Bot loop completed successfully!")
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return
    except Exception as e:
        print(f"\n❌ ERROR in bot loop: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ============ MAIN ============
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎯 MAIN ENTRY POINT")
    print("=" * 60)
    
    try:
        run_trading_bot()
        print("\n✅ BOT COMPLETED SUCCESSFULLY")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
