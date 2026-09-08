import os
import json
import requests

def call_claude_api(user_message):
    """Call Claude API directly via HTTP"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    workspace_id = os.getenv("ANTHROPIC_WORKSPACE_ID")
    
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not set")
        return None
    
    if not workspace_id:
        print("❌ ERROR: ANTHROPIC_WORKSPACE_ID not set")
        return None
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "anthropic-workspace-id": workspace_id,
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-opus-4-6",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text']
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

# MAIN ENTRY POINT
if __name__ == "__main__":
    print("🤖 DÉMARRAGE DU BOT - HTTP MODE")
    print(f"✅ API Key found: {len(os.getenv('ANTHROPIC_API_KEY', '')) > 0}")
    print(f"✅ Workspace ID: {os.getenv('ANTHROPIC_WORKSPACE_ID')}")
    
    # Test
    print("\n💬 Sending test message...")
    response = call_claude_api("Bonjour! C'est un test du bot.")
    
    if response:
        print(f"\n✅ Response: {response}")
    else:
        print("\n❌ No response received")
