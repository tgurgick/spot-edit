"""AI/LLM client for field detection and natural language processing."""
import os
from typing import Optional, Dict, Any
from enum import Enum


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


def get_ai_provider() -> AIProvider:
    """
    Determine which AI provider to use based on environment variables.

    Returns:
        AIProvider enum value
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return AIProvider.ANTHROPIC
    elif os.getenv("OPENAI_API_KEY"):
        return AIProvider.OPENAI
    else:
        raise ValueError("No AI API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")


def get_ai_client():
    """
    Get the appropriate AI client based on environment configuration.

    Returns:
        AI client instance
    """
    provider = get_ai_provider()

    if provider == AIProvider.ANTHROPIC:
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            return anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")

    elif provider == AIProvider.OPENAI:
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            return openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")


def call_llm(
    prompt: str,
    system_message: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.7
) -> str:
    """
    Call the LLM with a prompt and get a response.

    Args:
        prompt: The user prompt
        system_message: Optional system message to set context
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0-1)

    Returns:
        LLM response text
    """
    provider = get_ai_provider()
    client = get_ai_client()

    try:
        if provider == AIProvider.ANTHROPIC:
            messages = [{"role": "user", "content": prompt}]

            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message or "You are a helpful assistant.",
                messages=messages
            )

            return response.content[0].text

        elif provider == AIProvider.OPENAI:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Error calling LLM: {str(e)}")


async def call_llm_async(
    prompt: str,
    system_message: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.7
) -> str:
    """
    Async version of call_llm for use in async contexts.

    Args:
        prompt: The user prompt
        system_message: Optional system message
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature

    Returns:
        LLM response text
    """
    # For now, just call the sync version
    # In production, would use async clients
    return call_llm(prompt, system_message, max_tokens, temperature)
