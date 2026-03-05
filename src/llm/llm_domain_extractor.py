"""
Domain knowledge extractor using LLM.
"""

from typing import List, Dict, Any, Optional
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.models.java_models import JavaClass
from src.models.domain_models import (
    DomainKnowledge,
    BoundedContext,
    DomainEntity,
    ValueObject,
    BusinessRule,
    UseCase,
    APIEndpoint,
)
from src.llm.llm_client_provider import LLMClient
from src.llm.llm_prompt_templates import PromptTemplates
from src.llm.llm_token_manager import TokenManager
from src.config.settings import Settings


class DomainExtractor:
    """
    Extracts domain knowledge from Java code using LLM analysis.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the domain extractor.

        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        self.llm_client = LLMClient(self.settings)
        self.token_manager = TokenManager(
            model_name=self.llm_client.get_model_name(),
            max_context_length=self.llm_client.get_max_context_length(),
        )
        self.prompt_templates = PromptTemplates()
        self.console = Console()

    def extract_domain_knowledge(
        self,
        java_classes: List[JavaClass],
        verbose: bool = True,
    ) -> DomainKnowledge:
        """
        Extract complete domain knowledge from Java classes.

        Args:
            java_classes: List of parsed Java classes
            verbose: Whether to show progress

        Returns:
            DomainKnowledge object with all extracted information
        """
        if verbose:
            self.console.print("\n[bold cyan]Extracting Domain Knowledge with LLM[/bold cyan]\n")

        # Categorize classes
        entities = [cls for cls in java_classes if cls.category == "Entity"]
        controllers = [cls for cls in java_classes if cls.category == "Controller"]
        services = [cls for cls in java_classes if cls.category == "Service"]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Step 1: Extract bounded contexts
            task1 = progress.add_task("[cyan]Extracting bounded contexts...", total=1)
            bounded_contexts = self._extract_bounded_contexts(java_classes)
            progress.update(task1, advance=1)

            # Step 2: Extract domain entities
            task2 = progress.add_task("[cyan]Analyzing domain entities...", total=1)
            domain_entities = self._extract_domain_entities(entities) if entities else []
            progress.update(task2, advance=1)

            # Step 3: Extract use cases
            task3 = progress.add_task("[cyan]Extracting use cases...", total=1)
            use_cases = self._extract_use_cases(controllers, services) if controllers or services else []
            progress.update(task3, advance=1)

            # Step 4: Extract business rules
            task4 = progress.add_task("[cyan]Identifying business rules...", total=1)
            business_rules = self._extract_business_rules(java_classes)
            progress.update(task4, advance=1)

            # Step 5: Extract API contracts
            task5 = progress.add_task("[cyan]Analyzing API contracts...", total=1)
            api_endpoints = self._extract_api_contracts(controllers) if controllers else []
            progress.update(task5, advance=1)

        # Determine project name and domain
        project_name = self._infer_project_name(java_classes)
        domain = self._infer_domain(java_classes, bounded_contexts)

        # Build domain knowledge object
        domain_knowledge = DomainKnowledge(
            project_name=project_name,
            domain=domain,
            bounded_contexts=bounded_contexts,
            entities=domain_entities,
            value_objects=[],  # Could be extracted separately if needed
            business_rules=business_rules,
            api_contracts=api_endpoints,
            use_cases=use_cases,
            data_patterns=[],  # Could be extracted from repositories
            cross_cutting_concerns=[],  # Could be extracted from aspects, filters, etc.
        )

        if verbose:
            self._print_extraction_summary(domain_knowledge)

        return domain_knowledge

    def _extract_bounded_contexts(self, classes: List[JavaClass]) -> List[BoundedContext]:
        """Extract bounded contexts using LLM."""
        try:
            system_prompt = self.prompt_templates.get_domain_extraction_system_prompt()
            prompt = self.prompt_templates.extract_bounded_contexts_prompt(classes)

            response = self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more consistent analysis
            )

            # Parse response into BoundedContext objects
            bounded_contexts = []
            for ctx_data in response.get("bounded_contexts", []):
                # Map LLM response to BoundedContext model
                bounded_contexts.append(BoundedContext(
                    name=ctx_data.get("name", ""),
                    purpose=ctx_data.get("description", ""),  # Map description to purpose
                    entities=ctx_data.get("core_entities", []),
                    dependencies=ctx_data.get("responsibilities", [])[:3]  # Use first 3 responsibilities as dependencies
                ))

            return bounded_contexts

        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to extract bounded contexts: {e}[/yellow]")
            return []

    def _extract_domain_entities(self, entity_classes: List[JavaClass]) -> List[DomainEntity]:
        """Extract domain entity knowledge using LLM."""
        if not entity_classes:
            return []

        try:
            system_prompt = self.prompt_templates.get_domain_extraction_system_prompt()
            prompt = self.prompt_templates.extract_domain_entities_prompt(entity_classes)

            response = self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )

            # Parse response into DomainEntity objects
            domain_entities = []
            for entity_data in response.get("entities", []):
                # Convert relationships to proper format (target, type, cardinality)
                relationships = []
                for rel in entity_data.get("relationships", []):
                    relationships.append({
                        "target": rel.get("entity", ""),
                        "type": rel.get("type", ""),
                        "cardinality": rel.get("business_meaning", ""),
                    })

                # Convert attributes to properties (name, type, constraints)
                properties = []
                for attr in entity_data.get("key_attributes", []):
                    # Join constraints into a single string
                    constraints_str = ", ".join(attr.get("constraints", []))
                    properties.append({
                        "name": attr.get("name", ""),
                        "type": "string",  # Could be inferred from Java class
                        "constraints": constraints_str,
                    })

                # Map ddd_type to DomainEntityType enum
                ddd_type_str = entity_data.get("ddd_type", "Entity")
                if ddd_type_str == "AggregateRoot":
                    entity_type = "aggregate_root"
                elif ddd_type_str == "ValueObject":
                    entity_type = "value_object"
                else:
                    entity_type = "entity"

                domain_entities.append(DomainEntity(
                    name=entity_data.get("name", ""),
                    type=entity_type,
                    properties=properties,
                    business_rules=entity_data.get("business_rules", []),
                    relationships=relationships,
                    validation_rules=[],  # Can be extracted from constraints
                    lifecycle=None
                ))

            return domain_entities

        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to extract domain entities: {e}[/yellow]")
            import traceback
            traceback.print_exc()
            return []

    def _extract_use_cases(
        self,
        controllers: List[JavaClass],
        services: List[JavaClass],
    ) -> List[UseCase]:
        """Extract use cases from controllers and services."""
        if not controllers and not services:
            return []

        try:
            system_prompt = self.prompt_templates.get_domain_extraction_system_prompt()
            prompt = self.prompt_templates.extract_use_cases_prompt(controllers, services)

            response = self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )

            # Parse response into UseCase objects
            use_cases = []
            for uc_data in response.get("use_cases", []):
                use_cases.append(UseCase(
                    name=uc_data.get("name", ""),
                    description=uc_data.get("user_story", ""),
                    actors=uc_data.get("actors", []),
                    preconditions=uc_data.get("preconditions", []),
                    steps=uc_data.get("steps", []),
                    postconditions=uc_data.get("postconditions", []),
                    entities_involved=uc_data.get("related_entities", []),
                    error_scenarios=[]
                ))

            return use_cases

        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to extract use cases: {e}[/yellow]")
            return []

    def _extract_business_rules(self, classes: List[JavaClass]) -> List[BusinessRule]:
        """Extract business rules using LLM."""
        try:
            system_prompt = self.prompt_templates.get_domain_extraction_system_prompt()
            prompt = self.prompt_templates.extract_business_rules_prompt(classes)

            response = self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )

            # Parse response into BusinessRule objects
            business_rules = []
            for rule_data in response.get("business_rules", []):
                business_rules.append(BusinessRule(
                    name=rule_data.get("name", ""),
                    description=rule_data.get("description", ""),
                    source_method=rule_data.get("applies_to", "Unknown"),  # Required field
                    conditions=[],
                    actions=[rule_data.get("implementation", "")],
                    exceptions=[]
                ))

            return business_rules

        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to extract business rules: {e}[/yellow]")
            return []

    def _extract_api_contracts(self, controllers: List[JavaClass]) -> List[APIEndpoint]:
        """Extract API contracts from controllers."""
        if not controllers:
            return []

        try:
            system_prompt = self.prompt_templates.get_domain_extraction_system_prompt()
            prompt = self.prompt_templates.extract_api_contracts_prompt(controllers)

            response = self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )

            # Parse response into APIEndpoint objects
            api_endpoints = []
            for endpoint_data in response.get("api_endpoints", []):
                # Convert path/query parameters to proper format
                path_params = []
                for param in endpoint_data.get("path_parameters", []):
                    if isinstance(param, str):
                        path_params.append({"name": param, "type": "string", "description": ""})
                    else:
                        path_params.append(param)

                query_params = []
                for param in endpoint_data.get("query_parameters", []):
                    if isinstance(param, str):
                        query_params.append({"name": param, "type": "string", "description": ""})
                    else:
                        query_params.append(param)

                api_endpoints.append(APIEndpoint(
                    method=endpoint_data.get("http_method", "GET"),
                    path=endpoint_data.get("path", ""),
                    description=endpoint_data.get("summary", ""),
                    business_operation=endpoint_data.get("business_purpose", ""),  # Required field
                    request_schema=None,
                    response_schema=None,
                    path_parameters=path_params,
                    query_parameters=query_params,
                    validation_rules=[],
                    error_scenarios=[],
                    business_logic_summary=""
                ))

            return api_endpoints

        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to extract API contracts: {e}[/yellow]")
            return []

    def _infer_project_name(self, classes: List[JavaClass]) -> str:
        """Infer project name from package structure."""
        if not classes:
            return "Unknown Project"

        # Get most common base package
        packages = [cls.package.split(".")[0:3] for cls in classes if cls.package]
        if packages:
            # Take the most common package prefix
            package_str = ".".join(packages[0])
            # Extract likely project name (usually third part: org.springframework.petclinic -> petclinic)
            parts = package_str.split(".")
            if len(parts) >= 3:
                return parts[2].title()

        return "Java Project"

    def _infer_domain(self, classes: List[JavaClass], contexts: List[BoundedContext]) -> str:
        """Infer business domain."""
        if contexts:
            # Use first context as primary domain
            return contexts[0].purpose  # Changed from description to purpose

        # Fallback: try to infer from package names
        if classes:
            package = classes[0].package
            return f"Domain from {package}"

        return "Business Domain"

    def _print_extraction_summary(self, domain_knowledge: DomainKnowledge) -> None:
        """Print a summary of extracted domain knowledge."""
        self.console.print("\n[bold green]Domain Knowledge Extraction Complete[/bold green]\n")

        self.console.print(f"[cyan]Project:[/cyan] {domain_knowledge.project_name}")
        self.console.print(f"[cyan]Domain:[/cyan] {domain_knowledge.domain}\n")

        self.console.print(f"[yellow]Bounded Contexts:[/yellow] {len(domain_knowledge.bounded_contexts)}")
        for ctx in domain_knowledge.bounded_contexts:
            self.console.print(f"  • {ctx.name}")

        self.console.print(f"\n[yellow]Domain Entities:[/yellow] {len(domain_knowledge.entities)}")
        for entity in domain_knowledge.entities[:5]:
            self.console.print(f"  • {entity.name} ({entity.type})")

        self.console.print(f"\n[yellow]Use Cases:[/yellow] {len(domain_knowledge.use_cases)}")
        for uc in domain_knowledge.use_cases[:5]:
            self.console.print(f"  • {uc.name}")

        self.console.print(f"\n[yellow]Business Rules:[/yellow] {len(domain_knowledge.business_rules)}")
        for rule in domain_knowledge.business_rules[:5]:
            self.console.print(f"  • {rule.name}")

        self.console.print(f"\n[yellow]API Endpoints:[/yellow] {len(domain_knowledge.api_contracts)}")
        for endpoint in domain_knowledge.api_contracts[:5]:
            self.console.print(f"  • {endpoint.method} {endpoint.path}")
