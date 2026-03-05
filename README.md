# SAKILA AI AGENT

AI-powered tool that converts Java/Spring Boot applications to modern Node.js/TypeScript microservices using LangGraph workflow orchestration and LLM-based code generation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [RAG — Retrieval-Augmented Generation](#rag--retrieval-augmented-generation)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [CLI Commands](#cli-commands)
  - [Quick Examples](#quick-examples)
  - [Git Repository Support](#git-repository-support)
- [Generated Output](#generated-output)
  - [generate_missing.py — Targeted Generation](#generate_missingpy--targeted-generation)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Performance](#performance)
- [Assumptions and Limitations](#assumptions-and-limitations)
- [Token Limit Management](#token-limit-management)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

SAKILA AI AGENT analyzes Java/Spring Boot applications and generates production-ready Node.js/TypeScript code following Clean Architecture principles. It uses LangGraph for multi-step workflow orchestration and OpenAI/Anthropic Claude for intelligent domain extraction and code generation.

**Demonstrated on:** [spring-rest-sakila](https://github.com/codejsha/spring-rest-sakila) — a Spring Boot REST API for the MySQL Sakila DVD rental database. The agent parsed **199 Java classes**, identified **8 bounded contexts**, extracted **30 use cases** and **17 business rules**, and generated **54 TypeScript files** in ~14 minutes.

**What makes this different:**
- **100% LLM-Based Generation** — No templates, pure AI-generated code
- **RAG-Augmented Prompts** — ChromaDB vector store retrieves relevant domain context before every LLM call, producing more accurate and consistent code
- **Clean Architecture** — Domain, Application, Infrastructure, Presentation layers
- **LangGraph Workflow** — State machine orchestration for reliable multi-step transformation
- **Git Integration** — Clone and analyze repositories directly from GitHub/GitLab
- **Domain-Driven Design** — Bounded contexts, use cases, and business rules extracted automatically
- **Type-Safe TypeScript** — Full type coverage with TypeORM

---

## Key Features

### Code Analysis & Parsing
- **Tree-sitter Java Parser** — Accurate AST-based Java code parsing
- **Spring Framework Detection** — Identifies Controllers, Services, Repositories, Entities, Components
- **Dependency Analysis** — Builds complete class dependency graphs
- **Domain Knowledge Extraction** — Extracts bounded contexts, use cases, and business rules via LLM

### Code Generation
- **RAG-Augmented LLM Calls** — Each generation method retrieves semantically similar domain knowledge from ChromaDB before calling the LLM
- **Use Cases** — Business logic with dependency injection and Result pattern
- **DTOs** — Create, Update, Response DTOs aligned to entity fields
- **Repository Interfaces** — Domain layer abstractions
- **Configuration Files** — `package.json`, `tsconfig.json`, `domain_knowledge.json`

### Workflow & Integration
- **LangGraph Orchestration** — State machine workflow with 7 steps
- **Git Repository Support** — Clone from HTTPS/SSH URLs with branch selection
- **Rich CLI** — Progress tracking and verbose output
- **Multiple LLM Providers** — OpenAI (via OpenRouter), Azure OpenAI, Anthropic Claude

---

## Technology Stack

### Agent (Python)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Workflow Engine | LangGraph 0.2+ | State machine orchestration |
| LLM Integration | LangChain 0.3+ | LLM abstraction layer |
| Vector Database | ChromaDB 0.5+ | RAG — semantic retrieval of domain knowledge |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | Local embedding model used by ChromaDB |
| Java Parsing | tree-sitter-java | AST-based code parsing |
| CLI Framework | Click 8.0+ | Command-line interface |
| Console UI | Rich 13.0+ | Terminal output |

### LLM Providers

| Provider | Models | Notes |
|----------|--------|-------|
| OpenAI / OpenRouter | GPT-4o, GPT-4o-mini | Default; used in Sakila demo |
| Azure OpenAI | GPT-4.1, GPT-4 Turbo | Recommended for enterprise |
| Anthropic | Claude Sonnet 4, Claude Opus | Alternative provider |

### Generated Output (Node.js/TypeScript)

| Layer | Technology |
|-------|-----------|
| Language | TypeScript 5+ |
| Framework | Express |
| ORM | TypeORM |
| Runtime | Node.js 20 LTS |

---

## Architecture

### LangGraph Workflow (7-Step State Machine)

```
┌───────────────────────────────────────────────────┐
│                 SAKILA AI AGENT                   │
│              LangGraph Workflow                   │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. Clone repository (if Git URL)                 │
│            ↓                                      │
│  2. Scan & parse Java files (tree-sitter)         │
│            ↓                                      │
│  3. Categorize classes by Spring component        │
│            ↓                                      │
│  4. Build class dependency graph                  │
│            ↓                                      │
│  5. Extract domain knowledge via LLM              │
│     (bounded contexts, use cases, rules)          │
│            ↓                                      │
│  5b. Index domain knowledge → ChromaDB (RAG)      │
│      (entities, rules, use cases, endpoints,      │
│       bounded contexts embedded as vectors)       │
│            ↓                                      │
│  6. Generate TypeScript code via LLM + RAG        │
│     (each call retrieves relevant context         │
│      from ChromaDB before invoking the LLM)       │
│            ↓                                      │
│  7. Write files & export domain_knowledge         │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Clean Architecture — Generated Layer Structure

```
┌───────────────────────────────────────────────┐
│        Presentation Layer (Controllers)       │
│  - Express route handlers                     │
│  - HTTP request/response handling             │
└───────────────────────┬───────────────────────┘
                        │
┌───────────────────────▼───────────────────────┐
│     Application Layer (Use Cases & DTOs)      │
│  - Business orchestration logic               │
│  - Use cases with Result<T> pattern           │
│  - Input/output DTOs                          │
└───────────────────────┬───────────────────────┘
                        │
┌───────────────────────▼───────────────────────┐
│      Domain Layer (Entities & Interfaces)     │
│  - TypeORM entities with relationships        │
│  - Repository interfaces (abstractions)       │
│  - Domain models and business rules           │
└───────────────────────┬───────────────────────┘
                        │
┌───────────────────────▼───────────────────────┐
│     Infrastructure Layer (Implementations)    │
│  - TypeORM repository implementations         │
│  - Database configuration                     │
└───────────────────────────────────────────────┘
```

---

## RAG — Retrieval-Augmented Generation

### Why RAG?

Without RAG, every LLM prompt contains only the immediate object being generated (e.g., a single entity or use case) plus a static system prompt. This means:

- The LLM has **no awareness** of other entities in the domain when generating one entity
- **Business rules** that span multiple entities may be missed
- **Naming consistency** across related files is not guaranteed
- The LLM cannot learn from patterns established by earlier generation calls

With RAG, before each LLM call the agent retrieves the **semantically most relevant domain knowledge** from ChromaDB and injects it into the prompt. The LLM then generates code that is:
- Consistent with other entities, use cases, and endpoints in the domain
- Informed by relevant business rules and data constraints
- Aligned with the bounded context it belongs to

### How It Works

```
Domain Knowledge (after LLM extraction)
        │
        ▼
┌───────────────────────────────────────────────┐
│         DomainKnowledgeRAGStore               │
│   index_domain_knowledge(domain_knowledge)    │
│                                               │
│  Chunk each object into a rich text document  │
│  Embed with sentence-transformers             │
│  Persist in ChromaDB (cosine similarity)      │
└───────────────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  entities        business_rules   use_cases
  collection      collection       collection
        ▼               ▼               ▼
  api_endpoints    bounded_contexts
  collection       collection
                        │
                        ▼
         For each LLM generation call:
         ┌─────────────────────────────┐
         │  retrieve_for_*(query)      │
         │  → ChromaDB cosine search   │
         │  → top-k relevant documents │
         │  → format as context block  │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌─────────────────────────────┐
         │  LLM Prompt                 │
         │  ─────────────────────────  │
         │  [System Prompt]            │
         │  [Object-specific context]  │
         │  === RAG Context ===        │
         │  [Retrieved documents]      │
         │  === End RAG Context ===    │
         │  [Requirements]             │
         └─────────────────────────────┘
                        │
                        ▼
              Context-aware TypeScript code
```

### ChromaDB Collections

Five collections are maintained, one per domain object type:

| Collection | What is indexed | Metadata stored |
|---|---|---|
| `entities` | Name, type, properties, business rules, relationships, validations, lifecycle | `name`, `type`, `relationship_count` |
| `business_rules` | Name, description, source method, conditions, actions, exceptions | `name`, `source_method` |
| `use_cases` | Name, description, actors, entities involved, steps, pre/postconditions, error scenarios | `name`, `entities_involved` |
| `api_endpoints` | Method + path, description, business operation, params, validation rules, error scenarios | `method`, `path`, `business_operation` |
| `bounded_contexts` | Name, purpose, entities, dependencies | `name` |

### Chunking Strategy

Each domain object is serialized into a structured, plain-text document that captures all its semantically relevant attributes:

```
# Entity chunk example
Domain Entity: Customer
Type: aggregate_root
Properties: customerId: number, firstName: string, lastName: string, email: string
Business Rules: Email must be unique; Customer must be active to rent DVDs
Relationships: Address (ManyToOne), Rental (OneToMany)
Validations: email must match RFC-5322 format
Lifecycle: Created on registration; soft-deleted on account closure
```

```
# Business Rule chunk example
Business Rule: ActiveCustomerOnly
Description: Only customers with active status may initiate rental transactions
Source: RentalService.createRental
Conditions: customer.active == true
Actions: Proceed with rental creation
Exceptions: CustomerInactiveException
```

This format maximises semantic signal for the embedding model without token waste.

### Embedding Strategy

| Property | Value |
|---|---|
| Model | `all-MiniLM-L6-v2` (ChromaDB default) |
| Runs | **Locally** — no API key required for embeddings |
| Distance metric | Cosine similarity |
| Persistence | Local directory (`.chroma_db/` by default, configurable) |
| Re-indexing | Idempotent — uses `upsert`, safe to re-run |

### Retrieval per Generation Type

| Generator method | Collections queried | Excluded from results |
|---|---|---|
| `generate_entity` | `entities` (similar), `business_rules`, `bounded_contexts` | The entity itself |
| `generate_use_case` | `use_cases` (similar), `entities`, `business_rules` | The use case itself |
| `generate_controller` | `api_endpoints`, `use_cases`, `entities` | — |
| `generate_repository_interface` | `entities` (related), `business_rules` | The entity itself |
| `generate_repository_implementation` | `entities` (related), `business_rules` | The entity itself |
| `generate_dto` | `entities`, `use_cases` | — |

### RAG Context Block in Prompts

Retrieved documents are injected as a clearly delimited block:

```
=== RAG Context: Retrieved Domain Knowledge ===

Similar/Related Entities in the Domain:
Domain Entity: Rental
Type: aggregate_root
Properties: rentalId: number, rentalDate: Date, customerId: number, inventoryId: number
...
---
Domain Entity: Payment
...

Relevant Business Rules:
Business Rule: PaymentRequired
Description: Payment must be processed before rental is marked as returned
...

Bounded Context:
Bounded Context: Rental Management
Purpose: Rental transactions and statuses
Entities: RentalEntity
...

=== End of RAG Context ===
```

### Configuration

All RAG settings can be overridden in `.env`:

```env
# Enable or disable RAG entirely (default: true)
ENABLE_RAG=true

# Local directory where ChromaDB persists its vector index
CHROMA_PERSIST_DIR=./.chroma_db

# Number of similar documents to retrieve per query (1–10, default: 3)
RAG_TOP_K=3
```

Setting `ENABLE_RAG=false` falls back to the original plain-prompt behaviour with no ChromaDB dependency at runtime.

---

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Clone and Setup

```bash
# Clone the agent
git clone https://github.com/your-org/spring-rest-sakila-agent.git
cd spring-rest-sakila-agent

# Install dependencies
uv sync

# Verify installation
uv run python cli.py --help
```

---

## Configuration

Create a `.env` file in the project root:

### Option 1: OpenAI Direct (used in Sakila demo)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...          # native OpenAI key (sk-proj-...)
OPENAI_API_BASE=                    # leave empty for direct OpenAI API
OPENAI_MODEL=gpt-4o-mini            # use native model name (NOT openai/gpt-4o-mini)
OPENAI_TEMPERATURE=0.3
MAX_TOKENS=4096
MAX_TOKENS_PER_REQUEST=4096
```

> **Important:** If using OpenRouter instead of direct OpenAI, set `OPENAI_API_BASE=https://openrouter.ai/api/v1`, use an `sk-or-...` key, and prefix the model name: `OPENAI_MODEL=openai/gpt-4o-mini`.

### Option 1b: OpenAI via OpenRouter

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-or-...            # OpenRouter key
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini     # vendor-prefixed model name
OPENAI_TEMPERATURE=0.3
MAX_TOKENS=4096
MAX_TOKENS_PER_REQUEST=4096
```

### Option 2: Azure OpenAI

```env
LLM_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_TEMPERATURE=0.2
```

### Option 3: Anthropic Claude

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5
ANTHROPIC_TEMPERATURE=0.2
```

### RAG / ChromaDB Settings (optional — defaults work out of the box)

```env
# Retrieval-Augmented Generation
ENABLE_RAG=true
CHROMA_PERSIST_DIR=./.chroma_db
RAG_TOP_K=3
```

### Verify Configuration

```bash
uv run python cli.py config
```

---

## Usage

### CLI Commands

#### `convert` — Full Java to Node.js Conversion

```bash
uv run python cli.py convert JAVA_REPO_PATH [OPTIONS]

Options:
  --output, -o TEXT    Output directory (default: ./output)
  --verbose, -v        Enable verbose output
  --branch, -b TEXT    Git branch (for Git URLs)
  --yes, -y            Skip confirmation prompt (for CI/automation)
  --help               Show this message and exit
```

#### `analyze` — Domain Analysis Only (no code generation)

```bash
uv run python cli.py analyze JAVA_REPO_PATH [OPTIONS]

Options:
  --verbose, -v        Show detailed analysis
  --branch, -b TEXT    Git branch (for Git URLs)
  --help               Show this message and exit
```

#### `config` — Show current LLM configuration

```bash
uv run python cli.py config
```

#### `examples` — Show usage examples

```bash
uv run python cli.py examples
```

---

### Quick Examples

#### Convert from GitHub (spring-rest-sakila)

```bash
uv run python cli.py convert \
  https://github.com/codejsha/spring-rest-sakila \
  --output ./output \
  --yes \
  -v
```

> **Tip:** Use `--yes` / `-y` to skip the interactive confirmation prompt — required for CI pipelines and non-interactive terminals.

#### Convert a local repository

```bash
uv run python cli.py convert \
  /path/to/spring-rest-sakila \
  --output ./sakila-nodejs \
  --verbose
```

#### Convert a specific branch via SSH

```bash
uv run python cli.py convert \
  git@github.com:codejsha/spring-rest-sakila.git \
  --branch main \
  --output ./converted \
  -v
```

#### Analyze without generating code

```bash
uv run python cli.py analyze \
  https://github.com/codejsha/spring-rest-sakila \
  --verbose
```

---

### Git Repository Support

**Supported URL formats:**
- HTTPS: `https://github.com/user/repo.git`
- SSH: `git@github.com:user/repo.git`
- Git Protocol: `git://github.com/user/repo.git`

The repository is cloned to a temporary directory, converted, and the temp directory is automatically cleaned up. Output is saved to `--output`.

---

## Generated Output

### File Structure (spring-rest-sakila result)

```
output/                                         # 54 TypeScript files total
├── src/
│   ├── presentation/
│   │   └── controllers/                        # Express route handlers (LLM + RAG generated)
│   │       ├── customer.controller.ts           # 5 REST endpoints (GET list, GET by id, POST, PUT, DELETE)
│   │       ├── rental.controller.ts             # 3 REST endpoints (GET list, POST, PUT return)
│   │       └── store.controller.ts              # 4 REST endpoints (GET list, GET by id, POST, PUT)
│   │
│   ├── application/
│   │   └── use-cases/                           # 30 AI-generated use cases
│   │       ├── report-sales-by-category.use-case.ts
│   │       ├── report-sales-by-store.use-case.ts
│   │       ├── manage-store-list.use-case.ts
│   │       ├── add-new-store.use-case.ts
│   │       ├── update-store-information.use-case.ts
│   │       ├── delete-store.use-case.ts
│   │       ├── manage-staff-list.use-case.ts
│   │       ├── add-new-staff.use-case.ts
│   │       ├── update-staff-information.use-case.ts
│   │       ├── delete-staff.use-case.ts
│   │       ├── manage-rental-transactions.use-case.ts
│   │       ├── manage-customer-payments.use-case.ts
│   │       ├── manage-customer-information.use-case.ts
│   │       ├── manage-film-inventory.use-case.ts
│   │       ├── user-login.use-case.ts
│   │       └── ... (15 additional use cases)
│   │
│   ├── infrastructure/
│   │   └── repositories/                        # TypeORM repository implementations (DAOs)
│   │       ├── customer.repository.impl.ts      # CRUD + search by name, email, active filter
│   │       ├── rental.repository.impl.ts        # CRUD + overdue check, return processing
│   │       └── store.repository.impl.ts         # CRUD + manager lookup
│   │
│   └── domain/
│       ├── entities/                            # TypeORM entity classes
│       │   ├── customer.entity.ts               # CustomerEntity — 9 fields, Address ManyToOne
│       │   ├── rental.entity.ts                 # RentalEntity — 6 fields, Customer/Inventory FKs
│       │   └── store.entity.ts                  # StoreEntity — 4 fields, Staff/Address FKs
│       │
│       ├── repositories/                        # Repository interfaces (domain abstractions)
│       │   ├── customer.repository.ts           # ICustomerRepository interface
│       │   ├── rental.repository.ts             # IRentalRepository interface
│       │   └── store.repository.ts              # IStoreRepository interface
│       │
│       └── dtos/                                # Input/output DTOs
│           ├── customer-create.dto.ts           # CreateCustomerDto
│           ├── customer-update.dto.ts           # UpdateCustomerDto
│           ├── customer-response.dto.ts         # CustomerResponseDto
│           ├── rental-create.dto.ts             # CreateRentalDto
│           ├── rental-update.dto.ts             # UpdateRentalDto
│           ├── rental-response.dto.ts           # RentalResponseDto
│           ├── store-create.dto.ts              # CreateStoreDto
│           ├── store-update.dto.ts              # UpdateStoreDto
│           └── store-response.dto.ts            # StoreResponseDto
│
├── package.json                                 # Node.js project (name: spring-rest-sakila)
├── tsconfig.json                                # TypeScript configuration
├── domain_knowledge.json                        # Extracted domain knowledge (8 bounded contexts)
└── knowledge_extraction.json                    # Structured module/method index (projectOverview + modules[])
```

> **Note:** The 3 entities, 3 repository interfaces, 3 repository implementations, 9 DTOs, and 3 controllers were generated using the `generate_missing.py` supplementary script (see [generate_missing.py](#generate_missingpy--targeted-generation) below). The main pipeline generated the 30 use cases and configuration files.

### Generated Code Examples

**Store DTO — aligned to Sakila `StoreEntity`:**
```typescript
export interface StoreDTO {
  managerStaffId: number;
  addressId: number;
}

export interface IStoreRepository {
  getAllStores(): Promise<Store[]>;
  addStore(storeData: StoreDTO): Promise<void>;
  exists(storeId: number): Promise<boolean>;
  delete(storeId: number): Promise<void>;
}
```

**Use Case — Add New Store:**
```typescript
export class AddNewStoreUseCase {
  constructor(
    private storeRepository: IStoreRepository,
    private authService: IAuthService
  ) {}

  public async execute(userId: string, storeData: StoreDTO): Promise<Result<void>> {
    if (!this.authService.isAuthenticated(userId))
      return Result.fail('User is not authenticated.');
    if (!this.authService.hasAdminPrivileges(userId))
      return Result.fail('User does not have admin privileges.');

    const errors = this.validateStoreData(storeData);
    if (errors.length > 0)
      return Result.fail(`Validation errors: ${errors.join(', ')}`);

    await this.storeRepository.addStore(storeData);
    return Result.ok();
  }
}
```

**Use Case — Manage Rental Transactions:**
```typescript
export class ManageRentalTransactionsUseCase {
  constructor(
    private rentalRepository: IRentalRepository,
    private authService: IAuthService
  ) {}

  public async execute(request: RentDvdRequestDto): Promise<Result<RentDvdResponseDto>> {
    if (!this.authService.isAuthenticated(request.userId))
      return Result.fail('User is not authenticated.');
    if (!this.authService.isStoreStaff(request.userId))
      return Result.fail('User is not authorized as store staff.');

    const isAvailable = await this.rentalRepository.checkInventory(request.dvdId);
    if (!isAvailable)
      return Result.fail('DVD is not available for rent.');

    await this.rentalRepository.processRental(request.dvdId, request.userId);
    return Result.ok(new RentDvdResponseDto('DVD rented successfully.'));
  }
}
```

### `generate_missing.py` — Targeted Generation

When the main pipeline LLM extraction step produces incomplete entity or API endpoint data (e.g., due to token truncation with 199-class projects), use the supplementary `generate_missing.py` script to generate the core Clean Architecture files with hardcoded Sakila domain knowledge:

```bash
# After running the main pipeline (which generates use cases and domain_knowledge.json):
PYTHONUTF8=1 uv run python generate_missing.py
```

This script:
- Defines `Customer`, `Rental`, and `Store` domain entities with full Sakila schema fields
- Defines REST API endpoints for each entity
- Calls `DomainKnowledgeRAGStore` to index and `LLMCodeCreator` to generate all files via LLM + RAG:
  - 3 TypeORM entities (`customer.entity.ts`, `rental.entity.ts`, `store.entity.ts`)
  - 3 repository interfaces (`customer.repository.ts`, etc.)
  - 3 TypeORM repository implementations (`customer.repository.impl.ts`, etc.)
  - 9 DTOs (create / update / response × 3 entities)
  - 3 Express controllers (`customer.controller.ts`, `rental.controller.ts`, `store.controller.ts`)
  - `knowledge_extraction.json` — structured module/method index

### Domain Knowledge Export

The `domain_knowledge.json` file captures all extracted knowledge:

```json
{
  "project_name": "spring-rest-sakila",
  "domain": "DVD rental store management - films, customers, rentals, payments, staff, and stores.",
  "bounded_contexts": [
    { "name": "Authentication",     "entities": ["AuthorityEntity"],                               "purpose": "User authentication and authorization." },
    { "name": "Catalog Management", "entities": ["FilmEntity", "ActorEntity", "CategoryEntity"],   "purpose": "Manages films, actors, and categories." },
    { "name": "Customer Management","entities": ["CustomerEntity"],                                "purpose": "Manages customer information and interactions." },
    { "name": "Location Management","entities": ["AddressEntity", "CityEntity", "CountryEntity"],  "purpose": "Geographical data including addresses, cities, countries." },
    { "name": "Payment Processing", "entities": ["PaymentEntity"],                                "purpose": "Manages payment transactions." },
    { "name": "Rental Management",  "entities": ["RentalEntity"],                                 "purpose": "Rental transactions and statuses." },
    { "name": "Staff Management",   "entities": ["StaffEntity"],                                  "purpose": "Staff information and roles." },
    { "name": "Store Management",   "entities": ["StoreEntity", "InventoryEntity"],               "purpose": "Inventory and store-related operations." }
  ],
  "use_cases": [
    { "name": "Report Sales by Category",  "actors": ["Manager", "Sales Analyst"] },
    { "name": "Report Sales by Store",     "actors": ["Manager", "Sales Analyst"] },
    { "name": "Manage Store List",         "actors": ["Admin"] },
    { "name": "Add New Store",             "actors": ["Admin"] },
    { "name": "Update Store Information",  "actors": ["Admin"] },
    { "name": "Delete Store",              "actors": ["Admin"] },
    { "name": "Manage Staff List",         "actors": ["Admin"] },
    { "name": "Add New Staff",             "actors": ["Admin"] },
    { "name": "Update Staff Information",  "actors": ["Admin"] },
    { "name": "Delete Staff",              "actors": ["Admin"] },
    { "name": "Manage Rental Transactions","actors": ["Store Staff", "Customer"] },
    { "name": "Manage Customer Payments",  "actors": ["Store Staff", "Customer"] },
    { "name": "Manage Customer Information","actors": ["Store Staff"] },
    { "name": "Manage Film Inventory",     "actors": ["Store Staff"] },
    { "name": "User Login",                "actors": ["User"] }
  ],
  "business_rules": [
    "Film ID must not be null (InventoryEntity)",
    "Store ID must not be null (InventoryEntity)",
    "Username must be 1-16 characters (StaffEntity)",
    "Rental date must not be null (RentalEntity)",
    "Payment amount must not be null (PaymentEntity)"
  ]
}
```

---

## Project Structure

```
spring-rest-sakila-agent/
├── src/
│   ├── config/
│   │   └── settings.py              # LLM, RAG, and app configuration
│   │
│   ├── graph/
│   │   ├── state.py                 # LangGraph state definitions
│   │   ├── nodes.py                 # Workflow node implementations (7 steps)
│   │   └── workflow.py              # LangGraph workflow definition
│   │
│   ├── parsers/
│   │   └── java_parser.py           # tree-sitter Java AST parser
│   │
│   ├── analyzers/
│   │   ├── code_scanner.py          # Repository file scanner
│   │   ├── class_categorizer.py     # Spring component detection
│   │   └── dependency_mapper.py     # Class dependency graph builder
│   │
│   ├── llm/
│   │   ├── llm_client_provider.py   # LLM provider abstraction (OpenAI/Azure/Anthropic)
│   │   ├── llm_domain_extractor.py  # Domain knowledge extraction via LLM
│   │   └── llm_prompt_templates.py  # LLM prompt templates
│   │
│   ├── rag/                         # RAG module (ChromaDB vector store)
│   │   ├── __init__.py
│   │   └── rag_store.py             # DomainKnowledgeRAGStore — chunk, embed, retrieve
│   │
│   ├── models/
│   │   ├── java_models.py           # Java AST data models
│   │   ├── domain_models.py         # DDD domain models
│   │   └── architecture_models.py   # Architecture design models
│   │
│   ├── generators/
│   │   ├── llm_code_creator.py      # TypeScript code generation via LLM + RAG
│   │   └── file_writer.py           # Output file writer
│   │
│   └── utils/
│       ├── token_counter.py         # Token usage tracking
│       └── logger.py                # Logging utilities
│
├── .chroma_db/                      # ChromaDB persistent vector index (auto-created)
│
├── output/                          # Generated TypeScript project (54 files)
│   ├── src/
│   │   ├── presentation/controllers/  # 3 Express controllers
│   │   ├── application/use-cases/     # 30 generated use cases
│   │   ├── infrastructure/repositories/ # 3 TypeORM repository implementations
│   │   └── domain/
│   │       ├── entities/              # 3 TypeORM entities
│   │       ├── repositories/          # 3 repository interfaces
│   │       └── dtos/                  # 9 DTOs (create/update/response × 3)
│   ├── package.json
│   ├── tsconfig.json
│   ├── domain_knowledge.json
│   └── knowledge_extraction.json
│
├── generate_missing.py              # Supplementary script for targeted entity/controller/DAO generation
├── cli.py                           # CLI entry point
├── pyproject.toml                   # Python project configuration
├── .env                             # LLM + RAG credentials/config (not committed)
└── README.md                        # This file
```

---

## How It Works

1. **Clone** — If a Git URL is provided, the repository is cloned to a temp directory.

2. **Scan & Parse** — All `.java` files are scanned and parsed with tree-sitter to extract class names, annotations, methods, fields, and inheritance.

3. **Categorize** — Each class is categorized by Spring component type: `@RestController`, `@Service`, `@Repository`, `@Entity`, `@Component`, `@Configuration`.

4. **Dependency Graph** — A directed dependency graph is built across all classes to understand how components interact.

5. **Domain Extraction (LLM)** — The LLM identifies bounded contexts (DDD), extracts use cases, business rules, and entity relationships from the parsed class summaries.

5b. **RAG Indexing (ChromaDB)** — The extracted `DomainKnowledge` is chunked and embedded into five ChromaDB collections (`entities`, `business_rules`, `use_cases`, `api_endpoints`, `bounded_contexts`). This happens automatically on the first code generation call and is idempotent. The index is persisted locally under `.chroma_db/` and reused across runs.

6. **Code Generation (LLM + RAG)** — For each entity, use case, controller, repository, and DTO:
   - A semantic query is issued against ChromaDB to retrieve the top-k most relevant domain documents
   - The retrieved context is injected into the LLM prompt as a clearly labelled `=== RAG Context ===` block
   - The LLM generates TypeScript code that is aware of the full domain — not just the single object being generated

7. **Write Output** — All generated TypeScript files, `package.json`, `tsconfig.json`, and `domain_knowledge.json` are written to the output directory.

---

## Performance

### Benchmark — spring-rest-sakila

Source: [https://github.com/codejsha/spring-rest-sakila](https://github.com/codejsha/spring-rest-sakila)
Spring Boot REST API for the MySQL Sakila DVD rental database.

| Metric | Result |
|--------|--------|
| Java Files Scanned | 200 |
| Java Classes Parsed | 199 |
| Bounded Contexts Extracted | 8 |
| Use Cases Generated | 30 |
| Business Rules Identified | 17 |
| TypeScript Files Written | 54 |
| Execution Time | ~840 seconds (~14 min) |
| LLM Provider | OpenAI GPT-4o-mini (direct) |

### Bounded Contexts Identified

| Context | Entities |
|---------|----------|
| Authentication | AuthorityEntity |
| Catalog Management | FilmEntity, ActorEntity, CategoryEntity |
| Customer Management | CustomerEntity |
| Location Management | AddressEntity, CityEntity, CountryEntity |
| Payment Processing | PaymentEntity |
| Rental Management | RentalEntity |
| Staff Management | StaffEntity |
| Store Management | StoreEntity, InventoryEntity |

### Cost Estimates

| App Size | Classes | Estimated Cost (GPT-4o-mini) |
|----------|---------|-------------------------------|
| Small | 10-20 | ~$0.01 - $0.05 |
| Medium | 30-50 | ~$0.05 - $0.15 |
| Large | 100-200 | ~$0.20 - $0.50 |

---

## Assumptions and Limitations

### Assumptions

| Assumption | Detail |
|-----------|--------|
| **Java version** | Source project uses Java 11+ with Spring Boot 2.x/3.x |
| **Spring annotations** | Classes are annotated with `@RestController`, `@Service`, `@Repository`, `@Entity` — bare classes without annotations are skipped |
| **Build tool** | Maven or Gradle project (pom.xml or build.gradle present); used to locate source root |
| **Package structure** | Standard Maven layout (`src/main/java/`) expected for file scanning |
| **Database** | Generated TypeORM code assumes a relational database (MySQL/PostgreSQL). No MongoDB/NoSQL support |
| **Authentication** | Converted Express code assumes a JWT-based `requireAuth` / `requireRole` middleware exists in the target project |
| **Field naming** | Entity fields in generated DTOs are derived from Java field names; they must match actual DB column names (or TypeORM `@Column(name=...)` overrides must be added manually) |
| **Relationships** | ManyToOne/OneToMany/ManyToMany JPA relationships are noted in domain_knowledge.json but not fully generated as TypeORM `@Relation` decorators |

### Limitations

| Limitation | Impact / Workaround |
|-----------|---------------------|
| **LLM context window** | Large projects (200+ classes) exceed single-prompt context. The agent batches classes but very large monorepos may produce incomplete domain extraction. Increase `MAX_TOKENS_PER_REQUEST` to 4096+ and consider splitting by bounded context. |
| **Abstract use cases** | AI-generated use cases model business intent (not 1:1 method mapping). For exact endpoint parity, use the manually converted `customer.controller.ts` / `customer.service.ts` as the reference pattern. |
| **No test generation** | Unit and integration tests are not generated. Manual test authoring is required for the output project. |
| **No migration scripts** | Database migration files (Flyway/Liquibase → TypeORM migrations) are not generated. Schema must be created separately. |
| **MapStruct not reproduced** | Java MapStruct mappers are replaced with inline `toDto()` helper functions. For large projects with many DTOs this may require cleanup. |
| **QueryDSL complexity** | Very complex QueryDSL queries (multi-level joins, subqueries) are approximated with TypeORM `QueryBuilder`. Review each repository method for correctness. |
| **Security roles** | Spring Security `@Secured`/`@PreAuthorize` expressions are converted to role string constants. The actual middleware implementation is left to the developer. |
| **Windows encoding** | Running on Windows requires `PYTHONUTF8=1` or PowerShell UTF-8 mode to avoid `UnicodeEncodeError` on non-ASCII characters in console output. |

---

## Token Limit Management

### The Problem

The Sakila project contains **199 Java classes** across 200 files. Sending all class summaries to the LLM in a single prompt exceeds typical context windows and causes:
- Truncated LLM responses (mid-JSON cuts)
- Empty entity lists in extracted domain knowledge
- Missing API contracts in `domain_knowledge.json`

### How the Agent Handles It

**1. Batched Class Processing**

Classes are grouped and sent to the LLM in batches rather than all at once. `MAX_TOKENS_PER_REQUEST` controls the maximum tokens per individual LLM call.

```env
MAX_TOKENS_PER_REQUEST=4096   # recommended for projects > 50 classes
MAX_TOKENS=4096               # max tokens per LLM response
```

**2. Structured Summaries (not full source)**

The agent does **not** send raw Java source to the LLM. Instead, tree-sitter parses each file and extracts only:
- Class name, type (Controller/Service/Repository/Entity)
- Method signatures and annotations
- Field names and types
- Direct class dependencies

This compressed representation is ~10-20x smaller than the full source, enabling more classes per prompt.

**3. Domain Extraction vs. Code Generation Separation**

Token usage is split across two LLM calls per workflow run:
- **Step 5 (domain extraction)**: Processes all class summaries → produces bounded contexts, use cases, business rules
- **Step 6 (code generation)**: One LLM call per use case → generates a single TypeScript file per call

This prevents any single call from needing both full analysis and code generation simultaneously.

**4. Recommended Settings by Project Size**

| Project Size | Classes | `MAX_TOKENS` | `MAX_TOKENS_PER_REQUEST` |
|-------------|---------|-------------|--------------------------|
| Small       | < 30    | 2000        | 2000                     |
| Medium      | 30–100  | 4096        | 4096                     |
| Large       | 100–200 | 4096        | 4096                     |
| Very Large  | 200+    | 8192        | 8192 (GPT-4o recommended)|

**5. Practical Notes from the Sakila Run**

During the Sakila demonstration run (`MAX_TOKENS_PER_REQUEST=4096`), the domain extraction step produced **30 use cases** and **17 business rules** across 8 bounded contexts, but entity-level detail (individual entity fields and API endpoints) was incomplete due to LLM response truncation mid-JSON. Use `generate_missing.py` to supplement the main pipeline with targeted entity/controller/DAO generation in that case.

Setting `MAX_TOKENS_PER_REQUEST=4096` is the minimum recommended value for a 199-class project. For complete entity extraction in a single pass, use GPT-4o with `MAX_TOKENS=8192`.

---

## Development

### Run Tests

```bash
uv sync --extra dev
uv run pytest
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
uv run black src/ cli.py
uv run ruff check src/ cli.py
uv run mypy src/ cli.py
```

### Development Mode

```bash
uv pip install -e .
sakila-agent convert https://github.com/codejsha/spring-rest-sakila
```

---

## Troubleshooting

### "No API key found" / "Connection error" / 401 Authentication error

Ensure `.env` uses the correct key format and base URL for your provider:

**Direct OpenAI (recommended):**
```env
OPENAI_API_KEY=sk-proj-...    # native OpenAI key
OPENAI_API_BASE=              # leave empty
OPENAI_MODEL=gpt-4o-mini      # native model name (no vendor prefix)
```

**OpenRouter:**
```env
OPENAI_API_KEY=sk-or-...                        # OpenRouter key
OPENAI_API_BASE=https://openrouter.ai/api/v1    # OpenRouter base URL
OPENAI_MODEL=openai/gpt-4o-mini                 # vendor-prefixed model name
```

> **Common mistake:** Using a native OpenAI key (`sk-proj-...`) with the OpenRouter base URL causes a `401 Missing Authentication header` error. Similarly, using model name `openai/gpt-4o-mini` with direct OpenAI causes a `400 invalid model ID` error.

Verify with: `uv run python cli.py config`

### "Failed to clone repository"

```bash
# Test the URL manually
git ls-remote https://github.com/codejsha/spring-rest-sakila

# For private repos, use SSH
uv run python cli.py convert git@github.com:user/private-repo.git
```

### JSON parse errors during domain extraction

Increase token limits in `.env`:
```env
MAX_TOKENS=4096
MAX_TOKENS_PER_REQUEST=4096
```
This occurs when the LLM response is too long and gets truncated mid-JSON.

### Unicode errors on Windows

Run with UTF-8 mode:
```bash
PYTHONUTF8=1 uv run python cli.py convert ...
```

### "Module not found"

```bash
uv sync --reinstall
```

### ChromaDB / RAG issues

**`ModuleNotFoundError: No module named 'chromadb'`**

```bash
pip install chromadb>=0.5.0
# or, if using uv:
uv sync
```

**`sentence-transformers` not found / embedding errors**

ChromaDB's default embedding function requires `sentence-transformers`. It is installed automatically as a `chromadb` transitive dependency. If it is missing:

```bash
pip install sentence-transformers
```

**Disable RAG to skip ChromaDB entirely**

```env
ENABLE_RAG=false
```

**Clear and rebuild the vector index**

Delete the `.chroma_db/` directory to force a full re-index on the next run:

```bash
rm -rf .chroma_db/
```

**Change the ChromaDB persistence location**

```env
CHROMA_PERSIST_DIR=/path/to/custom/chroma_dir
```

---

## License

MIT License — Copyright (c) 2025 SAKILA AI AGENT

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) by LangChain — workflow orchestration
- [ChromaDB](https://www.trychroma.com/) — vector database powering the RAG layer
- [sentence-transformers](https://www.sbert.net/) — local embedding model (`all-MiniLM-L6-v2`)
- [tree-sitter](https://tree-sitter.github.io/) — Java AST parsing
- [spring-rest-sakila](https://github.com/codejsha/spring-rest-sakila) — source Java project used for demonstration
- [OpenRouter](https://openrouter.ai/) — LLM API gateway
