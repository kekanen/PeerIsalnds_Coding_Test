"""
Prompt templates for domain knowledge extraction.
"""

from typing import List, Dict, Any
from src.models.java_models import JavaClass


class PromptTemplates:
    """
    Collection of prompt templates for LLM-based domain knowledge extraction.
    """

    @staticmethod
    def get_domain_extraction_system_prompt() -> str:
        """Get the system prompt for domain extraction."""
        return """You are an expert software architect and domain-driven design specialist.
Your task is to analyze Java code and extract high-level domain knowledge, business rules,
and architectural patterns.

Focus on understanding the BUSINESS DOMAIN and BUSINESS LOGIC, not just the technical implementation.
Identify:
- Core domain entities and their business meaning
- Value objects and their constraints
- Business rules and validation logic
- Use cases and business workflows
- Domain events and their significance
- Bounded contexts and domain boundaries
- Aggregates and consistency boundaries

Provide clear, concise analysis that would help a developer understand the business domain
and modernize the application while preserving business logic."""

    @staticmethod
    def extract_bounded_contexts_prompt(classes: List[JavaClass]) -> str:
        """
        Create prompt for extracting bounded contexts.

        Args:
            classes: List of Java classes to analyze

        Returns:
            Formatted prompt
        """
        # Group classes by package
        packages = {}
        for cls in classes:
            package = cls.package
            if package not in packages:
                packages[package] = []
            packages[package].append(cls)

        # Build summary
        summary_lines = []
        summary_lines.append("Here is a summary of the Java codebase structure:\n")

        for package, pkg_classes in sorted(packages.items()):
            summary_lines.append(f"\nPackage: {package}")
            summary_lines.append(f"  Classes ({len(pkg_classes)}):")

            for cls in pkg_classes:
                summary_lines.append(f"    - {cls.name} ({cls.category})")

        summary = "\n".join(summary_lines)

        prompt = f"""{summary}

Based on the package structure and class organization above, identify the bounded contexts in this application.

A bounded context is a boundary within which a particular domain model is defined and applicable.
It represents a specific responsibility or sub-domain of the business.

Provide your analysis in the following JSON format:
{{
  "bounded_contexts": [
    {{
      "name": "context name",
      "description": "what this context is responsible for",
      "packages": ["list", "of", "packages"],
      "core_entities": ["list", "of", "key", "entities"],
      "responsibilities": ["list", "of", "responsibilities"]
    }}
  ]
}}"""

        return prompt

    @staticmethod
    def extract_domain_entities_prompt(entity_classes: List[JavaClass]) -> str:
        """
        Create prompt for extracting domain entity knowledge.

        Args:
            entity_classes: List of entity classes

        Returns:
            Formatted prompt
        """
        entities_info = []

        for entity in entity_classes:
            info_lines = [f"\n## Entity: {entity.name}"]
            info_lines.append(f"Package: {entity.package}")

            if entity.extends:
                info_lines.append(f"Extends: {entity.extends}")

            # Annotations
            if entity.annotations:
                info_lines.append("\nAnnotations:")
                for ann in entity.annotations:
                    info_lines.append(f"  - @{ann.name}{ann.arguments}")

            # Fields
            if entity.fields:
                info_lines.append("\nFields:")
                for field in entity.fields:
                    field_anns = ", ".join([f"@{a.name}" for a in field.annotations])
                    info_lines.append(f"  - {field.name}: {field.type} [{field_anns}]")

            # Methods (just names and signatures)
            if entity.methods:
                info_lines.append(f"\nMethods ({len(entity.methods)}):")
                for method in entity.methods[:5]:  # Limit to first 5
                    info_lines.append(f"  - {method.name}({', '.join([p.type for p in method.parameters])}): {method.return_type}")

            entities_info.append("\n".join(info_lines))

        entities_text = "\n".join(entities_info)

        prompt = f"""Analyze the following domain entities and extract their business meaning:

{entities_text}

For each entity, provide:
1. Business purpose and meaning
2. Key business rules and constraints (from annotations and field types)
3. Relationships with other entities
4. Whether it's an Aggregate Root, Entity, or Value Object in DDD terms

Respond in JSON format:
{{
  "entities": [
    {{
      "name": "entity name",
      "business_purpose": "what this entity represents in the business domain",
      "ddd_type": "AggregateRoot|Entity|ValueObject",
      "business_rules": ["list", "of", "business", "rules"],
      "relationships": [
        {{
          "entity": "related entity name",
          "type": "OneToMany|ManyToOne|ManyToMany|OneToOne",
          "business_meaning": "what this relationship means"
        }}
      ],
      "key_attributes": [
        {{
          "name": "attribute name",
          "business_meaning": "what this attribute represents",
          "constraints": ["list", "of", "constraints"]
        }}
      ]
    }}
  ]
}}"""

        return prompt

    @staticmethod
    def extract_use_cases_prompt(
        controllers: List[JavaClass],
        services: List[JavaClass],
    ) -> str:
        """
        Create prompt for extracting use cases from controllers and services.

        Args:
            controllers: List of controller classes
            services: List of service classes

        Returns:
            Formatted prompt
        """
        controllers_info = []

        for controller in controllers:
            info_lines = [f"\n## Controller: {controller.name}"]

            # Find REST endpoints
            endpoints = []
            for method in controller.methods:
                http_methods = []
                path = ""

                for ann in method.annotations:
                    if ann.name in ["GetMapping", "PostMapping", "PutMapping", "DeleteMapping", "PatchMapping"]:
                        http_methods.append(ann.name.replace("Mapping", ""))
                        path = ann.arguments.strip("()\"'")
                    elif ann.name == "RequestMapping":
                        http_methods.append("REQUEST")
                        path = ann.arguments

                if http_methods:
                    params = ", ".join([f"{p.name}: {p.type}" for p in method.parameters])
                    endpoints.append(f"  - [{','.join(http_methods)}] {path} -> {method.name}({params}): {method.return_type}")

            if endpoints:
                info_lines.append("Endpoints:")
                info_lines.extend(endpoints)

            controllers_info.append("\n".join(info_lines))

        services_info = []
        for service in services:
            info_lines = [f"\n## Service: {service.name}"]

            # List public methods
            public_methods = [m for m in service.methods if "public" in m.modifiers]
            if public_methods:
                info_lines.append("Public Methods:")
                for method in public_methods[:10]:  # Limit to 10
                    params = ", ".join([f"{p.name}: {p.type}" for p in method.parameters])
                    info_lines.append(f"  - {method.name}({params}): {method.return_type}")

            services_info.append("\n".join(info_lines))

        controllers_text = "\n".join(controllers_info)
        services_text = "\n".join(services_info)

        prompt = f"""Analyze the following controllers and services to extract the business use cases:

# Controllers
{controllers_text}

# Services
{services_text}

For each use case, identify:
1. The business goal or user story
2. The actors involved
3. The business workflow/steps
4. Success criteria

Respond in JSON format:
{{
  "use_cases": [
    {{
      "name": "use case name",
      "user_story": "As a [role], I want to [action] so that [benefit]",
      "actors": ["list", "of", "actors"],
      "preconditions": ["list", "of", "preconditions"],
      "steps": ["step 1", "step 2", "step 3"],
      "postconditions": ["list", "of", "postconditions"],
      "api_endpoints": ["list", "of", "related", "endpoints"],
      "related_entities": ["list", "of", "entities"]
    }}
  ]
}}"""

        return prompt

    @staticmethod
    def extract_business_rules_prompt(classes: List[JavaClass]) -> str:
        """
        Create prompt for extracting business rules.

        Args:
            classes: List of classes to analyze

        Returns:
            Formatted prompt
        """
        rules_context = []

        for cls in classes:
            # Look for validation annotations and method logic
            info_lines = [f"\n## {cls.name}"]

            # Field validations
            for field in cls.fields:
                validations = []
                for ann in field.annotations:
                    if ann.name in ["NotNull", "NotBlank", "NotEmpty", "Size", "Min", "Max", "Pattern", "Email", "Valid"]:
                        validations.append(f"@{ann.name}{ann.arguments}")

                if validations:
                    info_lines.append(f"  {field.name}: {' '.join(validations)}")

            # Methods with @Transactional, @Validated, etc.
            for method in cls.methods:
                important_anns = []
                for ann in method.annotations:
                    if ann.name in ["Transactional", "Validated", "PreAuthorize", "PostAuthorize"]:
                        important_anns.append(f"@{ann.name}{ann.arguments}")

                if important_anns:
                    info_lines.append(f"  {method.name}: {' '.join(important_anns)}")

            if len(info_lines) > 1:  # Only add if we found something
                rules_context.append("\n".join(info_lines))

        context_text = "\n".join(rules_context)

        prompt = f"""Analyze the following validation annotations and method constraints to extract business rules:

{context_text}

Identify all business rules and constraints, including:
1. Data validation rules
2. Business invariants
3. Transaction boundaries
4. Authorization rules
5. Business constraints

Respond in JSON format:
{{
  "business_rules": [
    {{
      "name": "rule name",
      "description": "what the rule enforces",
      "type": "Validation|Invariant|Transaction|Authorization|Constraint",
      "applies_to": "entity or operation",
      "implementation": "how it's currently implemented"
    }}
  ]
}}"""

        return prompt

    @staticmethod
    def extract_api_contracts_prompt(controllers: List[JavaClass]) -> str:
        """
        Create prompt for extracting API contracts.

        Args:
            controllers: List of controller classes

        Returns:
            Formatted prompt
        """
        endpoints_info = []

        for controller in controllers:
            base_path = ""

            # Get base path from class-level @RequestMapping
            for ann in controller.annotations:
                if ann.name == "RequestMapping":
                    base_path = ann.arguments.strip("()\"'")

            for method in controller.methods:
                http_method = "GET"  # default
                path = ""

                for ann in method.annotations:
                    if ann.name == "GetMapping":
                        http_method = "GET"
                        path = ann.arguments.strip("()\"'")
                    elif ann.name == "PostMapping":
                        http_method = "POST"
                        path = ann.arguments.strip("()\"'")
                    elif ann.name == "PutMapping":
                        http_method = "PUT"
                        path = ann.arguments.strip("()\"'")
                    elif ann.name == "DeleteMapping":
                        http_method = "DELETE"
                        path = ann.arguments.strip("()\"'")
                    elif ann.name == "PatchMapping":
                        http_method = "PATCH"
                        path = ann.arguments.strip("()\"'")

                if path or any(ann.name.endswith("Mapping") for ann in method.annotations):
                    full_path = f"{base_path}{path}".replace("//", "/")

                    params = []
                    for param in method.parameters:
                        param_anns = [ann.name for ann in param.annotations]
                        param_info = f"{param.name}: {param.type}"
                        if "PathVariable" in param_anns:
                            param_info += " [Path]"
                        elif "RequestParam" in param_anns:
                            param_info += " [Query]"
                        elif "RequestBody" in param_anns:
                            param_info += " [Body]"
                        params.append(param_info)

                    endpoints_info.append(
                        f"{http_method} {full_path}\n"
                        f"  Method: {method.name}\n"
                        f"  Parameters: {', '.join(params) if params else 'None'}\n"
                        f"  Returns: {method.return_type}\n"
                    )

        endpoints_text = "\n".join(endpoints_info)

        prompt = f"""Analyze the following REST API endpoints and extract the API contracts:

{endpoints_text}

For each endpoint, provide:
1. Business purpose
2. Request/response format expectations
3. HTTP status codes likely used
4. Business validation requirements

Respond in JSON format:
{{
  "api_endpoints": [
    {{
      "http_method": "GET|POST|PUT|DELETE|PATCH",
      "path": "/api/path",
      "summary": "what this endpoint does",
      "business_purpose": "why this endpoint exists",
      "request_body": "expected request format or null",
      "path_parameters": ["list", "of", "path", "params"],
      "query_parameters": ["list", "of", "query", "params"],
      "response_type": "expected response type",
      "status_codes": [
        {{
          "code": 200,
          "description": "success case"
        }}
      ],
      "related_use_case": "which use case this supports"
    }}
  ]
}}"""

        return prompt
