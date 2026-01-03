"""
Chat API Router

Provides endpoints for real-time chat interaction with the AI system.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel, Field
import requests

from ...config import get_settings


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str
    message_type: str = Field("chat", pattern="^(chat|constraint|directive)$")


@router.post("/{session_id}/message")
async def send_message(session_id: str, request: ChatRequest) -> Dict[str, Any]:
    """Send a message and get AI response."""
    settings = get_settings()

    try:
        response = requests.post(
            f"{settings.llm.api_base}/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": settings.llm.api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": settings.llm.model,
                "max_tokens": settings.llm.max_tokens,
                "messages": [
                    {"role": "user", "content": request.message}
                ]
            },
            timeout=60
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        result = response.json()
        content = result.get("content", [{}])[0].get("text", "No response")

        return {
            "success": True,
            "data": {
                "id": result.get("id", ""),
                "role": "assistant",
                "content": content,
            }
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"LLM proxy error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
