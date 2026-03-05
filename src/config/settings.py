"""
Configuration settings for the Java to Node.js converter.
Loads settings from environment variables using pydantic-settings.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Provider Configuration
    llm_provider: Literal["openai", "azure_openai", "anthropic"] = Field(
        default="openai", description="LLM provider to use"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_api_base: Optional[str] = Field(default=None, description="OpenAI API base URL (for OpenRouter, etc.)")
    openai_model: str = Field(
        default="gpt-4-turbo-preview", description="OpenAI model to use"
    )
    openai_temperature: float = Field(
        default=0.2, ge=0.0, le=2.0, description="OpenAI temperature parameter"
    )

    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = Field(
        default=None, description="Azure OpenAI API key"
    )
    azure_openai_endpoint: Optional[str] = Field(
        default=None, description="Azure OpenAI endpoint URL"
    )
    azure_openai_deployment_name: Optional[str] = Field(
        default=None, description="Azure OpenAI deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview", description="Azure OpenAI API version"
    )
    azure_openai_temperature: float = Field(
        default=0.2, ge=0.0, le=2.0, description="Azure OpenAI temperature parameter"
    )
    
    # Azure Authentication Configuration
    tenant_id: Optional[str] = Field(default=None, description="Azure Tenant ID")
    client_id: Optional[str] = Field(default=None, description="Azure Client ID")
    client_secret: Optional[str] = Field(default=None, description="Azure Client Secret")
    scope: Optional[str] = Field(default=None, description="Azure OAuth Scope")
    azure_endpoint: Optional[str] = Field(default=None, description="Azure Gateway Endpoint")
    api_version: Optional[str] = Field(default=None, description="Azure API Version")

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-sonnet-4", description="Anthropic model to use"
    )
    anthropic_temperature: float = Field(
        default=0.2, ge=0.0, le=1.0, description="Anthropic temperature parameter"
    )

    # Application Configuration
    max_tokens_per_request: int = Field(
        default=3000, gt=0, description="Maximum tokens per LLM request"
    )
    output_dir: str = Field(default="./output", description="Output directory path")

    # Architecture Preferences
    architecture_pattern: Literal[
        "clean_architecture", "hexagonal", "onion", "layered"
    ] = Field(default="clean_architecture", description="Architecture pattern to use")

    nodejs_framework: Literal["express", "nestjs"] = Field(
        default="express", description="Node.js framework for generated code"
    )

    orm_preference: Literal["typeorm", "sequelize"] = Field(
        default="typeorm", description="ORM to use in generated code"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )

    # RAG / ChromaDB Configuration
    enable_rag: bool = Field(
        default=True,
        description="Enable RAG (Retrieval-Augmented Generation) with ChromaDB",
    )
    chroma_persist_dir: str = Field(
        default="./.chroma_db",
        description="Directory where ChromaDB persists its vector index",
    )
    rag_top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of similar documents to retrieve per RAG query",
    )

    @field_validator("openai_api_key", "anthropic_api_key")
    @classmethod
    def validate_api_keys(cls, v: Optional[str], info) -> Optional[str]:  # type: ignore
        """Validate that appropriate API key is set based on provider."""
        # This will be validated in the root validator
        return v

    @property
    def api_key(self) -> str:
        """Get the appropriate API key based on the selected provider."""
        if self.llm_provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY must be set when using OpenAI provider")
            return self.openai_api_key
        elif self.llm_provider == "azure_openai":
            if not self.azure_openai_api_key:
                raise ValueError("AZURE_OPENAI_API_KEY must be set when using Azure OpenAI provider")
            return self.azure_openai_api_key
        elif self.llm_provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY must be set when using Anthropic provider"
                )
            return self.anthropic_api_key
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    @property
    def model_name(self) -> str:
        """Get the appropriate model name based on the selected provider."""
        if self.llm_provider == "openai":
            return self.openai_model
        elif self.llm_provider == "azure_openai":
            # For Azure, use deployment name
            return self.azure_openai_deployment_name or "gpt-4"
        elif self.llm_provider == "anthropic":
            return self.anthropic_model
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    @property
    def temperature(self) -> float:
        """Get the appropriate temperature based on the selected provider."""
        if self.llm_provider == "openai":
            return self.openai_temperature
        elif self.llm_provider == "azure_openai":
            return self.azure_openai_temperature
        elif self.llm_provider == "anthropic":
            return self.anthropic_temperature
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    @property
    def max_tokens(self) -> int:
        """Get the maximum tokens per request (alias for max_tokens_per_request)."""
        return self.max_tokens_per_request


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    Creates it if it doesn't exist.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    Useful for testing or when environment changes.
    """
    global _settings
    _settings = Settings()
    return _settings
