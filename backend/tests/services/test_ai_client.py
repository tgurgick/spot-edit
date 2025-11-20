"""
Unit tests for ai_client.py

Tests the AIClient service with mock LLM responses.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.src.services.ai_client import (
    AIClient,
    AIProvider,
    AIClientError,
    AIRateLimitError,
    get_ai_client,
)


class TestAIClient:
    """Test cases for AIClient class."""

    @patch('backend.src.services.ai_client.Anthropic')
    def test_init_anthropic_with_api_key(self, mock_anthropic):
        """Test initializing Anthropic client with API key."""
        client = AIClient(
            provider=AIProvider.ANTHROPIC,
            api_key="test-key-123"
        )

        assert client.provider == AIProvider.ANTHROPIC
        assert client.model == AIClient.DEFAULT_MODEL_ANTHROPIC
        mock_anthropic.assert_called_once_with(api_key="test-key-123")

    @patch('backend.src.services.ai_client.OpenAI')
    def test_init_openai_with_api_key(self, mock_openai):
        """Test initializing OpenAI client with API key."""
        client = AIClient(
            provider=AIProvider.OPENAI,
            api_key="test-key-456"
        )

        assert client.provider == AIProvider.OPENAI
        assert client.model == AIClient.DEFAULT_MODEL_OPENAI
        mock_openai.assert_called_once_with(api_key="test-key-456")

    @patch('backend.src.services.ai_client.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'env-key-789'})
    def test_init_anthropic_from_env(self, mock_anthropic):
        """Test initializing Anthropic client from environment variable."""
        client = AIClient(provider=AIProvider.ANTHROPIC)

        mock_anthropic.assert_called_once_with(api_key="env-key-789")

    @patch('backend.src.services.ai_client.Anthropic')
    @patch.dict(os.environ, {}, clear=True)
    def test_init_anthropic_no_api_key_raises_error(self, mock_anthropic):
        """Test that missing API key raises error."""
        with pytest.raises(AIClientError) as exc_info:
            AIClient(provider=AIProvider.ANTHROPIC)

        assert "api key" in str(exc_info.value).lower()

    @patch('backend.src.services.ai_client.Anthropic')
    def test_custom_model(self, mock_anthropic):
        """Test initializing with custom model."""
        client = AIClient(
            provider=AIProvider.ANTHROPIC,
            api_key="test-key",
            model="claude-custom-model"
        )

        assert client.model == "claude-custom-model"

    @patch('backend.src.services.ai_client.Anthropic')
    def test_custom_retry_settings(self, mock_anthropic):
        """Test initializing with custom retry settings."""
        client = AIClient(
            provider=AIProvider.ANTHROPIC,
            api_key="test-key",
            max_retries=5,
            retry_delay=2.0
        )

        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    @patch('backend.src.services.ai_client.Anthropic')
    def test_call_llm_anthropic(self, mock_anthropic):
        """Test calling Anthropic LLM."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is the AI response")]
        mock_client.messages.create.return_value = mock_response

        # Create client and call
        client = AIClient(provider=AIProvider.ANTHROPIC, api_key="test-key")
        result = client.call_llm(
            prompt="Test prompt",
            system_message="Test system",
            temperature=0.5,
            max_tokens=1000
        )

        # Verify
        assert result == "This is the AI response"
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == client.model
        assert call_kwargs['temperature'] == 0.5
        assert call_kwargs['max_tokens'] == 1000
        assert call_kwargs['system'] == "Test system"
        assert call_kwargs['messages'][0]['role'] == 'user'
        assert call_kwargs['messages'][0]['content'] == "Test prompt"

    @patch('backend.src.services.ai_client.OpenAI')
    def test_call_llm_openai(self, mock_openai):
        """Test calling OpenAI LLM."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = "OpenAI response text"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Create client and call
        client = AIClient(provider=AIProvider.OPENAI, api_key="test-key")
        result = client.call_llm(
            prompt="Test prompt",
            system_message="Test system",
            temperature=0.7,
            max_tokens=1500
        )

        # Verify
        assert result == "OpenAI response text"
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == client.model
        assert call_kwargs['temperature'] == 0.7
        assert call_kwargs['max_tokens'] == 1500
        assert len(call_kwargs['messages']) == 2
        assert call_kwargs['messages'][0]['role'] == 'system'
        assert call_kwargs['messages'][1]['role'] == 'user'

    @patch('backend.src.services.ai_client.Anthropic')
    def test_call_llm_without_system_message(self, mock_anthropic):
        """Test calling LLM without system message."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        client = AIClient(provider=AIProvider.ANTHROPIC, api_key="test-key")
        result = client.call_llm(prompt="Test")

        call_kwargs = mock_client.messages.create.call_args[1]
        assert 'system' not in call_kwargs or call_kwargs.get('system') is None

    @patch('backend.src.services.ai_client.Anthropic')
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_retry_on_rate_limit(self, mock_sleep, mock_anthropic):
        """Test retry logic on rate limit error."""
        from backend.src.services.ai_client import AnthropicRateLimitError

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Fail twice, then succeed
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Success")]
        mock_client.messages.create.side_effect = [
            AnthropicRateLimitError("Rate limit"),
            AnthropicRateLimitError("Rate limit"),
            mock_response
        ]

        client = AIClient(provider=AIProvider.ANTHROPIC, api_key="test-key", max_retries=3)
        result = client.call_llm(prompt="Test")

        assert result == "Success"
        assert mock_client.messages.create.call_count == 3
        assert mock_sleep.call_count == 2  # Slept twice before success

    @patch('backend.src.services.ai_client.Anthropic')
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_anthropic):
        """Test that max retries raises error."""
        from backend.src.services.ai_client import AnthropicRateLimitError

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = AnthropicRateLimitError("Rate limit")

        client = AIClient(provider=AIProvider.ANTHROPIC, api_key="test-key", max_retries=2)

        with pytest.raises(AIRateLimitError):
            client.call_llm(prompt="Test")

        assert mock_client.messages.create.call_count == 2


class TestGetAIClient:
    """Test cases for get_ai_client factory function."""

    @patch('backend.src.services.ai_client.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_client_default_provider(self, mock_anthropic):
        """Test getting client with default provider."""
        client = get_ai_client()

        assert client.provider == AIProvider.ANTHROPIC

    @patch('backend.src.services.ai_client.OpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'AI_PROVIDER': 'openai'})
    def test_get_client_from_env(self, mock_openai):
        """Test getting client from environment variable."""
        client = get_ai_client()

        assert client.provider == AIProvider.OPENAI

    @patch('backend.src.services.ai_client.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_client_explicit_provider(self, mock_anthropic):
        """Test getting client with explicit provider."""
        client = get_ai_client(provider="anthropic")

        assert client.provider == AIProvider.ANTHROPIC

    def test_get_client_invalid_provider(self):
        """Test that invalid provider raises error."""
        with pytest.raises(AIClientError) as exc_info:
            get_ai_client(provider="invalid-provider")

        assert "invalid provider" in str(exc_info.value).lower()

    @patch('backend.src.services.ai_client.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_client_with_model(self, mock_anthropic):
        """Test getting client with custom model."""
        client = get_ai_client(provider="anthropic", model="custom-model")

        assert client.model == "custom-model"
