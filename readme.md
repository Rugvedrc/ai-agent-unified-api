# AI Agent Wrapper API

This service provides a unified API for creating AI agents on both Vapi.ai and Retell platforms. Instead of using different APIs with different parameters, you can use a single standardized interface.

## Features

- Create agents on Vapi.ai or Retell using a common API structure
- Standardized parameter mapping between providers
- Simple API that abstracts away platform differences
- Easy deployment with Docker

## Setup Instructions

### Prerequisites

- Python 3.9+
- API keys for both Vapi.ai and Retell

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ai-agent-wrapper.git
   cd ai-agent-wrapper
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file and add your API keys:
   ```
   VAPI_API_KEY=your_vapi_api_key_here
   RETELL_API_KEY=your_retell_api_key_here
   ```

### Running the Service

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

- API Documentation: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json

## API Usage

### Create Agent Endpoint

**POST /create-agent**

Create an agent on either Vapi.ai or Retell using a unified interface.

**Request Body:**

```json
{
  "name": "My Assistant",
  "description": "A helpful assistant",
  "provider": "vapi",  // or "retell"
  "voice_id": "eleven-labs-voice-id",
  "language": "en-US",
  "webhook_url": "https://example.com/webhook",
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7
  },
  "custom_instructions": "You are a helpful assistant who speaks in a friendly tone.",
  "initial_message": "Hello! How can I help you today?"
}
```

**Response:**

```json
{
  "id": "agent-id-from-provider",
  "name": "My Assistant",
  "provider": "vapi",
  "raw_response": {
    // Full response from the provider API
  }
}
```

## Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t ai-agent-wrapper .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env ai-agent-wrapper
   ```

## Testing

You can test the API using the interactive docs at http://localhost:8000/docs or using curl:

```bash
curl -X POST http://localhost:8000/create-agent \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "description": "Test description",
    "provider": "vapi",
    "voice_id": "eleven-labs-voice-id",
    "custom_instructions": "You are a helpful assistant",
    "llm_config": {
      "provider": "openai",
      "model": "gpt-4"
    }
  }'
```