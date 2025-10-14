from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for mongodb imports
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from openai_client import (
    AudioRequest,
    ImageRequest,
    Message,
    TextRequest,
    client,
)
from mongodb.content import content_controller, ContentModel


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
        repository: str = "unknown",
        commit_sha: str = "unknown",
        branch: str = "unknown",
        summary: str = "Text content generated via OpenAI",
        persist_to_db: bool = True,
    ) -> Dict[str, Any]:
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

        generated_text = response["text"]

        # Optionally persist to MongoDB
        if persist_to_db:
            try:
                from datetime import datetime, timezone

                # Create a summary of the conversation for content field
                conversation_summary = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

                content = ContentModel(
                    repository=repository,
                    commit_sha=commit_sha,
                    branch=branch,
                    summary=summary,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    platform="openai_text",
                    status="generated",
                    content=f"{conversation_summary}\n\nGenerated Response:\n{generated_text}",
                    image_content=[],
                    audio_content=[],
                    video_content=[],
                )

                # Store in MongoDB
                content_id = await content_controller.create(content)

                return {
                    "content_id": content_id,
                    "text": generated_text,
                    "model": model,
                    "storage": "mongodb",
                    "message_count": len(messages),
                    "response_length": len(generated_text),
                }

            except Exception as exc:
                raise Exception(f"Failed to persist text to MongoDB: {exc}") from exc
        else:
            # Return just the text for backward compatibility
            return {
                "text": generated_text,
                "model": model,
                "storage": "none",
            }


class ImageTools:
    @staticmethod
    async def generate_image(
        prompt: str,
        model: Optional[str] = None,
        repository: str = "unknown",
        commit_sha: str = "unknown",
        branch: str = "unknown",
        summary: str = "Image content generated via OpenAI",
    ) -> Dict[str, Any]:
        if not prompt:
            raise ValueError("Image prompt must not be empty")

        request = ImageRequest(
            prompt=prompt,
            model=model,
            response_format="url",
        )

        # Generate image
        result = await client.generate_image(request)

        # Extract image URLs from response
        try:
            image_urls = []
            if result.get("data"):
                for item in result["data"]:
                    if item.get("url"):
                        image_urls.append(item["url"])

            if not image_urls:
                raise Exception("No image URLs returned in response")

            # Create content model for MongoDB
            from datetime import datetime, timezone
            content = ContentModel(
                repository=repository,
                commit_sha=commit_sha,
                branch=branch,
                summary=summary,
                timestamp=datetime.now(timezone.utc).isoformat(),
                platform="openai_image",
                status="generated",
                content=prompt,  # Original prompt
                image_content=image_urls,
                audio_content=[],
                video_content=[],
            )

            # Store in MongoDB
            content_id = await content_controller.create(content)

            return {
                "content_id": content_id,
                "image_urls": image_urls,
                "prompt": prompt,
                "model": model or "default",
                "storage": "mongodb",
                "image_count": len(image_urls),
            }

        except Exception as exc:
            raise Exception(f"Failed to persist image to MongoDB: {exc}") from exc


class AudioTools:
    @staticmethod
    async def generate_speech(
        text: str,
        model: str,
        voice: str,
        repository: str = "unknown",
        commit_sha: str = "unknown",
        branch: str = "unknown",
        summary: str = "Audio content generated via OpenAI TTS",
    ) -> Dict[str, Any]:
        if not text:
            raise ValueError("Input text for speech synthesis must not be empty")

        request = AudioRequest(
            input=text,
            model=model,
            voice=voice,
        )

        # Generate audio file
        result = await client.generate_speech(request)

        # Read the audio file and encode as base64 for MongoDB storage
        try:
            audio_path = Path(result["file_path"])
            audio_bytes = audio_path.read_bytes()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

            # Create content model for MongoDB
            from datetime import datetime, timezone
            content = ContentModel(
                repository=repository,
                commit_sha=commit_sha,
                branch=branch,
                summary=summary,
                timestamp=datetime.now(timezone.utc).isoformat(),
                platform="openai_audio",
                status="generated",
                content=text,  # Original text input
                audio_content=[audio_base64],
                image_content=[],
                video_content=[],
            )

            # Store in MongoDB
            content_id = await content_controller.create(content)

            # Clean up temp file
            audio_path.unlink(missing_ok=True)

            return {
                "content_id": content_id,
                "format": result["format"],
                "content_type": result["content_type"],
                "size_bytes": result["size_bytes"],
                "storage": "mongodb",
                "original_text": text,
                "model": model,
                "voice": voice,
            }

        except Exception as exc:
            raise Exception(f"Failed to persist audio to MongoDB: {exc}") from exc


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
