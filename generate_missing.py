"""
Targeted generator: produces the mandatory Controller, Entity, and DAO files
that are required by the deliverables specification but were not generated in
the main pipeline run (because entity/API-endpoint extraction hit token limits).

Generates for three domains: Customer, Rental, Store
  - TypeORM entity
  - Repository interface (DAO)
  - TypeORM repository implementation
  - Create / Update / Response DTOs
  - Express/TSOA controller
  - knowledge_extraction.json structured output
"""

import json
import os
import sys
from pathlib import Path

# ── project path setup ────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
os.environ.setdefault("OPENAI_API_BASE", "")          # use OpenAI directly
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")  # correct model name

from src.config.settings import Settings
from src.generators.llm_code_creator import LLMCodeGenerator
from src.models.domain_models import (
    APIEndpoint,
    BoundedContext,
    BusinessRule,
    DomainEntity,
    DomainEntityType,
    DomainKnowledge,
    UseCase,
)
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
settings = Settings()


# ── Domain entity definitions (based on Sakila schema + extracted knowledge) ──

CUSTOMER_ENTITY = DomainEntity(
    name="Customer",
    type=DomainEntityType.AGGREGATE_ROOT,
    properties=[
        {"name": "customerId", "type": "number", "constraints": "primary key, auto-increment"},
        {"name": "storeId", "type": "number", "constraints": "not null, FK to store"},
        {"name": "firstName", "type": "string", "constraints": "not null, max 45"},
        {"name": "lastName", "type": "string", "constraints": "not null, max 45"},
        {"name": "email", "type": "string", "constraints": "optional, max 50"},
        {"name": "addressId", "type": "number", "constraints": "not null, FK to address"},
        {"name": "active", "type": "boolean", "constraints": "not null, default true"},
        {"name": "createDate", "type": "Date", "constraints": "not null"},
        {"name": "lastUpdate", "type": "Date", "constraints": "auto-updated"},
    ],
    business_rules=[
        "Only active customers may rent DVDs",
        "Email must be unique across all customers",
        "Customer must belong to exactly one store",
    ],
    relationships=[
        {"target": "Store", "type": "ManyToOne", "cardinality": "N:1"},
        {"target": "Address", "type": "ManyToOne", "cardinality": "N:1"},
        {"target": "Rental", "type": "OneToMany", "cardinality": "1:N"},
        {"target": "Payment", "type": "OneToMany", "cardinality": "1:N"},
    ],
    validation_rules=[
        "firstName must not be empty",
        "lastName must not be empty",
        "storeId must be a positive integer",
        "addressId must be a positive integer",
    ],
    lifecycle="Created on customer registration; soft-deleted by setting active=false",
)

RENTAL_ENTITY = DomainEntity(
    name="Rental",
    type=DomainEntityType.AGGREGATE_ROOT,
    properties=[
        {"name": "rentalId", "type": "number", "constraints": "primary key, auto-increment"},
        {"name": "rentalDate", "type": "Date", "constraints": "not null"},
        {"name": "inventoryId", "type": "number", "constraints": "not null, FK to inventory"},
        {"name": "customerId", "type": "number", "constraints": "not null, FK to customer"},
        {"name": "returnDate", "type": "Date", "constraints": "nullable"},
        {"name": "staffId", "type": "number", "constraints": "not null, FK to staff"},
        {"name": "lastUpdate", "type": "Date", "constraints": "auto-updated"},
    ],
    business_rules=[
        "Rental date must not be null",
        "Only active customers can create rentals",
        "Inventory item must be available (no open rental) before renting",
        "Staff member must be from the same store as the inventory item",
    ],
    relationships=[
        {"target": "Inventory", "type": "ManyToOne", "cardinality": "N:1"},
        {"target": "Customer", "type": "ManyToOne", "cardinality": "N:1"},
        {"target": "Staff", "type": "ManyToOne", "cardinality": "N:1"},
        {"target": "Payment", "type": "OneToMany", "cardinality": "1:N"},
    ],
    validation_rules=[
        "rentalDate must not be null",
        "inventoryId must be positive",
        "customerId must be positive",
        "staffId must be positive",
    ],
    lifecycle="Created when DVD is rented; returnDate set when DVD is returned",
)

