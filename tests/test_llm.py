"""
Tests for LLM integration components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.llm.llm_client_provider import LLMClient, LLMProvider
from src.llm.llm_token_manager import TokenManager
from src.llm.llm_prompt_templates import PromptTemplates
from src.llm.llm_domain_extractor import DomainExtractor
from src.config.settings import Settings
from src.parsers.tree_sitter_parser import TreeSitterJavaParser


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = Settings()
    settings.openai_api_key = "test-key"
    settings.llm_provider = "openai"
    return settings


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures" / "sample_java"


@pytest.fixture
def sample_classes(fixtures_dir):
    """Parse sample Java files."""
    parser = TreeSitterJavaParser()
    java_files = list(fixtures_dir.glob("*.java"))
    classes = []

    for file_path in java_files:
        content = file_path.read_text()
        java_class = parser.parse_file(str(file_path), content)
        classes.append(java_class)

    return classes


class TestLLMClient:
    """Test the LLMClient class."""

    @patch('src.llm.llm_client_provider.ChatOpenAI')
    def test_client_initialization_openai(self, mock_openai, mock_settings):
        """Test initializing client with OpenAI."""
        client = LLMClient(mock_settings)

        assert client.settings == mock_settings
        assert client.get_provider() == "openai"
        mock_openai.assert_called_once()

    @patch('src.llm.llm_client_provider.AzureChatOpenAI')
    def test_client_initialization_azure_openai(self, mock_azure):
        """Test initializing client with Azure OpenAI."""
        settings = Settings()
        settings.azure_openai_api_key = "test-key"
        settings.azure_openai_endpoint = "https://test.openai.azure.com/"
        settings.azure_openai_deployment_name = "gpt-4"
        settings.llm_provider = "azure_openai"

        client = LLMClient(settings)

        assert client.get_provider() == "azure_openai"
        mock_azure.assert_called_once()

    @patch('src.llm.llm_client_provider.ChatAnthropic')
    def test_client_initialization_anthropic(self, mock_anthropic):
        """Test initializing client with Anthropic."""
        settings = Settings()
        settings.anthropic_api_key = "test-key"
        settings.llm_provider = "anthropic"

        client = LLMClient(settings)

        assert client.get_provider() == "anthropic"
        mock_anthropic.assert_called_once()

    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises error."""
        settings = Settings()
        settings.openai_api_key = None
        settings.llm_provider = "openai"

        with pytest.raises(ValueError, match="OpenAI API key is required"):
            LLMClient(settings)

    def test_missing_azure_endpoint_raises_error(self):
        """Test that missing Azure endpoint raises error."""
        settings = Settings()
        settings.azure_openai_api_key = "test-key"
        settings.azure_openai_endpoint = None
        settings.llm_provider = "azure_openai"

        with pytest.raises(ValueError, match="Azure OpenAI endpoint is required"):
            LLMClient(settings)

    def test_missing_azure_deployment_raises_error(self):
        """Test that missing Azure deployment name raises error."""
        settings = Settings()
        settings.azure_openai_api_key = "test-key"
        settings.azure_openai_endpoint = "https://test.openai.azure.com/"
        settings.azure_openai_deployment_name = None
        settings.llm_provider = "azure_openai"

        with pytest.raises(ValueError, match="Azure OpenAI deployment name is required"):
            LLMClient(settings)

    @patch('src.llm.llm_client_provider.ChatOpenAI')
    def test_generate(self, mock_openai, mock_settings):
        """Test generate method."""
        # Setup mock
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm

        client = LLMClient(mock_settings)
        response = client.generate("Test prompt")

        assert response == "Test response"
        mock_llm.invoke.assert_called_once()

    @patch('src.llm.llm_client_provider.ChatOpenAI')
    def test_generate_with_system_prompt(self, mock_openai, mock_settings):
        """Test generate with system prompt."""
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm

        client = LLMClient(mock_settings)
        response = client.generate(
            prompt="Test prompt",
            system_prompt="You are a helpful assistant"
        )

        assert response == "Test response"
        # Verify that two messages were sent (system + user)
        call_args = mock_llm.invoke.call_args[0][0]
        assert len(call_args) == 2

    @patch('src.llm.llm_client_provider.ChatOpenAI')
    def test_generate_json(self, mock_openai, mock_settings):
        """Test JSON generation."""
        mock_response = Mock()
        mock_response.content = '{"key": "value"}'
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm

        client = LLMClient(mock_settings)
        response = client.generate_json("Test prompt")

        assert response == {"key": "value"}

    @patch('src.llm.llm_client_provider.ChatOpenAI')
    def test_generate_json_with_markdown(self, mock_openai, mock_settings):
        """Test JSON generation with markdown code blocks."""
        mock_response = Mock()
        mock_response.content = '```json\n{"key": "value"}\n```'
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm

        client = LLMClient(mock_settings)
        response = client.generate_json("Test prompt")

        assert response == {"key": "value"}

    @patch('src.llm.llm_client_provider.ChatOpenAI')
    def test_count_tokens(self, mock_openai, mock_settings):
        """Test token counting."""
        mock_llm = Mock()
        mock_llm.get_num_tokens.return_value = 10
        mock_openai.return_value = mock_llm

        client = LLMClient(mock_settings)
        count = client.count_tokens("Test text")

        assert count == 10


