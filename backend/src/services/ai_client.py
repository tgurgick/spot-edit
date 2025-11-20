"""
AI client service for interacting with LLM APIs.

Supports OpenAI and Anthropic APIs with error handling and retries.
"""

import os
import time
from typing import Optional, Dict, Any, Literal
from enum import Enum

try:
    from openai import OpenAI, APIError as OpenAIAPIError, RateLimitError as OpenAIRateLimitError
except ImportError:
    OpenAI = None
    OpenAIAPIError = Exception
    OpenAIRateLimitError = Exception

try:
    from anthropic import Anthropic, APIError as AnthropicAPIError, RateLimitError as AnthropicRateLimitError
except ImportError:
    Anthropic = None
    AnthropicAPIError = Exception
    AnthropicRateLimitError = Exception


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AIClientError(Exception):
    """Base exception for AI client errors."""
    pass


class AIRateLimitError(AIClientError):
    """Raised when rate limit is exceeded."""
    pass


class AIClient:
    """
    Client for interacting with LLM APIs (OpenAI and Anthropic).

    Provides a unified interface for calling different LLM providers with
    automatic retries and error handling.
    """

    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0  # seconds
    DEFAULT_MODEL_OPENAI = "gpt-4-turbo-preview"
    DEFAULT_MODEL_ANTHROPIC = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        provider: AIProvider,
        api_key: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        model: Optional[str] = None,
    ):
        """
        Initialize AI client.

        Args:
            provider: AI provider to use (openai or anthropic)
            api_key: API key (if None, will look for environment variables)
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (uses exponential backoff)
            model: Model name to use (if None, uses default for provider)

        Raises:
            AIClientError: If provider is not supported or dependencies are missing
        """
        self.provider = provider
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Set model
        if model:
            self.model = model
        elif provider == AIProvider.OPENAI:
            self.model = self.DEFAULT_MODEL_OPENAI
        else:
            self.model = self.DEFAULT_MODEL_ANTHROPIC

        # Initialize client based on provider
        if provider == AIProvider.OPENAI:
            if OpenAI is None:
                raise AIClientError(
                    "OpenAI package is not installed. Install it with: pip install openai"
                )
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise AIClientError("OpenAI API key not provided and OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=api_key)

        elif provider == AIProvider.ANTHROPIC:
            if Anthropic is None:
                raise AIClientError(
                    "Anthropic package is not installed. Install it with: pip install anthropic"
                )
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise AIClientError("Anthropic API key not provided and ANTHROPIC_API_KEY not set")
            self.client = Anthropic(api_key=api_key)

        else:
            raise AIClientError(f"Unsupported provider: {provider}")

    def call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Call the LLM with a prompt and optional system message.

        Args:
            prompt: User prompt/message
            system_message: Optional system message to set context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            LLM response text

        Raises:
            AIClientError: If the API call fails after retries
            AIRateLimitError: If rate limit is exceeded
        """
        for attempt in range(self.max_retries):
            try:
                if self.provider == AIProvider.OPENAI:
                    return self._call_openai(prompt, system_message, temperature, max_tokens)
                else:
                    return self._call_anthropic(prompt, system_message, temperature, max_tokens)

            except (OpenAIRateLimitError, AnthropicRateLimitError) as e:
                if attempt == self.max_retries - 1:
                    raise AIRateLimitError(f"Rate limit exceeded after {self.max_retries} attempts") from e
                delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                time.sleep(delay)

            except (OpenAIAPIError, AnthropicAPIError) as e:
                if attempt == self.max_retries - 1:
                    raise AIClientError(f"API error after {self.max_retries} attempts: {str(e)}") from e
                delay = self.retry_delay * (2 ** attempt)
                time.sleep(delay)

            except Exception as e:
                raise AIClientError(f"Unexpected error calling LLM: {str(e)}") from e

        raise AIClientError("Failed to get response from LLM")

    def _call_openai(
        self,
        prompt: str,
        system_message: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call OpenAI API."""
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def _call_anthropic(
        self,
        prompt: str,
        system_message: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Call Anthropic API."""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_message:
            kwargs["system"] = system_message

        response = self.client.messages.create(**kwargs)

        return response.content[0].text


def get_ai_client(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> AIClient:
    """
    Factory function to create an AI client instance.

    Args:
        provider: AI provider name (openai or anthropic). If None, uses AI_PROVIDER env var
        api_key: API key. If None, uses provider-specific env var
        model: Model name. If None, uses default for provider

    Returns:
        Configured AIClient instance

    Raises:
        AIClientError: If provider is invalid or dependencies are missing

    Example:
        >>> client = get_ai_client(provider="openai")
        >>> response = client.call_llm("What is the capital of France?")
    """
    if provider is None:
        provider = os.getenv("AI_PROVIDER", "anthropic")

    try:
        provider_enum = AIProvider(provider.lower())
    except ValueError:
        raise AIClientError(
            f"Invalid provider: {provider}. Must be one of: {', '.join(p.value for p in AIProvider)}"
        )

    return AIClient(provider=provider_enum, api_key=api_key, model=model)
