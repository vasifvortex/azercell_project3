import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
# Chat endpoint
# ---------------------------
class ChatRequest(BaseModel):
    query: str
    system: str | None = None  # optional system prompt


@app.post("/chat")
def chat(req: ChatRequest) -> Dict[str, Any]:
    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        # Build messages list (without system role)
        messages = [{"role": "user", "content": [{"type": "text", "text": req.query}]}]

        # Request body for Claude model
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "temperature": 0.7,
            "system": req.system,  # <-- top-level system
            "messages": messages,
        }

        # Invoke model
        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            body=str(body).replace("'", '"'),  # JSON string
        )

        model_response = response["body"].read().decode("utf-8")
        return {"response": model_response}

    except ClientError as e:
        logger.error(f"AWS ClientError: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected: {str(e)}"}