STORE_ENTITY = DomainEntity(
    name="Store",
    type=DomainEntityType.AGGREGATE_ROOT,
    properties=[
        {"name": "storeId", "type": "number", "constraints": "primary key, auto-increment"},
        {"name": "managerStaffId", "type": "number", "constraints": "not null, unique, FK to staff"},
        {"name": "addressId", "type": "number", "constraints": "not null, FK to address"},
        {"name": "lastUpdate", "type": "Date", "constraints": "auto-updated"},
    ],
    business_rules=[
        "Each store must have exactly one manager",
        "Manager must be a staff member assigned to that store",
        "Store ID must not be null in inventory records",
    ],
    relationships=[
        {"target": "Staff", "type": "OneToOne", "cardinality": "1:1", "join": "managerStaffId"},
        {"target": "Address", "type": "ManyToOne", "cardinality": "N:1"},
        {"target": "Staff", "type": "OneToMany", "cardinality": "1:N"},
        {"target": "Inventory", "type": "OneToMany", "cardinality": "1:N"},
        {"target": "Customer", "type": "OneToMany", "cardinality": "1:N"},
    ],
    validation_rules=[
        "managerStaffId must be positive and unique",
        "addressId must be positive",
    ],
    lifecycle="Created when a new store is opened; cannot be deleted if it has active inventory",
)


# ── API endpoint definitions (from Spring @RestController analysis) ───────────

CUSTOMER_ENDPOINTS = [
    APIEndpoint(
        path="/customers",
        method="GET",
        description="Get list of all customers with optional filtering",
        business_operation="Manage Customer List",
        query_parameters=[
            {"name": "active", "type": "boolean", "description": "Filter by active status"},
            {"name": "storeId", "type": "number", "description": "Filter by store"},
        ],
        path_parameters=[],
        validation_rules=["storeId must be positive if provided"],
        error_scenarios=[{"status": "500", "description": "Database error"}],
        business_logic_summary="Returns all customers, optionally filtered by active status or store",
    ),
    APIEndpoint(
        path="/customers/{customerId}",
        method="GET",
        description="Get a single customer by ID",
        business_operation="Get Customer Details",
        path_parameters=[{"name": "customerId", "type": "number", "description": "Customer primary key"}],
        query_parameters=[],
        validation_rules=["customerId must be a positive integer"],
        error_scenarios=[
            {"status": "404", "description": "Customer not found"},
            {"status": "400", "description": "Invalid customer ID"},
        ],
        business_logic_summary="Fetches customer with related address and store information",
    ),
    APIEndpoint(
        path="/customers",
        method="POST",
        description="Add a new customer",
        business_operation="Add New Customer",
        path_parameters=[],
        query_parameters=[],
        request_schema={"firstName": "string", "lastName": "string", "email": "string", "storeId": "number", "addressId": "number"},
        response_schema={"customerId": "number", "firstName": "string", "lastName": "string"},
        validation_rules=["firstName required", "lastName required", "storeId required", "addressId required"],
        error_scenarios=[
            {"status": "400", "description": "Validation error"},
            {"status": "409", "description": "Email already exists"},
        ],
        business_logic_summary="Creates customer and links to store and address",
    ),
    APIEndpoint(
        path="/customers/{customerId}",
        method="PUT",
        description="Update customer information",
        business_operation="Update Customer Information",
        path_parameters=[{"name": "customerId", "type": "number", "description": "Customer primary key"}],
        query_parameters=[],
        validation_rules=["customerId must be positive", "at least one field required"],
        error_scenarios=[
            {"status": "404", "description": "Customer not found"},
            {"status": "400", "description": "Validation error"},
        ],
        business_logic_summary="Updates allowed fields on an existing customer record",
    ),
    APIEndpoint(
        path="/customers/{customerId}",
        method="DELETE",
        description="Delete a customer (soft delete by setting active=false)",
        business_operation="Delete Customer",
        path_parameters=[{"name": "customerId", "type": "number", "description": "Customer primary key"}],
        query_parameters=[],
        validation_rules=["customerId must be positive"],
        error_scenarios=[
            {"status": "404", "description": "Customer not found"},
            {"status": "409", "description": "Customer has open rentals"},
        ],
        business_logic_summary="Soft-deletes customer by setting active=false; rejects if open rentals exist",
    ),
]

