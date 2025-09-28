from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai_client import (
    AudioRequest,
    ImageRequest,
    Message,
    TextRequest,
    client,
)


class TextTools:
    @staticmethod
    async def generate_text(
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        instructions: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        try:
            message_models = [Message(role=msg["role"], content=msg["content"]) for msg in messages]
        except KeyError as exc:
            raise ValueError("Each message must include 'role' and 'content' keys") from exc

        request = TextRequest(
            model=model,
            messages=message_models,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            instructions=instructions,
            stream=stream,
        )
        response = await client.create_text_response(request)
        if not response.get("text"):
            raise Exception("No text returned by OpenAI response")
        return response["text"]


class ImageTools:
    @staticmethod
    async def generate_image(
        prompt: str,
        model: Optional[str] = None,
        n: int = 1,
        size: Optional[str] = None,
        response_format: Optional[str] = None,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not prompt:
            raise ValueError("Image prompt must not be empty")

        request = ImageRequest(
            prompt=prompt,
            model=model,
            n=n,
            size=size,
            response_format=response_format,
            user=user,
        )
        return await client.generate_image(request)


class AudioTools:
    @staticmethod
    async def generate_speech(
        text: str,
        model: str,
        voice: str,
        response_format: Optional[str] = None,
        speed: Optional[float] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not text:
            raise ValueError("Input text for speech synthesis must not be empty")

        request = AudioRequest(
            input=text,
            model=model,
            voice=voice,
            response_format=response_format,
            speed=speed,
            instructions=instructions,
        )
        return await client.generate_speech(request)


class ModelTools:
    @staticmethod
    async def list_models(model_type: Optional[str] = None) -> Dict[str, Any]:
        models: Dict[str, Any] = {
            "text": [
                {"id": "gpt-4o", "description": "Default GPT-4o flagship model"},
                {"id": "gpt-4.1", "description": "Latest GPT-4.1 reasoning model"},
                {"id": "gpt-4o-mini", "description": "Cost-efficient fast GPT-4o variant"},
            ],
            "image": [
                {"id": "gpt-image-1", "description": "Latest multimodal image generator"},
                {"id": "dall-e-3", "description": "High quality illustration model"},
            ],
            "audio": [
                {"id": "gpt-4o-mini-tts", "description": "Text-to-speech voice generation"},
                {"id": "tts-1-hd", "description": "Studio-grade text-to-speech"},
            ],
        }

        if model_type:
            return {model_type: models.get(model_type, [])}

        return models
