import logging
import os
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Timezone
# ---------------------------
BAKU_TZ = timezone(timedelta(hours=4))

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="FastAPI Backend for RAG Chatbot",
    description="REST API for RAG-based chatbot project",
    version="1.0.0",
    docs_url="/docs",
)

# ---------------------------
# CORS middleware
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Health endpoint
# ---------------------------
@app.get("/health")
def health() -> Dict[str, Any]:
    utc_time = datetime.now(timezone.utc).isoformat()
    baku_time = datetime.now(BAKU_TZ).isoformat()
    return {"status": "healthy", "utc_time": utc_time, "baku_time": baku_time}

# ---------------------------
# Chat request model
# ---------------------------
class ChatRequest(BaseModel):
    query: str
    system: str | None = None  # optional system prompt

# ---------------------------
# Bedrock Knowledge Base client
# ---------------------------
bedrock_kb = boto3.client(
    "bedrock-agent-runtime",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
knowledge_base_id = "JGMPKF6VEI"

def create_request(knowledge_base_id: str, query: str) -> dict:
    """Build the Bedrock KB retrieval request"""
    return {
        "knowledgeBaseId": knowledge_base_id,
        "retrievalQuery": {"text": query},
        "retrievalConfiguration": {
            "vectorSearchConfiguration": {"numberOfResults": 3}
        }
    }

def get_knowledge_base_data(query: str) -> str:
    """Query Bedrock KB and return concatenated results"""
    request_body = create_request(knowledge_base_id, query)
    response = bedrock_kb.retrieve(**request_body)
    results = []
    for item in response.get("results", []):
        content = item.get("documentContent", "")
        results.append(content)
    return "\n".join(results) if results else ""

# ---------------------------
# Helper functions
# ---------------------------
def add_user_message(messages: list, text: str):
    messages.append({"role": "user", "content": [{"type": "text", "text": text}]})

def create_body_json(messages: list, system: str | None = None) -> str:
    return json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0.7,
        "system": system,
        "messages": messages,
    })

# ---------------------------
# Chat endpoint
# ---------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        # Bedrock model client
        client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        # Retrieve knowledge from KB
        kb_text = get_knowledge_base_data(req.query)
        messages = []
        combined_query = f"{req.query}\n\n[KnowledgeBase]: {kb_text}" if kb_text else req.query
        add_user_message(messages, combined_query)

        body_json = create_body_json(messages, req.system)

        # Invoke model with streaming response
        stream = client.invoke_model_with_response_stream(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            contentType="application/json",
            accept="application/json",
            body=body_json,
        )

        stream_body = stream.get("body")

        def event_generator():
            try:
                for event in stream_body:
                    chunk = event.get("chunk")
                    if not chunk:
                        continue
                    decoded = json.loads(chunk.get("bytes").decode("utf-8"))
                    delta = decoded.get("delta", {})
                    text = delta.get("text", "")
                    if text:
                        yield text
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"[ERROR]: {str(e)}"

        return StreamingResponse(event_generator(), media_type="text/plain")

    except ClientError as e:
        logger.error(f"AWS ClientError: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected: {str(e)}"}
