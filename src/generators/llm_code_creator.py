"""
LLM-based code generator for Java-to-Node.js conversion.

Uses LLM to generate high-quality TypeScript/Node.js code from domain knowledge.
RAG (Retrieval-Augmented Generation) via ChromaDB enriches every prompt with
semantically relevant context retrieved from the indexed domain knowledge graph,
producing more accurate and context-aware code.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
import logging

from src.models.domain_models import (
    DomainEntity,
    UseCase,
    APIEndpoint,
    BusinessRule,
    DomainKnowledge,
)
from src.llm.llm_client_provider import LLMClient
from src.config.settings import Settings
from src.rag.rag_store import DomainKnowledgeRAGStore
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

logger = logging.getLogger(__name__)


class LLMCodeGenerator:
    """
    Generates Node.js/TypeScript code using LLM.

    Each generation method automatically retrieves semantically relevant
    domain knowledge from ChromaDB (RAG) and injects it into the LLM prompt,
    producing more context-aware and accurate code.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the LLM code generator.

        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        self.llm_client = LLMClient(self.settings)
        self.console = Console()

        # RAG store (lazily populated on first domain-knowledge-aware call)
        if self.settings.enable_rag:
            self.rag_store: Optional[DomainKnowledgeRAGStore] = DomainKnowledgeRAGStore(
                persist_dir=self.settings.chroma_persist_dir,
                top_k=self.settings.rag_top_k,
            )
        else:
            self.rag_store = None

    # ============================================================
    # RAG helpers
    # ============================================================

    def _ensure_rag_indexed(self, domain_knowledge: DomainKnowledge) -> None:
        """Index domain knowledge into the RAG store the first time it is needed."""
        if self.rag_store and not self.rag_store.is_initialized:
            logger.info("Indexing domain knowledge into ChromaDB RAG store …")
            self.rag_store.index_domain_knowledge(domain_knowledge)

    def _rag_context(self, retrieval: str) -> str:
        """Return retrieved context string (empty string when RAG is disabled)."""
        return retrieval if retrieval else ""

    # ============================================================
    # Entity Generation
    # ============================================================

    def generate_entity(
        self,
        entity: DomainEntity,
        domain_knowledge: DomainKnowledge,
    ) -> str:
        """
        Generate a TypeORM entity class from domain entity.

        Args:
            entity: Domain entity to generate
            domain_knowledge: Complete domain knowledge for context

        Returns:
            Generated TypeScript code
        """
        self._ensure_rag_indexed(domain_knowledge)

        # Retrieve RAG context for this entity
        rag_ctx = ""
        if self.rag_store:
            rag_ctx = self.rag_store.retrieve_for_entity(
                entity_name=entity.name,
                entity_description=f"{entity.type.value} with {len(entity.properties)} properties",
            )

        # Build context about related entities
        related_entities = [rel.get("target", "") for rel in entity.relationships]

        system_prompt = """You are an expert TypeScript and TypeORM developer.
Generate clean, production-ready TypeORM entity classes following best practices:
- Use proper TypeORM decorators (@Entity, @Column, @ManyToOne, etc.)
- Include all properties with correct types
- Add relationships with proper decorators
- Include validation decorators from class-validator
- Add JSDoc comments explaining business logic
- Follow TypeScript strict mode conventions
- Use proper naming conventions"""

        user_prompt = f"""Generate a TypeORM entity class for: {entity.name}

Entity Type: {entity.type}

Properties:
{json.dumps(entity.properties, indent=2)}

Business Rules:
{json.dumps(entity.business_rules, indent=2)}

Relationships:
{json.dumps(entity.relationships, indent=2)}

Context - Related Entities in Domain:
{', '.join(related_entities) if related_entities else 'None'}
{rag_ctx}
Requirements:
1. Create a complete TypeORM entity with @Entity() decorator
2. Add all properties with @Column() decorators and correct TypeScript types
3. Implement relationships using @ManyToOne, @OneToMany, @ManyToMany as needed
4. Add validation decorators (@IsNotEmpty, @IsString, @Matches, etc.) based on business rules
5. Include @PrimaryGeneratedColumn() for ID
6. Add createdAt and updatedAt timestamp columns
7. Include JSDoc comments explaining the entity's purpose and business rules
8. Export the class

Generate ONLY the TypeScript code, no explanations."""

        response = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )
        return self._extract_code_from_response(response)

    # ============================================================
    # Repository Generation
    # ============================================================

    def generate_repository_interface(self, entity: DomainEntity) -> str:
        """
        Generate repository interface for an entity.

        Args:
            entity: Domain entity

        Returns:
            Generated TypeScript interface code
        """
        rag_ctx = ""
        if self.rag_store:
            rag_ctx = self.rag_store.retrieve_for_repository(entity.name)

        system_prompt = """You are an expert TypeScript developer.
Generate clean repository interfaces following Domain-Driven Design principles."""

        user_prompt = f"""Generate a repository interface for: {entity.name}

The interface should include:
1. Standard CRUD methods (findById, findAll, save, update, delete)
2. Custom query methods based on the entity's properties
3. Proper TypeScript types and generics
4. JSDoc comments
5. Return types using Promise<T>

Entity properties for reference:
{json.dumps(entity.properties, indent=2)}
{rag_ctx}
Generate ONLY the TypeScript code, no explanations."""

        response = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )
        return self._extract_code_from_response(response)

    def generate_repository_implementation(
        self,
        entity: DomainEntity,
        interface_code: str,
    ) -> str:
        """
        Generate TypeORM repository implementation.

        Args:
            entity: Domain entity
            interface_code: Repository interface code

        Returns:
            Generated TypeScript implementation code
        """
        rag_ctx = ""
        if self.rag_store:
            rag_ctx = self.rag_store.retrieve_for_repository(entity.name)

        system_prompt = """You are an expert TypeORM developer.
Generate production-ready TypeORM repository implementations."""

        user_prompt = f"""Generate a TypeORM repository implementation for: {entity.name}

Repository Interface:
```typescript
{interface_code}
```
{rag_ctx}
Requirements:
1. Implement the repository interface
2. Use TypeORM Repository<T> from 'typeorm'
3. Inject the repository using @InjectRepository decorator
4. Implement all interface methods using TypeORM query methods
5. Add proper error handling with try-catch
6. Include logging for important operations
7. Use async/await for all database operations
8. Add JSDoc comments

Generate ONLY the TypeScript code, no explanations."""

        response = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )
        return self._extract_code_from_response(response)

    # ============================================================
    # Use Case Generation
    # ============================================================

    def generate_use_case(
        self,
        use_case: UseCase,
        domain_knowledge: DomainKnowledge,
    ) -> str:
        """
        Generate use case class with business logic.

        Args:
            use_case: Use case to generate
            domain_knowledge: Complete domain knowledge for context

        Returns:
            Generated TypeScript code
        """
        self._ensure_rag_indexed(domain_knowledge)

        # Retrieve RAG context for this use case
        rag_ctx = ""
        if self.rag_store:
            rag_ctx = self.rag_store.retrieve_for_use_case(
                use_case_name=use_case.name,
                description=use_case.description,
            )

        # Get related entities
        entities_context = []
        for entity_name in use_case.entities_involved:
            entity = next(
                (e for e in domain_knowledge.entities if e.name == entity_name), None
            )
            if entity:
                entities_context.append(
                    {
                        "name": entity.name,
                        "properties": entity.properties,
                        "business_rules": entity.business_rules,
                    }
                )

        # Get related business rules
        related_rules = [
            rule
            for rule in domain_knowledge.business_rules
            if any(entity in rule.source_method for entity in use_case.entities_involved)
        ]
        rules_data = [{"name": r.name, "description": r.description} for r in related_rules]

        system_prompt = """You are an expert in Clean Architecture and TypeScript.
Generate production-ready use case classes following these principles:
- Single Responsibility Principle
- Dependency Inversion (depend on interfaces, not implementations)
- Clear separation of concerns
- Proper error handling
- Validation before business logic
- Return Result<T> or proper response DTOs"""

        user_prompt = f"""Generate a use case class for: {use_case.name}

Description: {use_case.description}

Actors: {', '.join(use_case.actors)}

Steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(use_case.steps))}

Preconditions:
{chr(10).join(f"- {cond}" for cond in use_case.preconditions)}

Postconditions:
{chr(10).join(f"- {cond}" for cond in use_case.postconditions)}

Related Entities:
{json.dumps(entities_context, indent=2)}

Related Business Rules:
{json.dumps(rules_data, indent=2)}
{rag_ctx}
Requirements:
1. Create a use case class following Clean Architecture
2. Inject repository dependencies through constructor
3. Implement an execute() method with proper input DTO
4. Validate preconditions before executing business logic
5. Implement each step from the use case description
6. Enforce business rules
7. Return a proper response DTO or Result<T>
8. Add comprehensive error handling
9. Include JSDoc comments
10. Use dependency injection (constructor injection)

Generate ONLY the TypeScript code, no explanations."""

        response = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )
        return self._extract_code_from_response(response)

    # ============================================================
    # Controller Generation
    # ============================================================

    def generate_controller(
        self,
        endpoints: List[APIEndpoint],
        controller_name: str,
        domain_knowledge: DomainKnowledge,
    ) -> str:
        """
        Generate Express controller for API endpoints.

        Args:
            endpoints: List of API endpoints for this controller
            controller_name: Name of the controller
            domain_knowledge: Complete domain knowledge for context

        Returns:
            Generated TypeScript code
        """
        self._ensure_rag_indexed(domain_knowledge)

        # Retrieve RAG context for this controller
        rag_ctx = ""
        if self.rag_store:
            endpoint_summary = "; ".join(
                f"{ep.method} {ep.path}" for ep in endpoints[:5]
            )
            rag_ctx = self.rag_store.retrieve_for_controller(
                resource_name=controller_name,
                endpoint_summary=endpoint_summary,
            )

        endpoints_info = [
            {
                "method": ep.method,
                "path": ep.path,
                "description": ep.description,
                "business_operation": ep.business_operation,
                "path_parameters": ep.path_parameters,
                "query_parameters": ep.query_parameters,
            }
            for ep in endpoints
        ]

        system_prompt = """You are an expert TypeScript developer specializing in TSOA (TypeScript OpenAPI) framework.
Generate production-ready TSOA controllers following these strict requirements:
- MUST use TSOA framework (@Route, @Get, @Post, @Put, @Delete decorators from 'tsoa')
- MUST extend Controller class from 'tsoa'
- MUST use @Tags decorator for grouping
- MUST use @Path, @Body, @Query decorators for parameters
- MUST use @SuccessResponse and @Response decorators for documentation
- Use class-validator for DTO validation
- Handle errors gracefully with try-catch
- Use dependency injection via constructor
- Return proper HTTP status codes
- Include comprehensive JSDoc comments"""

        user_prompt = f"""Generate a TSOA controller class: {controller_name}

Endpoints to implement:
{json.dumps(endpoints_info, indent=2)}
{rag_ctx}
STRICT Requirements:
1. Import from 'tsoa': Controller, Get, Post, Put, Delete, Route, Tags, Path, Body, Query, SuccessResponse, Response as SwaggerResponse
2. Import from 'express': Request, Response, NextFunction
3. Import class-validator: validateOrReject
4. Create controller class extending Controller
5. Use @Route decorator with base path
6. Use @Tags decorator for API grouping
7. For each endpoint, create a method with:
   - Appropriate HTTP method decorator (@Get, @Post, etc.)
   - @SuccessResponse for success cases
   - @SwaggerResponse for error cases
   - Parameters decorated with @Path, @Body, @Query
   - Express req, res, next parameters
   - Validate DTOs using validateOrReject
   - Try-catch error handling
   - Proper HTTP status codes via res.status()
8. Define inline DTOs/interfaces if needed for request/response types
9. Inject use case interfaces via constructor
10. Include JSDoc comments for all methods

IMPORTANT: Use ONLY TSOA decorators, do NOT use routing-controllers or any other framework.

Generate ONLY the TypeScript code, no explanations."""

        response = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )
        return self._extract_code_from_response(response)

    # ============================================================
    # DTO Generation
    # ============================================================

    def generate_dto(
        self,
        dto_name: str,
        entity: DomainEntity,
        dto_type: str = "create",
    ) -> str:
        """
        Generate DTO (Data Transfer Object) class.

        Args:
            dto_name: Name of the DTO
            entity: Related domain entity
            dto_type: Type of DTO (create, update, response)

        Returns:
            Generated TypeScript code
        """
        rag_ctx = ""
        if self.rag_store:
            rag_ctx = self.rag_store.retrieve_for_dto(entity.name, dto_type)

        system_prompt = """You are an expert TypeScript developer.
Generate clean DTO classes with proper validation decorators."""

        user_prompt = f"""Generate a {dto_type.upper()} DTO for: {dto_name}

Based on entity: {entity.name}

Entity properties:
{json.dumps(entity.properties, indent=2)}

Business rules to validate:
{json.dumps(entity.business_rules, indent=2)}
{rag_ctx}
Requirements:
1. Create a DTO class with all necessary properties
2. Add class-validator decorators (@IsString, @IsNotEmpty, @IsOptional, etc.)
3. Add class-transformer decorators if needed (@Type, @Expose, @Exclude)
4. Include JSDoc comments
5. Export the class
6. For UPDATE DTOs, make most fields optional
7. For CREATE DTOs, include all required fields
8. For RESPONSE DTOs, include all fields that should be returned

Generate ONLY the TypeScript code, no explanations."""

        response = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )
        return self._extract_code_from_response(response)

    # ============================================================
    # Utility Methods
    # ============================================================

    def _extract_code_from_response(self, response: str) -> str:
        """
        Extract code from LLM response, removing markdown formatting.

        Args:
            response: Raw LLM response

        Returns:
            Clean code
        """
        if "```typescript" in response:
            code = response.split("```typescript")[1].split("```")[0]
        elif "```ts" in response:
            code = response.split("```ts")[1].split("```")[0]
        elif "```" in response:
            code = response.split("```")[1].split("```")[0]
        else:
            code = response
        return code.strip()

    def generate_all_for_entity(
        self,
        entity: DomainEntity,
        domain_knowledge: DomainKnowledge,
        verbose: bool = False,
    ) -> Dict[str, str]:
        """
        Generate all code files for a single entity.

        Args:
            entity: Domain entity
            domain_knowledge: Complete domain knowledge
            verbose: Show progress

        Returns:
            Dictionary mapping file paths to code content
        """
        # Ensure RAG is indexed before any generation begins
        self._ensure_rag_indexed(domain_knowledge)

        generated_files = {}

        if verbose:
            self.console.print(f"[cyan]Generating code for entity: {entity.name}[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            # Generate entity
            task = progress.add_task("  Generating entity...", total=1)
            entity_code = self.generate_entity(entity, domain_knowledge)
            generated_files[f"src/domain/entities/{entity.name.lower()}.entity.ts"] = entity_code
            progress.update(task, advance=1)

            # Generate repository interface
            task = progress.add_task("  Generating repository interface...", total=1)
            repo_interface = self.generate_repository_interface(entity)
            generated_files[
                f"src/domain/repositories/i{entity.name.lower()}.repository.ts"
            ] = repo_interface
            progress.update(task, advance=1)

            # Generate repository implementation
            task = progress.add_task("  Generating repository implementation...", total=1)
            repo_impl = self.generate_repository_implementation(entity, repo_interface)
            generated_files[
                f"src/infrastructure/repositories/{entity.name.lower()}.repository.ts"
            ] = repo_impl
            progress.update(task, advance=1)

            # Generate DTOs
            task = progress.add_task("  Generating DTOs...", total=1)
            create_dto = self.generate_dto(f"Create{entity.name}Dto", entity, "create")
            update_dto = self.generate_dto(f"Update{entity.name}Dto", entity, "update")
            response_dto = self.generate_dto(f"{entity.name}ResponseDto", entity, "response")

            generated_files[
                f"src/application/dtos/create-{entity.name.lower()}.dto.ts"
            ] = create_dto
            generated_files[
                f"src/application/dtos/update-{entity.name.lower()}.dto.ts"
            ] = update_dto
            generated_files[
                f"src/application/dtos/{entity.name.lower()}-response.dto.ts"
            ] = response_dto
            progress.update(task, advance=1)

        if verbose:
            self.console.print(
                f"[green]  ✓ Generated {len(generated_files)} files for {entity.name}[/green]"
            )

        return generated_files
