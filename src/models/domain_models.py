"""
Pydantic models representing extracted domain knowledge.
These models are populated by LLM analysis of Java code.
"""

from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field


class DomainEntityType(str, Enum):
    """Type of domain entity."""

    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    AGGREGATE_ROOT = "aggregate_root"


class DomainEntity(BaseModel):
    """Represents a domain entity extracted from Java code."""

    name: str = Field(..., description="Entity name")
    type: DomainEntityType = Field(..., description="Entity type classification")
    properties: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Entity properties with name, type, and constraints",
    )
    business_rules: List[str] = Field(
        default_factory=list, description="Business rules governing this entity"
    )
    relationships: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Relationships to other entities (target, type, cardinality)",
    )
    validation_rules: List[str] = Field(
        default_factory=list, description="Validation rules for entity properties"
    )
    lifecycle: Optional[str] = Field(
        default=None, description="Entity lifecycle rules (creation, update, deletion)"
    )

    def __str__(self) -> str:
        return f"{self.type.value}: {self.name}"


class ValueObject(BaseModel):
    """Represents a value object in domain-driven design."""

    name: str = Field(..., description="Value object name")
    properties: List[str] = Field(
        default_factory=list, description="Properties that make up this value object"
    )
    validation: str = Field(default="", description="Validation rules for the value object")
    immutable: bool = Field(default=True, description="Whether this value object is immutable")


class BusinessRule(BaseModel):
    """Represents an extracted business rule."""

    name: str = Field(..., description="Business rule name")
    description: str = Field(..., description="Detailed description of the rule")
    source_method: str = Field(..., description="Source method where rule was found")
    conditions: List[str] = Field(
        default_factory=list, description="Conditions that trigger this rule"
    )
    actions: List[str] = Field(
        default_factory=list, description="Actions taken when rule is applied"
    )
    exceptions: List[str] = Field(
        default_factory=list, description="Exceptions thrown when rule is violated"
    )

    def __str__(self) -> str:
        return f"Rule: {self.name}"


class APIEndpoint(BaseModel):
    """Represents a REST API endpoint extracted from controller."""

    path: str = Field(..., description="Endpoint path (e.g., /api/customers/{id})")
    method: str = Field(..., description="HTTP method (GET, POST, PUT, DELETE, etc.)")
    description: str = Field(..., description="What this endpoint does")
    business_operation: str = Field(
        ..., description="Business operation this endpoint represents"
    )
    request_schema: Optional[Dict] = Field(
        default=None, description="Request body schema (for POST/PUT)"
    )
    response_schema: Optional[Dict] = Field(
        default=None, description="Response body schema"
    )
    path_parameters: List[Dict[str, str]] = Field(
        default_factory=list, description="Path parameters with name, type, description"
    )
    query_parameters: List[Dict[str, str]] = Field(
        default_factory=list, description="Query parameters with name, type, description"
    )
    validation_rules: List[str] = Field(
        default_factory=list, description="Request validation rules"
    )
    error_scenarios: List[Dict[str, str]] = Field(
        default_factory=list, description="Error scenarios with status code and description"
    )
    business_logic_summary: str = Field(
        default="", description="Summary of business logic invoked"
    )

    def __str__(self) -> str:
        return f"{self.method} {self.path}"


class UseCase(BaseModel):
    """Represents a business use case."""

    name: str = Field(..., description="Use case name")
    description: str = Field(..., description="What this use case accomplishes")
    actors: List[str] = Field(default_factory=list, description="Actors involved in use case")
    preconditions: List[str] = Field(
        default_factory=list, description="Preconditions that must be met"
    )
    steps: List[str] = Field(default_factory=list, description="Steps to execute use case")
    postconditions: List[str] = Field(
        default_factory=list, description="Postconditions after use case completes"
    )
    entities_involved: List[str] = Field(
        default_factory=list, description="Domain entities involved"
    )
    error_scenarios: List[str] = Field(
        default_factory=list, description="Possible error scenarios"
    )

    def __str__(self) -> str:
        return f"UseCase: {self.name}"


class DataAccessPattern(BaseModel):
    """Represents data access patterns from repositories/DAOs."""

    entity: str = Field(..., description="Entity being accessed")
    operations: List[str] = Field(
        default_factory=list, description="CRUD and custom operations"
    )
    query_patterns: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Query patterns with method name, description, complexity",
    )
    relationships_loaded: List[str] = Field(
        default_factory=list, description="Related entities loaded (eager vs lazy)"
    )
    transaction_boundaries: List[str] = Field(
        default_factory=list, description="Transaction boundary descriptions"
    )


class BoundedContext(BaseModel):
    """Represents a bounded context in domain-driven design."""

    name: str = Field(..., description="Bounded context name")
    entities: List[str] = Field(
        default_factory=list, description="Entities within this context"
    )
    purpose: str = Field(..., description="Purpose of this bounded context")
    dependencies: List[str] = Field(
        default_factory=list, description="Other contexts this depends on"
    )


class DomainKnowledge(BaseModel):
    """Complete domain knowledge extracted from Java codebase."""

    project_name: str = Field(..., description="Project name")
    domain: str = Field(..., description="Business domain (e.g., e-commerce, rental management)")
    bounded_contexts: List[BoundedContext] = Field(
        default_factory=list, description="Identified bounded contexts"
    )
    entities: List[DomainEntity] = Field(
        default_factory=list, description="Domain entities"
    )
    value_objects: List[ValueObject] = Field(
        default_factory=list, description="Value objects"
    )
    business_rules: List[BusinessRule] = Field(
        default_factory=list, description="Business rules"
    )
    api_contracts: List[APIEndpoint] = Field(
        default_factory=list, description="REST API endpoints"
    )
    use_cases: List[UseCase] = Field(default_factory=list, description="Business use cases")
    data_patterns: List[DataAccessPattern] = Field(
        default_factory=list, description="Data access patterns"
    )
    cross_cutting_concerns: List[str] = Field(
        default_factory=list,
        description="Cross-cutting concerns (authentication, logging, validation, etc.)",
    )

    def get_entity_by_name(self, name: str) -> Optional[DomainEntity]:
        """Get entity by name."""
        return next((e for e in self.entities if e.name == name), None)

    def get_use_case_by_name(self, name: str) -> Optional[UseCase]:
        """Get use case by name."""
        return next((uc for uc in self.use_cases if uc.name == name), None)

    def get_endpoints_by_entity(self, entity_name: str) -> List[APIEndpoint]:
        """Get all API endpoints related to an entity."""
        return [ep for ep in self.api_contracts if entity_name.lower() in ep.path.lower()]

    def __str__(self) -> str:
        return (
            f"DomainKnowledge(project={self.project_name}, "
            f"entities={len(self.entities)}, "
            f"use_cases={len(self.use_cases)}, "
            f"endpoints={len(self.api_contracts)})"
        )