RENTAL_ENDPOINTS = [
    APIEndpoint(
        path="/rentals",
        method="GET",
        description="Get list of all rental transactions",
        business_operation="Manage Rental List",
        path_parameters=[],
        query_parameters=[
            {"name": "customerId", "type": "number", "description": "Filter by customer"},
            {"name": "returned", "type": "boolean", "description": "Filter by return status"},
        ],
        validation_rules=[],
        error_scenarios=[{"status": "500", "description": "Database error"}],
        business_logic_summary="Returns rental transactions with optional customer or return-status filter",
    ),
    APIEndpoint(
        path="/rentals",
        method="POST",
        description="Create a new rental (rent a DVD)",
        business_operation="Rent DVD",
        path_parameters=[],
        query_parameters=[],
        request_schema={"inventoryId": "number", "customerId": "number", "staffId": "number"},
        response_schema={"rentalId": "number", "rentalDate": "string"},
        validation_rules=["inventoryId required", "customerId required", "staffId required", "customer must be active", "inventory must be available"],
        error_scenarios=[
            {"status": "400", "description": "Inventory not available"},
            {"status": "403", "description": "Customer is not active"},
        ],
        business_logic_summary="Records a DVD rental; validates inventory availability and customer active status",
    ),
    APIEndpoint(
        path="/rentals/{rentalId}/return",
        method="PUT",
        description="Return a rented DVD",
        business_operation="Return DVD",
        path_parameters=[{"name": "rentalId", "type": "number", "description": "Rental primary key"}],
        query_parameters=[],
        validation_rules=["rentalId must be positive", "rental must not already be returned"],
        error_scenarios=[
            {"status": "404", "description": "Rental not found"},
            {"status": "409", "description": "DVD already returned"},
        ],
        business_logic_summary="Sets returnDate on the rental record",
    ),
]

STORE_ENDPOINTS = [
    APIEndpoint(
        path="/stores",
        method="GET",
        description="Get list of all stores",
        business_operation="Manage Store List",
        path_parameters=[],
        query_parameters=[],
        validation_rules=[],
        error_scenarios=[{"status": "500", "description": "Database error"}],
        business_logic_summary="Returns all stores with manager and address information",
    ),
    APIEndpoint(
        path="/stores",
        method="POST",
        description="Add a new store",
        business_operation="Add New Store",
        path_parameters=[],
        query_parameters=[],
        request_schema={"managerStaffId": "number", "addressId": "number"},
        response_schema={"storeId": "number"},
        validation_rules=["managerStaffId required", "addressId required", "user must be admin"],
        error_scenarios=[
            {"status": "400", "description": "Validation error"},
            {"status": "403", "description": "Insufficient privileges"},
        ],
        business_logic_summary="Creates a new store; caller must have admin role",
    ),
    APIEndpoint(
        path="/stores/{storeId}",
        method="PUT",
        description="Update store information",
        business_operation="Update Store Information",
        path_parameters=[{"name": "storeId", "type": "number", "description": "Store primary key"}],
        query_parameters=[],
        validation_rules=["storeId must be positive"],
        error_scenarios=[
            {"status": "404", "description": "Store not found"},
            {"status": "403", "description": "Insufficient privileges"},
        ],
        business_logic_summary="Updates manager or address of an existing store",
    ),
    APIEndpoint(
        path="/stores/{storeId}",
        method="DELETE",
        description="Delete a store",
        business_operation="Delete Store",
        path_parameters=[{"name": "storeId", "type": "number", "description": "Store primary key"}],
        query_parameters=[],
        validation_rules=["storeId must be positive", "store must have no active inventory"],
        error_scenarios=[
            {"status": "404", "description": "Store not found"},
            {"status": "409", "description": "Store has active inventory"},
        ],
        business_logic_summary="Deletes store; rejected if active inventory exists",
    ),
]


