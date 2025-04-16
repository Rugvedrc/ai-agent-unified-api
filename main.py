from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
import httpx
import os
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Agent Wrapper API", 
              description="A unified API for creating agents on Vapi.ai and Retell")

# Enum for provider selection
class Provider(str, Enum):
    VAPI = "vapi"
    RETELL = "retell"

# Common request model for creating an agent
class CreateAgentRequest(BaseModel):
    name: str = Field(..., description="Name of the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    provider: Provider = Field(..., description="AI provider to use (vapi or retell)")
    voice_id: Optional[str] = Field(None, description="ID of the voice to be used")
    language: Optional[str] = Field("en-US", description="Language code")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    
    # Optional provider-specific parameters
    openai_config: Optional[Dict[str, Any]] = Field(None, description="OpenAI configuration (if applicable)")
    anthropic_config: Optional[Dict[str, Any]] = Field(None, description="Anthropic configuration (if applicable)")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="Generic LLM configuration")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions for the agent")
    
    # Additional fields that might be specific to one provider but can be mapped
    phone_number: Optional[str] = Field(None, description="Phone number (for Retell)")
    initial_message: Optional[str] = Field(None, description="Initial message for the conversation")
    forwarding_phone_number: Optional[str] = Field(None, description="Forwarding phone number (for Retell)")
    first_message: Optional[str] = Field(None, description="First message for the agent to say")
    avatar_url: Optional[str] = Field(None, description="URL of the avatar image")
    model: Optional[str] = Field(None, description="LLM model to use")

class AgentResponse(BaseModel):
    id: str
    name: str
    provider: Provider
    raw_response: Dict[str, Any]
    # Additional standardized fields can be added here

# Get API keys from environment variables
def get_api_keys():
    vapi_api_key = os.getenv("VAPI_API_KEY")
    retell_api_key = os.getenv("RETELL_API_KEY")
    
    if not vapi_api_key or not retell_api_key:
        raise HTTPException(status_code=500, detail="API keys not configured")
    
    return {"vapi": vapi_api_key, "retell": retell_api_key}

@app.post("/create-agent", response_model=AgentResponse)
async def create_agent(request: CreateAgentRequest, api_keys: Dict[str, str] = Depends(get_api_keys)):
    """
    Create an agent using either Vapi.ai or Retell based on the provider parameter
    """
    if request.provider == Provider.VAPI:
        return await create_vapi_agent(request, api_keys["vapi"])
    elif request.provider == Provider.RETELL:
        return await create_retell_agent(request, api_keys["retell"])
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")

async def create_vapi_agent(request: CreateAgentRequest, api_key: str) -> AgentResponse:
    """Create an agent using Vapi.ai API"""
    # Map the unified request to Vapi.ai format
    vapi_payload = {
        "name": request.name,
        "description": request.description,
        "webhook_url": request.webhook_url,
        "voice_id": request.voice_id,
    }
    
    # Add conditional fields
    if request.llm_config:
        vapi_payload["model"] = {
            "provider": request.llm_config.get("provider", "openai"),
            "model": request.llm_config.get("model", "gpt-4"),
            "temperature": request.llm_config.get("temperature", 0.7),
            "system_prompt": request.custom_instructions or "",
        }
    
    # Add first_message if provided
    if request.first_message or request.initial_message:
        vapi_payload["first_message"] = request.first_message or request.initial_message
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vapi.ai/assistants",
                json=vapi_payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Vapi.ai API error: {response.text}"
                )
            
            vapi_response = response.json()
            
            # Map Vapi.ai response to standard format
            return AgentResponse(
                id=vapi_response.get("assistant_id", ""),
                name=request.name,
                provider=Provider.VAPI,
                raw_response=vapi_response
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Vapi.ai: {str(e)}")

async def create_retell_agent(request: CreateAgentRequest, api_key: str) -> AgentResponse:
    """Create an agent using Retell API"""
    # Map the unified request to Retell format
    retell_payload = {
        "name": request.name,
        "description": request.description or "",
        "voice_id": request.voice_id,
        "webhook_url": request.webhook_url,
        "language": request.language,
    }
    
    # Add phone number if provided
    if request.phone_number:
        retell_payload["phone_number"] = request.phone_number
    
    # Add forwarding phone number if provided
    if request.forwarding_phone_number:
        retell_payload["forwarding_phone_number"] = request.forwarding_phone_number
    
    # Map LLM configuration
    if request.llm_config or request.model:
        llm_model = request.model or (request.llm_config or {}).get("model", "gpt-4")
        llm_provider = (request.llm_config or {}).get("provider", "openai")
        
        retell_payload["llm"] = {
            "provider": llm_provider,
            "model": llm_model,
            "temperature": (request.llm_config or {}).get("temperature", 0.7),
        }
    
    # Add instructions if provided
    if request.custom_instructions:
        retell_payload["instructions"] = request.custom_instructions
    
    # Add avatar if provided
    if request.avatar_url:
        retell_payload["avatar_url"] = request.avatar_url
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.retellai.com/agents",
                json=retell_payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code not in (200, 201):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Retell API error: {response.text}"
                )
            
            retell_response = response.json()
            
            # Map Retell response to standard format
            return AgentResponse(
                id=retell_response.get("id", ""),
                name=request.name,
                provider=Provider.RETELL,
                raw_response=retell_response
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Retell: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Agent Wrapper API", 
            "docs": "/docs",
            "providers": ["vapi", "retell"]}