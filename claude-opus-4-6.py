#!/usr/bin/env python3
"""
🤖 TRADING BOT IA - HTTP DIRECT
Pas d'import Anthropic SDK - requests seulement
"""

import os
import requests
import json

API_KEY = os.getenv("ANTHROPIC_API_KEY")
WORKSPACE_ID = os.getenv("ANTHROPIC_WORKSPACE_ID")
MODEL = "claude-opus-4-6"
API_URL = "https://api.anthropic.com/v1/messages"

def call_claude(msg):
    """Call Claude API directly via HTTP"""
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
            data = response.json()
            return data['content'][0]['text']
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BOT TRADING IA - DÉMARRAGE")
    print("=" * 60)
    
    print(f"✅ API Key présent: {bool(API_KEY)}")
    print(f"✅ Workspace ID: {WORKSPACE_ID}")
    print(f"✅ Modèle: {MODEL}")
    
    print("\n💬 Démarrage conversation...")
    
    test_msg = "Bonjour! Tu es mon bot trading. Explique moi brièvement ta stratégie."
    print(f"\n📝 Message test: {test_msg}")
    
    response = call_claude(test_msg)
    
    if response:
        print(f"\n✅ RÉPONSE REÇUE:\n{response}")
        print("\n🎉 BOT OPÉRATIONNEL - HTTP DIRECT OK!")
    else:
        print("\n❌ Pas de réponse - Vérifier les logs Render")
    
    print("\n" + "=" * 60)