# ── Minimal DomainKnowledge (load from saved JSON + augment) ─────────────────

def load_domain_knowledge() -> DomainKnowledge:
    dk_path = ROOT / "output" / "domain_knowledge.json"
    raw = json.loads(dk_path.read_text(encoding="utf-8"))

    # Re-hydrate bounded contexts and business rules from JSON
    bounded_contexts = [BoundedContext(**bc) for bc in raw.get("bounded_contexts", [])]
    business_rules = [BusinessRule(**br) for br in raw.get("business_rules", [])]
    use_cases = [UseCase(**uc) for uc in raw.get("use_cases", [])]

    return DomainKnowledge(
        project_name=raw.get("project_name", "spring-rest-sakila"),
        domain=raw.get("domain", "DVD rental store management"),
        bounded_contexts=bounded_contexts,
        entities=[CUSTOMER_ENTITY, RENTAL_ENTITY, STORE_ENTITY],
        business_rules=business_rules,
        use_cases=use_cases,
        api_contracts=CUSTOMER_ENDPOINTS + RENTAL_ENDPOINTS + STORE_ENDPOINTS,
    )


# ── Main generation ───────────────────────────────────────────────────────────

def write(path: str, content: str) -> None:
    full = ROOT / "output" / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    console.print(f"  [green]✓[/green] {path}")


def generate_knowledge_extraction(domain_knowledge: DomainKnowledge) -> None:
    """Generate structured knowledge_extraction.json."""
    knowledge = {
        "projectOverview": {
            "name": domain_knowledge.project_name,
            "domain": domain_knowledge.domain,
            "sourceRepository": "https://github.com/codejsha/spring-rest-sakila",
            "targetFramework": "Node.js / TypeScript / Express / TypeORM",
            "architecturePattern": "Clean Architecture",
            "boundedContexts": len(domain_knowledge.bounded_contexts),
            "totalEntities": len(domain_knowledge.entities),
            "totalUseCases": len(domain_knowledge.use_cases),
            "totalBusinessRules": len(domain_knowledge.business_rules),
            "totalApiEndpoints": len(domain_knowledge.api_contracts),
        },
        "boundedContexts": [
            {
                "name": bc.name,
                "purpose": bc.purpose,
                "entities": bc.entities,
                "dependencies": bc.dependencies,
            }
            for bc in domain_knowledge.bounded_contexts
        ],
        "businessRules": [
            {
                "name": br.name,
                "description": br.description,
                "sourceMethod": br.source_method,
                "conditions": br.conditions,
                "actions": br.actions,
                "exceptions": br.exceptions,
            }
            for br in domain_knowledge.business_rules
        ],
        "modules": [
            {
                "name": entity.name,
                "type": entity.type.value,
                "description": f"Domain entity for {entity.name} management",
                "properties": entity.properties,
                "businessRules": entity.business_rules,
                "relationships": entity.relationships,
                "endpoints": [
                    {
                        "method": ep.method,
                        "path": ep.path,
                        "operation": ep.business_operation,
                        "description": ep.description,
                    }
                    for ep in domain_knowledge.api_contracts
                    if entity.name.lower() in ep.path.lower()
                ],
                "useCases": [
                    {
                        "name": uc.name,
                        "description": uc.description,
                        "actors": uc.actors,
                        "steps": uc.steps,
                    }
                    for uc in domain_knowledge.use_cases
                    if entity.name in uc.name or entity.name.lower() in uc.description.lower()
                ],
                "complexityEstimate": "medium",
                "internalDependencies": [r["target"] for r in entity.relationships],
            }
            for entity in domain_knowledge.entities
        ],
    }
    write("knowledge_extraction.json", json.dumps(knowledge, indent=2))


