import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test creating a Vapi agent
def test_create_vapi_agent():
    url = "http://localhost:8000/create-agent"
    
    payload = {
        "name": "Test Vapi Agent",
        "description": "A test agent for Vapi",
        "provider": "vapi",
        "voice_id": "eleven-labs-emily",  # Replace with a valid voice ID
        "webhook_url": "https://example.com/webhook",
        "llm_config": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "custom_instructions": "You are a helpful assistant who speaks clearly.",
        "initial_message": "Hello! I'm your virtual assistant. How can I help you today?"
    }
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

# Test creating a Retell agent
def test_create_retell_agent():
    url = "http://localhost:8000/create-agent"
    
    payload = {
        "name": "Test Retell Agent",
        "description": "A test agent for Retell",
        "provider": "retell",
        "voice_id": "retell-voice-id",  # Replace with a valid voice ID
        "language": "en-US",
        "webhook_url": "https://example.com/webhook",
        "phone_number": "+15551234567",  # Optional for Retell
        "forwarding_phone_number": "+15557654321",  # Optional for Retell
        "llm_config": {
            "provider": "anthropic",
            "model": "claude-3-opus-20240229",
            "temperature": 0.5
        },
        "custom_instructions": "You are a helpful phone assistant who answers questions clearly.",
        "avatar_url": "https://example.com/avatar.png"  # Optional for Retell
    }
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

if __name__ == "__main__":
    print("Testing Vapi agent creation...")
    test_create_vapi_agent()
    
    print("\nTesting Retell agent creation...")
    test_create_retell_agent()