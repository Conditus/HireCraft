# Module for LLM init
import ollama
import os
from openai import OpenAI, APIConnectionError, APITimeoutError
from typing import Optional, Union
from dataclasses import dataclass

@dataclass
class LLMConfig:
    model: str = "gemma4:e4b"
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    api_key: str = os.getenv("OLLAMA_API_KEY", "ollama")
    temperature: float = 0.9
    max_tokens: int = 500 #2048

class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.cfg = config or LLMConfig()
        self.client = OpenAI(
            base_url=self.cfg.base_url,
            api_key=self.cfg.api_key,
            timeout=30.0
        )
        print("got connection")

    def response(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        try:
            print("generating")
            completion = self.client.chat.completions.create(
                model=self.cfg.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.cfg.temperature),
                max_tokens=kwargs.get("max_tokens", self.cfg.max_tokens),
            )
            print("done")
            return completion.choices[0].message.content.strip()
        except APIConnectionError:
            raise RuntimeError("Ollama not initialized or not available. Check `ollama serve`.")
        except APITimeoutError:
            raise RuntimeError("⏳ Respnse timeout. Try to increase max_tokens or timeout (lol).")
        except Exception as e:
            raise RuntimeError(f"❌ LLM fault: {e}")