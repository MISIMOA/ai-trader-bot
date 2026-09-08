#!/usr/bin/env python3
import os, requests

api_key = os.getenv("ANTHROPIC_API_KEY")
workspace_id = os.getenv("ANTHROPIC_WORKSPACE_ID")

headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "anthropic-workspace-id": workspace_id,
    "content-type": "application/json"
}

payload = {
    "model": "claude-opus-4-6",
    "max_tokens": 512,
    "messages": [{"role": "user", "content": "Bonjour, je suis le bot trading."}]
}

try:
    response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=30)
    if response.status_code == 200:
        print("✅ SUCCESS:", response.json()['content'][0]['text'])
    else:
        print("❌ ERROR:", response.status_code, response.text)
except Exception as e:
    print("❌ ERREUR:", str(e))
requests>=2.31.0
anthropic>=0.7.0
