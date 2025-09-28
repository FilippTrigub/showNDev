from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from config import config


class Message(BaseModel):
    role: str
    content: str

    def to_payload(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content}


class TextRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_output_tokens: Optional[int] = Field(default=None, ge=1)
    stream: bool = False
    instructions: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model,
            "input": [message.to_payload() for message in self.messages],
        }

        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        if self.max_output_tokens is not None:
            payload["max_output_tokens"] = self.max_output_tokens
        if self.instructions:
            payload["instructions"] = self.instructions
        if self.stream:
            payload["stream"] = self.stream

        return payload


class ImageRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    response_format: Optional[str] = None
    user: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"prompt": self.prompt}
        if self.model:
            payload["model"] = self.model
        return payload


class AudioRequest(BaseModel):
    input: str
    model: str
    voice: str

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "input": self.input,
            "model": self.model,
            "voice": self.voice,
        }
        return payload


class OpenAIClient:
    """Thin wrapper around OpenAI's REST API for MCP tooling."""

    def __init__(self) -> None:
        headers = {"Content-Type": "application/json", **config.auth_header}
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=headers,
        )

    async def create_text_response(self, request: TextRequest) -> Dict[str, Any]:
        try:
            response = await self.client.post("/responses", json=request.to_payload())
            response.raise_for_status()
            data = response.json()
            return {"text": self._extract_text(data), "raw": data}
        except httpx.HTTPStatusError as exc:
            raise Exception(self._format_error(exc)) from exc
        except Exception as exc:
            raise Exception(f"OpenAI text generation failed: {exc}") from exc

    async def generate_image(self, request: ImageRequest) -> Dict[str, Any]:
        try:
            response = await self.client.post("/images/generations", json=request.to_payload(), timeout=90)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise Exception(self._format_error(exc)) from exc
        except Exception as exc:
            raise Exception(f"OpenAI image generation failed: {exc}") from exc

    async def generate_speech(self, request: AudioRequest) -> Dict[str, Any]:
        try:
            response = await self.client.post("/audio/speech", json=request.to_payload(), timeout=90)
            response.raise_for_status()
            audio_bytes = response.content
            b64_audio = base64.b64encode(audio_bytes).decode("ascii")
            return {
                "audio_base64": b64_audio,
                "format": request.response_format or "mp3",
                "content_type": response.headers.get("content-type", "audio/mpeg"),
                "size_bytes": len(audio_bytes),
            }
        except httpx.HTTPStatusError as exc:
            raise Exception(self._format_error(exc)) from exc
        except Exception as exc:
            raise Exception(f"OpenAI speech synthesis failed: {exc}") from exc

    async def close(self) -> None:
        await self.client.aclose()

    @staticmethod
    def _extract_text(payload: Dict[str, Any]) -> str:
        outputs: List[str] = []
        for item in payload.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    text = content.get("text") or content.get("output_text")
                    if text:
                        outputs.append(text)
            elif item.get("type") in {"output_text", "text"}:
                text_value = item.get("text") or item.get("output_text")
                if text_value:
                    outputs.append(text_value)
        return "".join(outputs).strip()

    @staticmethod
    def _format_error(exc: httpx.HTTPStatusError) -> str:
        detail = None
        try:
            detail = exc.response.json()
        except ValueError:
            detail = exc.response.text
        return (
            "OpenAI API request failed: "
            f"{exc.response.status_code} - {detail}"
        )


client = OpenAIClient()