class TestTokenManager:
    """Test the TokenManager class."""

    def test_token_manager_initialization(self):
        """Test token manager initialization."""
        manager = TokenManager(model_name="gpt-4", max_context_length=8192)

        assert manager.model_name == "gpt-4"
        assert manager.max_context_length == 8192
        assert manager.max_request_tokens > 0

    def test_count_tokens(self):
        """Test token counting."""
        manager = TokenManager()
        count = manager.count_tokens("Hello world")

        assert count > 0
        assert isinstance(count, int)

    def test_count_tokens_in_messages(self):
        """Test counting tokens in messages."""
        manager = TokenManager()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
        ]

        count = manager.count_tokens_in_messages(messages)
        assert count > 0

    def test_estimate_class_tokens(self, sample_classes):
        """Test estimating tokens for a Java class."""
        manager = TokenManager()

        # Get a sample class
        java_class = sample_classes[0]
        tokens = manager.estimate_class_tokens(java_class)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_chunk_classes(self, sample_classes):
        """Test chunking classes."""
        manager = TokenManager(max_context_length=8192)

        chunks = manager.chunk_classes(
            classes=sample_classes,
            system_prompt="System prompt",
            prompt_template="Template",
        )

        assert len(chunks) > 0
        assert all(isinstance(chunk, list) for chunk in chunks)

    def test_optimize_class_list(self, sample_classes):
        """Test optimizing class list."""
        manager = TokenManager()

        fit, dont_fit = manager.optimize_class_list_for_prompt(
            classes=sample_classes,
            max_tokens=5000,
        )

        assert isinstance(fit, list)
        assert isinstance(dont_fit, list)
        # All classes should be in one of the lists
        assert len(fit) + len(dont_fit) == len(sample_classes)

    def test_create_summary_for_large_class(self, sample_classes):
        """Test creating summary for a large class."""
        manager = TokenManager()

        java_class = sample_classes[0]
        summary = manager.create_summary_for_large_class(java_class)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert java_class.name in summary

    def test_get_usage_stats(self):
        """Test getting usage stats."""
        manager = TokenManager()
        stats = manager.get_usage_stats()

        assert "max_context_length" in stats
        assert "max_request_tokens" in stats
        assert "model" in stats


class TestPromptTemplates:
    """Test the PromptTemplates class."""

    def test_get_system_prompt(self):
        """Test getting system prompt."""
        prompt = PromptTemplates.get_domain_extraction_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "domain" in prompt.lower()

    def test_extract_bounded_contexts_prompt(self, sample_classes):
        """Test bounded contexts prompt."""
        prompt = PromptTemplates.extract_bounded_contexts_prompt(sample_classes)

        assert isinstance(prompt, str)
        assert "bounded context" in prompt.lower()
        assert "JSON" in prompt

    def test_extract_domain_entities_prompt(self, sample_classes):
        """Test domain entities prompt."""
        entities = [cls for cls in sample_classes if cls.category == "Entity"]

        if entities:
            prompt = PromptTemplates.extract_domain_entities_prompt(entities)

            assert isinstance(prompt, str)
            assert "entity" in prompt.lower()
            assert entities[0].name in prompt

    def test_extract_use_cases_prompt(self, sample_classes):
        """Test use cases prompt."""
        controllers = [cls for cls in sample_classes if cls.category == "Controller"]
        services = [cls for cls in sample_classes if cls.category == "Service"]

        prompt = PromptTemplates.extract_use_cases_prompt(controllers, services)

        assert isinstance(prompt, str)
        assert "use case" in prompt.lower()

    def test_extract_business_rules_prompt(self, sample_classes):
        """Test business rules prompt."""
        prompt = PromptTemplates.extract_business_rules_prompt(sample_classes)

        assert isinstance(prompt, str)
        assert "business rule" in prompt.lower()

    def test_extract_api_contracts_prompt(self, sample_classes):
        """Test API contracts prompt."""
        controllers = [cls for cls in sample_classes if cls.category == "Controller"]

        if controllers:
            prompt = PromptTemplates.extract_api_contracts_prompt(controllers)

            assert isinstance(prompt, str)
            assert "endpoint" in prompt.lower() or "API" in prompt


class TestDomainExtractor:
    """Test the DomainExtractor class."""

    @patch('src.llm.llm_domain_extractor.LLMClient')
    def test_domain_extractor_initialization(self, mock_llm_client, mock_settings):
        """Test domain extractor initialization."""
        extractor = DomainExtractor(mock_settings)

        assert extractor.settings == mock_settings

    @patch('src.llm.llm_domain_extractor.LLMClient')
    def test_infer_project_name(self, mock_llm_client, sample_classes):
        """Test inferring project name."""
        extractor = DomainExtractor()

        # Mock the LLM client to avoid actual API calls
        extractor.llm_client = Mock()

        project_name = extractor._infer_project_name(sample_classes)

        assert isinstance(project_name, str)
        assert len(project_name) > 0

    @patch('src.llm.llm_domain_extractor.LLMClient')
    def test_infer_domain(self, mock_llm_client, sample_classes):
        """Test inferring domain."""
        extractor = DomainExtractor()
        extractor.llm_client = Mock()

        domain = extractor._infer_domain(sample_classes, [])

        assert isinstance(domain, str)
        assert len(domain) > 0
