#!/usr/bin/env python3
"""
🤖 TRADING BOT IA - HTTP DIRECT
Pas d'import Anthropic SDK - requests seulement
"""

import os
import requests
from datetime import datetime

API_KEY = os.getenv("ANTHROPIC_API_KEY")
WORKSPACE_ID = os.getenv("ANTHROPIC_WORKSPACE_ID")
MODEL = "claude-opus-4-6"
API_URL = "https://api.anthropic.com/v1/messages"

def call_claude(msg):
    if not API_KEY or not WORKSPACE_ID:
        print("❌ ERREUR: API_KEY ou WORKSPACE_ID manquants")
        return None
    
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-workspace-id": WORKSPACE_ID,
        "content-type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "max_tokens": 512,
        "messages": [{"role": "user", "content": msg}]
    }
    
    try:
        print("📤 Appel API...")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 BOT DÉMARRAGE")
    print(f"✅ API Key: {bool(API_KEY)}")
    print(f"✅ Workspace: {WORKSPACE_ID}")
    print("\n💬 Test message...")
    
    response = call_claude("Bonjour! Tu es mon bot trading. Explique ta stratégie.")
    
    if response:
        print(f"\n✅ RÉPONSE:\n{response}\n🎉 BOT OK!")
    else:
        print("\n❌ Pas de réponse")
