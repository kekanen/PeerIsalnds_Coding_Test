"""
Token counting and management for LLM requests.
"""

from typing import List, Dict, Tuple
import tiktoken
from src.models.java_models import JavaClass


class TokenManager:
    """
    Manages token counting and chunking for LLM requests.
    Ensures requests stay within context window limits.
    """

    def __init__(self, model_name: str = "gpt-4", max_context_length: int = 8192):
        """
        Initialize the token manager.

        Args:
            model_name: Name of the model (for encoding)
            max_context_length: Maximum context length in tokens
        """
        self.model_name = model_name
        self.max_context_length = max_context_length

        # Reserve tokens for response
        self.max_response_tokens = 4000
        self.max_request_tokens = max_context_length - self.max_response_tokens

        # Initialize tokenizer
        self.encoding = self._get_encoding()

    def _get_encoding(self):
        """Get the appropriate tokenizer encoding for the model."""
        try:
            # Handle None or empty model name
            if not self.model_name:
                return tiktoken.get_encoding("cl100k_base")

            # Try to get exact model encoding
            return tiktoken.encoding_for_model(self.model_name)
        except (KeyError, AttributeError):
            # Fall back to cl100k_base encoding (used by GPT-4 and GPT-3.5-turbo)
            # This works for Azure deployments and unknown models
            return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def count_tokens_in_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        Count tokens in a list of messages.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Total token count
        """
        # Format messages as they would be sent to the API
        # Each message has overhead: role, content, formatting tokens
        total_tokens = 0

        for message in messages:
            # Add tokens for role
            total_tokens += 4  # Overhead per message

            # Add tokens for content
            content = message.get("content", "")
            total_tokens += self.count_tokens(content)

        # Add overhead for message array
        total_tokens += 2

        return total_tokens

    def estimate_class_tokens(self, java_class: JavaClass, include_body: bool = False) -> int:
        """
        Estimate the number of tokens needed to represent a Java class.

        Args:
            java_class: The JavaClass to estimate
            include_body: Whether to include method bodies

        Returns:
            Estimated token count
        """
        # Build a string representation
        parts = []

        # Package and imports
        parts.append(f"Package: {java_class.package}")
        parts.append(f"Imports: {len(java_class.imports)} imports")

        # Class declaration
        parts.append(f"Class: {java_class.name} ({java_class.type})")
        if java_class.extends:
            parts.append(f"Extends: {java_class.extends}")
        if java_class.implements:
            parts.append(f"Implements: {', '.join(java_class.implements)}")

        # Annotations
        for ann in java_class.annotations:
            parts.append(f"@{ann.name}{ann.arguments}")

        # Fields
        for field in java_class.fields:
            field_str = f"{field.name}: {field.type}"
            for ann in field.annotations:
                field_str += f" @{ann.name}{ann.arguments}"
            parts.append(field_str)

        # Methods
        for method in java_class.methods:
            params = ", ".join([f"{p.name}: {p.type}" for p in method.parameters])
            method_str = f"{method.name}({params}): {method.return_type}"

            for ann in method.annotations:
                method_str += f" @{ann.name}{ann.arguments}"

            parts.append(method_str)

            if include_body and method.body:
                parts.append(method.body[:200])  # Truncate long bodies

        representation = "\n".join(parts)
        return self.count_tokens(representation)

    def chunk_classes(
        self,
        classes: List[JavaClass],
        system_prompt: str,
        prompt_template: str,
        safety_margin: int = 500,
    ) -> List[List[JavaClass]]:
        """
        Split classes into chunks that fit within token limits.

        Args:
            classes: List of JavaClass objects to chunk
            system_prompt: System prompt text
            prompt_template: Prompt template text
            safety_margin: Extra tokens to reserve for safety

        Returns:
            List of class chunks, each within token limits
        """
        # Calculate overhead
        system_tokens = self.count_tokens(system_prompt)
        template_tokens = self.count_tokens(prompt_template)
        overhead = system_tokens + template_tokens + safety_margin

        available_tokens = self.max_request_tokens - overhead

        chunks = []
        current_chunk = []
        current_tokens = 0

        for cls in classes:
            class_tokens = self.estimate_class_tokens(cls)

            if current_tokens + class_tokens > available_tokens:
                # Current chunk is full, start a new one
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = [cls]
                current_tokens = class_tokens
            else:
                # Add to current chunk
                current_chunk.append(cls)
                current_tokens += class_tokens

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def optimize_class_list_for_prompt(
        self,
        classes: List[JavaClass],
        max_tokens: int,
    ) -> Tuple[List[JavaClass], List[JavaClass]]:
        """
        Optimize a list of classes to fit within token limit.
        Returns classes that fit and classes that don't.

        Args:
            classes: List of classes to optimize
            max_tokens: Maximum tokens allowed

        Returns:
            Tuple of (classes_that_fit, classes_that_dont_fit)
        """
        classes_that_fit = []
        classes_that_dont_fit = []
        current_tokens = 0

        # Sort classes by importance (entities and controllers first)
        priority_order = ["Entity", "Controller", "Service", "DAO", "Config", "Util", "Unknown"]

        def get_priority(cls):
            try:
                return priority_order.index(cls.category)
            except ValueError:
                return len(priority_order)

        sorted_classes = sorted(classes, key=get_priority)

        for cls in sorted_classes:
            class_tokens = self.estimate_class_tokens(cls)

            if current_tokens + class_tokens <= max_tokens:
                classes_that_fit.append(cls)
                current_tokens += class_tokens
            else:
                classes_that_dont_fit.append(cls)

        return classes_that_fit, classes_that_dont_fit

    def create_summary_for_large_class(self, java_class: JavaClass) -> str:
        """
        Create a condensed summary of a large class.

        Args:
            java_class: The class to summarize

        Returns:
            Condensed string representation
        """
        parts = []

        parts.append(f"Class: {java_class.name} ({java_class.category})")
        parts.append(f"Package: {java_class.package}")

        if java_class.extends:
            parts.append(f"Extends: {java_class.extends}")

        if java_class.implements:
            parts.append(f"Implements: {', '.join(java_class.implements[:3])}")

        # Key annotations only
        key_annotations = [
            ann.name for ann in java_class.annotations
            if ann.name in ["Entity", "Controller", "Service", "Repository", "RestController"]
        ]
        if key_annotations:
            parts.append(f"Annotations: {', '.join(key_annotations)}")

        # Field summary
        parts.append(f"Fields: {len(java_class.fields)}")

        # Method summary
        parts.append(f"Methods: {len(java_class.methods)}")

        # List important methods (REST endpoints, public methods)
        important_methods = []
        for method in java_class.methods:
            is_endpoint = any(
                ann.name in ["GetMapping", "PostMapping", "PutMapping", "DeleteMapping"]
                for ann in method.annotations
            )
            if is_endpoint or ("public" in method.modifiers and len(important_methods) < 5):
                params = ", ".join([p.type for p in method.parameters])
                important_methods.append(f"  - {method.name}({params}): {method.return_type}")

        if important_methods:
            parts.append("Key Methods:")
            parts.extend(important_methods)

        return "\n".join(parts)

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get token usage statistics.

        Returns:
            Dictionary with usage stats
        """
        return {
            "max_context_length": self.max_context_length,
            "max_request_tokens": self.max_request_tokens,
            "max_response_tokens": self.max_response_tokens,
            "model": self.model_name,
        }
