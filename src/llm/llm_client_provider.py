"""
LLM client wrapper for OpenAI and Anthropic APIs.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models import BaseChatModel

from src.config.settings import Settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"


class LLMClient:
    """
    Unified client for interacting with LLM providers.
    Supports OpenAI (GPT-4) and Anthropic (Claude).
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize the LLM client.

        Args:
            settings: Application settings (uses default if not provided)
        """
        self.settings = settings or Settings()
        self._oauth_token = None
        self.llm = self._initialize_llm()

    def _get_azure_oauth_token(self) -> str:
        """
        Get OAuth token for Azure using client credentials flow.
        
        Returns:
            OAuth access token
        """
        if not all([
            self.settings.tenant_id,
            self.settings.client_id,
            self.settings.client_secret,
            self.settings.scope
        ]):
            # Fall back to using API key directly if OAuth config not available
            return self.settings.azure_openai_api_key or ""
        
        import msal
        
        # Create MSAL confidential client
        authority = f"https://login.microsoftonline.com/{self.settings.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.settings.client_id,
            authority=authority,
            client_credential=self.settings.client_secret,
        )
        
        # Acquire token
        result = app.acquire_token_for_client(scopes=[self.settings.scope])
        
        if "access_token" in result:
            return result["access_token"]
        else:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise ValueError(f"Failed to acquire Azure OAuth token: {error}")
    
    def _create_azure_http_client(self) -> httpx.Client:
        """
        Create HTTP client with custom authentication for Azure.
        
        Returns:
            Configured HTTP client
        """
        # Get OAuth token
        token = self._get_azure_oauth_token()
        self._oauth_token = token
        
        # Create custom headers with OAuth token
        headers = {
            "Authorization": f"Bearer {token}",
            "api-key": token,  # Some Azure gateways expect this header
        }
        
        # Create HTTP client with custom headers and disabled SSL verification
        return httpx.Client(
            verify=False,
            headers=headers,
            timeout=60.0,
        )

    def _initialize_llm(self) -> BaseChatModel:
        """
        Initialize the appropriate LLM based on settings.

        Returns:
            Initialized LLM client

        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        provider = self.settings.llm_provider

        if provider == LLMProvider.OPENAI:
            if not self.settings.openai_api_key:
                raise ValueError(
                    "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
                )

            # Build kwargs for ChatOpenAI
            openai_kwargs = {
                "model": self.settings.openai_model,
                "temperature": self.settings.temperature,
                "max_tokens": self.settings.max_tokens,
                "api_key": self.settings.openai_api_key,
            }
            
            # Add base_url if specified (for OpenRouter, etc.)
            if self.settings.openai_api_base:
                openai_kwargs["base_url"] = self.settings.openai_api_base
            
            return ChatOpenAI(**openai_kwargs)

        elif provider == LLMProvider.AZURE_OPENAI:
            if not self.settings.azure_openai_endpoint:
                raise ValueError(
                    "Azure OpenAI endpoint is required. Set AZURE_OPENAI_ENDPOINT environment variable."
                )
            if not self.settings.azure_openai_deployment_name:
                raise ValueError(
                    "Azure OpenAI deployment name is required. Set AZURE_OPENAI_DEPLOYMENT_NAME environment variable."
                )

            # Create HTTP client with OAuth authentication
            http_client = self._create_azure_http_client()
            
            # Use a dummy API key since we're using OAuth token in headers
            return AzureChatOpenAI(
                azure_deployment=self.settings.azure_openai_deployment_name,
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_key="oauth-token-used-in-headers",  # Dummy key, actual auth in headers
                api_version=self.settings.azure_openai_api_version,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                http_client=http_client,
            )

        elif provider == LLMProvider.ANTHROPIC:
            if not self.settings.anthropic_api_key:
                raise ValueError(
                    "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable."
                )

            return ChatAnthropic(
                model=self.settings.anthropic_model,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                api_key=self.settings.anthropic_api_key,
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            The LLM's response as a string
        """
        messages = []

        # Add system message if provided
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        # Add user message
        messages.append(HumanMessage(content=prompt))

        # Override settings if provided
        kwargs = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        # Generate response
        if kwargs:
            # Create a new instance with overridden parameters
            llm = self.llm.bind(**kwargs)
            response = llm.invoke(messages)
        else:
            response = self.llm.invoke(messages)

        return response.content

    def generate_with_conversation(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response using a conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Role can be 'system', 'user', or 'assistant'
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            The LLM's response as a string
        """
        # Convert message dicts to LangChain message objects
        langchain_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                raise ValueError(f"Unknown message role: {role}")

        # Override settings if provided
        kwargs = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        # Generate response
        if kwargs:
            llm = self.llm.bind(**kwargs)
            response = llm.invoke(langchain_messages)
        else:
            response = self.llm.invoke(langchain_messages)

        return response.content

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate a JSON response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override

        Returns:
            Parsed JSON response as a dictionary
        """
        import json

        # Add JSON formatting instruction to prompt
        json_instruction = "\n\nPlease respond with valid JSON only. Do not include any explanation or markdown formatting."
        enhanced_prompt = prompt + json_instruction

        response = self.generate(
            prompt=enhanced_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )

        # Try to parse JSON from response
        # Handle cases where LLM returns markdown code blocks
        response = response.strip()

        if response.startswith("```json"):
            response = response[7:]  # Remove ```json
        elif response.startswith("```"):
            response = response[3:]  # Remove ```

        if response.endswith("```"):
            response = response[:-3]  # Remove closing ```

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response}")

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        # Use the LLM's token counter
        return self.llm.get_num_tokens(text)

    def get_model_name(self) -> str:
        """
        Get the name of the current model.

        Returns:
            Model name
        """
        return self.llm.model_name

    def get_provider(self) -> str:
        """
        Get the current LLM provider.

        Returns:
            Provider name
        """
        return self.settings.llm_provider

    def get_max_context_length(self) -> int:
        """
        Get the maximum context length for the current model.

        Returns:
            Maximum context length in tokens
        """
        # Common context lengths for different models
        model_contexts = {
            # OpenAI
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-3.5-turbo": 16385,
            "gpt-35-turbo": 16385,  # Azure naming
            # Anthropic
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-3-5-sonnet-20240620": 200000,
        }

        model_name = self.get_model_name()

        # For Azure, the deployment name might not match standard model names
        # Try to infer from deployment name if available
        if self.settings.llm_provider == "azure_openai":
            deployment_name = self.settings.azure_openai_deployment_name or ""
            # Check if deployment name contains known model identifiers
            for known_model in model_contexts.keys():
                if known_model.replace("-", "").replace(".", "") in deployment_name.replace("-", "").replace(".", "").lower():
                    return model_contexts[known_model]
            # Default for Azure GPT-4
            return 128000

        return model_contexts.get(model_name, 8192)  # Default to 8K if unknown
