import os
import httpx
from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """
        Generates text given a system prompt and a user prompt.
        """
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        # Using Gemini v1beta API
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        # For Gemini, system instructions are passed in systemInstruction field.
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": self.api_key
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_prompt}
                ]
            },
            "generationConfig": {
                "temperature": temperature
            }
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_url, headers=headers, params=params, json=payload)
                response.raise_for_status()
                data = response.json()
                # Parse gemini response
                parts = data["candidates"][0]["content"]["parts"]
                text = "".join(part["text"] for part in parts)
                return text
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {str(e)}")


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4096,
            "temperature": temperature
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {str(e)}")


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider based on env variables.
    """
    provider_name = os.environ.get("LLM_PROVIDER", "").lower()
    api_key = os.environ.get("API_KEY")
    model = os.environ.get("MODEL")

    if provider_name == "openai":
        return OpenAIProvider(api_key, model or "gpt-4o")
    elif provider_name == "gemini":
        return GeminiProvider(api_key, model or "gemini-2.5-flash")
    elif provider_name == "anthropic":
        return AnthropicProvider(api_key, model or "claude-3-5-sonnet-20241022")
        
    raise ValueError("You must provide a valid AI Provider and API Key")
