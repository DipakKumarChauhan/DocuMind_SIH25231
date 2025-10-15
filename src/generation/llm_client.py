"""
LLM client for generating answers in RAG pipeline.
Supports OpenAI, Google Gemini, and local LLMs via Ollama.
"""

from typing import List, Dict, Any, Optional
import os

from openai import OpenAI
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.core.logger import app_logger
from src.core.exceptions import LLMError


class LLMClient:
    """
    LLM client with multi-provider support (OpenAI, Gemini, Local).
    """
    
    def __init__(
        self,
        provider: str = None,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider ('openai', 'gemini', or 'local')
            api_key: API key for the provider
            model: Model name (defaults to settings)
            temperature: Sampling temperature
        """
        self.provider = provider or settings.llm_provider
        self.temperature = temperature or 0.1
        
        if self.provider == "gemini":
            self._init_gemini(api_key, model)
        elif self.provider == "openai":
            self._init_openai(api_key, model)
        elif self.provider == "local":
            self._init_local(model)
        else:
            raise LLMError(f"Unknown provider: {self.provider}. Use 'openai', 'gemini', or 'local'")
    
    def _init_gemini(self, api_key: str = None, model: str = None):
        """Initialize Google Gemini."""
        self.model = model or settings.gemini_model
        self.api_key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise LLMError(
                "Gemini API key not found. Set GEMINI_API_KEY in .env or environment"
            )
        
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
        self.temperature = self.temperature or settings.gemini_temperature
        
        app_logger.info(f"Using Google Gemini model: {self.model}")
    
    def _init_openai(self, api_key: str = None, model: str = None):
        """Initialize OpenAI."""
        self.model = model or settings.openai_model
        self.api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise LLMError(
                "OpenAI API key not found. Set OPENAI_API_KEY in .env or environment"
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.temperature = self.temperature or settings.openai_temperature
        
        app_logger.info(f"Using OpenAI model: {self.model}")
    
    def _init_local(self, model: str = None):
        """Initialize local LLM (Ollama)."""
        self.model = model or settings.local_llm_model
        self.endpoint = settings.local_llm_endpoint
        
        # Ollama uses OpenAI-compatible API
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key="ollama",  # Ollama doesn't need real API key
        )
        
        app_logger.info(f"Using local LLM: {self.model} at {self.endpoint}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate completion with retry logic.
        
        Args:
            messages: Chat messages in OpenAI format
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.temperature
        
        try:
            app_logger.debug(f"Generating with {self.provider} model {self.model}, temp={temp}")
            
            if self.provider == "gemini":
                return self._generate_gemini(messages, temp, max_tokens)
            else:
                return self._generate_openai_compatible(messages, temp, max_tokens)
            
        except Exception as e:
            app_logger.error(f"LLM generation failed: {e}")
            raise LLMError(f"Failed to generate response: {e}") from e
    
    def _generate_gemini(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate using Google Gemini."""
        # Convert OpenAI-style messages to Gemini format
        prompt_parts = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                # Gemini doesn't have system role, prepend to first user message
                prompt_parts.append(f"Instructions: {content}\n\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Generate with Gemini
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        response = self.client.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        generated_text = response.text
        
        app_logger.debug(f"Generated {len(generated_text)} characters with Gemini")
        
        return generated_text
    
    def _generate_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate using OpenAI or local LLM (OpenAI-compatible)."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        generated_text = response.choices[0].message.content
        
        app_logger.debug(
            f"Generated {len(generated_text)} characters, "
            f"used {response.usage.total_tokens} tokens"
        )
        
        return generated_text
    
    def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = None,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate with system and user messages.
        
        Args:
            system_prompt: System instruction
            user_message: User query
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Generated response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        
        return self.generate(messages, temperature, max_tokens)