def main() -> None:
    console.print()
    console.print("[bold cyan]Generating missing deliverable files (Controller, Entity, DAO)...[/bold cyan]")
    console.print()

    domain_knowledge = load_domain_knowledge()
    generator = LLMCodeGenerator(settings)

    # ── Index into RAG ────────────────────────────────────────────────────────
    console.print("[cyan]Indexing domain knowledge into ChromaDB RAG store...[/cyan]")
    generator._ensure_rag_indexed(domain_knowledge)
    console.print("[green]✓ RAG store ready[/green]")
    console.print()

    # ── Generate entities (TypeORM) ───────────────────────────────────────────
    console.print("[bold]Generating TypeORM entities...[/bold]")
    for entity in [CUSTOMER_ENTITY, RENTAL_ENTITY, STORE_ENTITY]:
        console.print(f"  [cyan]→ {entity.name} entity[/cyan]")
        code = generator.generate_entity(entity, domain_knowledge)
        write(f"src/domain/entities/{entity.name.lower()}.entity.ts", code)

    console.print()

    # ── Generate repository interfaces (DAO contracts) ────────────────────────
    console.print("[bold]Generating repository interfaces (DAO contracts)...[/bold]")
    repo_interfaces: dict[str, str] = {}
    for entity in [CUSTOMER_ENTITY, RENTAL_ENTITY, STORE_ENTITY]:
        console.print(f"  [cyan]→ I{entity.name}Repository interface[/cyan]")
        code = generator.generate_repository_interface(entity)
        repo_interfaces[entity.name] = code
        write(f"src/domain/repositories/i{entity.name.lower()}.repository.ts", code)

    console.print()

    # ── Generate repository implementations (TypeORM DAO) ────────────────────
    console.print("[bold]Generating TypeORM repository implementations (DAO)...[/bold]")
    for entity in [CUSTOMER_ENTITY, RENTAL_ENTITY, STORE_ENTITY]:
        console.print(f"  [cyan]→ {entity.name}Repository implementation[/cyan]")
        code = generator.generate_repository_implementation(entity, repo_interfaces[entity.name])
        write(f"src/infrastructure/repositories/{entity.name.lower()}.repository.ts", code)

    console.print()

    # ── Generate DTOs ─────────────────────────────────────────────────────────
    console.print("[bold]Generating DTOs...[/bold]")
    for entity in [CUSTOMER_ENTITY, RENTAL_ENTITY, STORE_ENTITY]:
        for dto_type in ("create", "update", "response"):
            label = f"{'Create' if dto_type=='create' else 'Update' if dto_type=='update' else ''}{entity.name}{'Dto' if dto_type!='response' else 'ResponseDto'}"
            console.print(f"  [cyan]→ {label}[/cyan]")
            code = generator.generate_dto(label, entity, dto_type)
            write(f"src/application/dtos/{dto_type}-{entity.name.lower()}.dto.ts", code)

    console.print()

    # ── Generate controllers (Express/TSOA) ───────────────────────────────────
    console.print("[bold]Generating Express controllers...[/bold]")
    controller_defs = [
        ("CustomerController", CUSTOMER_ENDPOINTS),
        ("RentalController", RENTAL_ENDPOINTS),
        ("StoreController", STORE_ENDPOINTS),
    ]
    for controller_name, endpoints in controller_defs:
        console.print(f"  [cyan]→ {controller_name}[/cyan]")
        code = generator.generate_controller(endpoints, controller_name, domain_knowledge)
        resource = controller_name.replace("Controller", "").lower()
        write(f"src/presentation/controllers/{resource}.controller.ts", code)

    console.print()

    # ── Generate knowledge_extraction.json ────────────────────────────────────
    console.print("[bold]Generating knowledge_extraction.json...[/bold]")
    generate_knowledge_extraction(domain_knowledge)

    console.print()
    console.print("[bold green]All deliverable files generated successfully.[/bold green]")
    console.print()

    # ── Summary ───────────────────────────────────────────────────────────────
    output_files = list((ROOT / "output").rglob("*"))
    ts_files = [f for f in output_files if f.suffix == ".ts"]
    json_files = [f for f in output_files if f.suffix == ".json"]
    console.print(f"  TypeScript files: [green]{len(ts_files)}[/green]")
    console.print(f"  JSON files:       [green]{len(json_files)}[/green]")
    console.print()


if __name__ == "__main__":
    main()
