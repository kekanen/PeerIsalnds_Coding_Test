"""
RAG-based domain knowledge store using ChromaDB.

Indexes domain knowledge as vector embeddings for semantic retrieval,
providing relevant context to LLM prompts during code generation.

Chunking strategy:
  - Each DomainEntity  → one document with properties, rules, relationships
  - Each BusinessRule  → one document
  - Each UseCase       → one document
  - Each APIEndpoint   → one document
  - Each BoundedContext → one document

Embedding strategy:
  - Uses ChromaDB's built-in default embedding (sentence-transformers
    all-MiniLM-L6-v2) so no external API calls are needed for embeddings.
  - Stored in a persistent local ChromaDB directory (configurable).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import chromadb

from src.models.domain_models import (
    APIEndpoint,
    BoundedContext,
    BusinessRule,
    DomainEntity,
    DomainKnowledge,
    UseCase,
)

logger = logging.getLogger(__name__)

# ── ChromaDB collection names ─────────────────────────────────────────────────
_COL_ENTITIES = "entities"
_COL_RULES = "business_rules"
_COL_USE_CASES = "use_cases"
_COL_ENDPOINTS = "api_endpoints"
_COL_CONTEXTS = "bounded_contexts"


class DomainKnowledgeRAGStore:
    """
    ChromaDB-backed RAG store for domain knowledge.

    Usage
    -----
    1. Call ``index_domain_knowledge(domain_knowledge)`` once after extraction.
    2. Call the appropriate ``retrieve_for_*`` method before each LLM generation
       to obtain a context string that is injected into the LLM prompt.
    """

    def __init__(self, persist_dir: str = "./.chroma_db", top_k: int = 3) -> None:
        """
        Args:
            persist_dir: Local directory where ChromaDB persists its data.
            top_k: Number of semantically similar documents to retrieve per query.
        """
        self.persist_dir = persist_dir
        self.top_k = top_k
        self._client: Optional[chromadb.ClientAPI] = None
        self._collections: dict[str, chromadb.Collection] = {}
        self._initialized = False

    # ── Lazy client init ──────────────────────────────────────────────────────

    def _get_client(self) -> chromadb.ClientAPI:
        if self._client is None:
            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_dir)
        return self._client

    def _collection(self, name: str) -> chromadb.Collection:
        if name not in self._collections:
            self._collections[name] = self._get_client().get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[name]

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def index_domain_knowledge(self, domain_knowledge: DomainKnowledge) -> None:
        """
        Chunk and embed the entire domain knowledge graph into ChromaDB.

        Safe to call multiple times; uses upsert so re-runs are idempotent.
        """
        logger.info("Indexing domain knowledge into ChromaDB RAG store …")
        self._index_entities(domain_knowledge.entities)
        self._index_business_rules(domain_knowledge.business_rules)
        self._index_use_cases(domain_knowledge.use_cases)
        self._index_api_endpoints(domain_knowledge.api_contracts)
        self._index_bounded_contexts(domain_knowledge.bounded_contexts)
        self._initialized = True
        logger.info(
            "RAG store ready: %d entities, %d rules, %d use-cases, "
            "%d endpoints, %d contexts indexed.",
            len(domain_knowledge.entities),
            len(domain_knowledge.business_rules),
            len(domain_knowledge.use_cases),
            len(domain_knowledge.api_contracts),
            len(domain_knowledge.bounded_contexts),
        )

    # ── Retrieval helpers ─────────────────────────────────────────────────────

    def retrieve_for_entity(self, entity_name: str, entity_description: str = "") -> str:
        """Return RAG context for entity code generation."""
        query = f"domain entity {entity_name} {entity_description}"
        sections: list[str] = []

        similar = self._query(
            _COL_ENTITIES, query, exclude_ids=[f"entity_{entity_name}"]
        )
        if similar:
            sections.append("Similar/Related Entities in the Domain:\n" + _join(similar))

        rules = self._query(_COL_RULES, f"{entity_name} validation constraint rule")
        if rules:
            sections.append("Relevant Business Rules:\n" + _join(rules))

        ctx = self._query(_COL_CONTEXTS, query, n=2)
        if ctx:
            sections.append("Bounded Context:\n" + _join(ctx))

        return _format_context(sections)

    def retrieve_for_use_case(self, use_case_name: str, description: str = "") -> str:
        """Return RAG context for use-case code generation."""
        query = f"use case {use_case_name} {description}"
        sections: list[str] = []

        similar = self._query(
            _COL_USE_CASES, query, exclude_ids=[f"usecase_{use_case_name[:40]}"]
        )
        if similar:
            sections.append("Related Use Cases:\n" + _join(similar))

        entities = self._query(_COL_ENTITIES, query)
        if entities:
            sections.append("Related Domain Entities:\n" + _join(entities))

        rules = self._query(_COL_RULES, query)
        if rules:
            sections.append("Relevant Business Rules:\n" + _join(rules))

        return _format_context(sections)

    def retrieve_for_controller(
        self, resource_name: str, endpoint_summary: str = ""
    ) -> str:
        """Return RAG context for controller code generation."""
        query = f"REST controller {resource_name} HTTP {endpoint_summary}"
        sections: list[str] = []

        endpoints = self._query(_COL_ENDPOINTS, query)
        if endpoints:
            sections.append("Related API Endpoint Patterns:\n" + _join(endpoints))

        use_cases = self._query(_COL_USE_CASES, query)
        if use_cases:
            sections.append("Related Use Cases:\n" + _join(use_cases))

        entities = self._query(_COL_ENTITIES, query, n=2)
        if entities:
            sections.append("Related Domain Entities:\n" + _join(entities))

        return _format_context(sections)

    def retrieve_for_repository(self, entity_name: str) -> str:
        """Return RAG context for repository code generation."""
        query = f"repository data access {entity_name} CRUD queries"
        sections: list[str] = []

        entities = self._query(
            _COL_ENTITIES, query, exclude_ids=[f"entity_{entity_name}"]
        )
        if entities:
            sections.append("Related Entities for Reference:\n" + _join(entities))

        rules = self._query(
            _COL_RULES, f"{entity_name} data constraint validation", n=3
        )
        if rules:
            sections.append("Data Constraints and Business Rules:\n" + _join(rules))

        return _format_context(sections)

    def retrieve_for_dto(self, entity_name: str, dto_type: str = "") -> str:
        """Return RAG context for DTO code generation."""
        query = f"{dto_type} DTO {entity_name} data transfer validation"
        sections: list[str] = []

        entities = self._query(_COL_ENTITIES, query, n=2)
        if entities:
            sections.append("Related Entities:\n" + _join(entities))

        use_cases = self._query(_COL_USE_CASES, f"{entity_name} {dto_type}", n=2)
        if use_cases:
            sections.append("Use Cases Using This DTO:\n" + _join(use_cases))

        return _format_context(sections)

    # ── Indexing internals ────────────────────────────────────────────────────

    def _index_entities(self, entities: List[DomainEntity]) -> None:
        if not entities:
            return
        col = self._collection(_COL_ENTITIES)
        col.upsert(
            documents=[_chunk_entity(e) for e in entities],
            metadatas=[
                {
                    "name": e.name,
                    "type": e.type.value,
                    "relationship_count": len(e.relationships),
                }
                for e in entities
            ],
            ids=[f"entity_{e.name}" for e in entities],
        )

    def _index_business_rules(self, rules: List[BusinessRule]) -> None:
        if not rules:
            return
        col = self._collection(_COL_RULES)
        col.upsert(
            documents=[_chunk_rule(r) for r in rules],
            metadatas=[
                {"name": r.name, "source_method": r.source_method} for r in rules
            ],
            ids=[f"rule_{i}_{r.name[:30]}" for i, r in enumerate(rules)],
        )

    def _index_use_cases(self, use_cases: List[UseCase]) -> None:
        if not use_cases:
            return
        col = self._collection(_COL_USE_CASES)
        col.upsert(
            documents=[_chunk_use_case(uc) for uc in use_cases],
            metadatas=[
                {
                    "name": uc.name,
                    "entities_involved": ", ".join(uc.entities_involved),
                }
                for uc in use_cases
            ],
            ids=[f"usecase_{uc.name[:40]}" for uc in use_cases],
        )

    def _index_api_endpoints(self, endpoints: List[APIEndpoint]) -> None:
        if not endpoints:
            return
        col = self._collection(_COL_ENDPOINTS)
        col.upsert(
            documents=[_chunk_endpoint(ep) for ep in endpoints],
            metadatas=[
                {
                    "method": ep.method,
                    "path": ep.path,
                    "business_operation": ep.business_operation,
                }
                for ep in endpoints
            ],
            ids=[
                f"ep_{i}_{ep.method}_{ep.path.replace('/', '_')[:30]}"
                for i, ep in enumerate(endpoints)
            ],
        )

    def _index_bounded_contexts(self, contexts: List[BoundedContext]) -> None:
        if not contexts:
            return
        col = self._collection(_COL_CONTEXTS)
        col.upsert(
            documents=[
                (
                    f"Bounded Context: {ctx.name}\n"
                    f"Purpose: {ctx.purpose}\n"
                    f"Entities: {', '.join(ctx.entities)}\n"
                    f"Dependencies: {', '.join(ctx.dependencies)}"
                )
                for ctx in contexts
            ],
            metadatas=[{"name": ctx.name} for ctx in contexts],
            ids=[f"ctx_{ctx.name[:40]}" for ctx in contexts],
        )

    # ── Low-level query ───────────────────────────────────────────────────────

    def _query(
        self,
        collection_name: str,
        query: str,
        n: Optional[int] = None,
        exclude_ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Query a ChromaDB collection, returning matching document texts."""
        n = n or self.top_k
        try:
            col = self._collection(collection_name)
            count = col.count()
            if count == 0:
                return []
            results = col.query(
                query_texts=[query],
                n_results=min(n, count),
            )
            docs: List[str] = results.get("documents", [[]])[0]
            ids: List[str] = results.get("ids", [[]])[0]
            if exclude_ids:
                docs = [d for d, i in zip(docs, ids) if i not in exclude_ids]
            return docs
        except Exception as exc:
            logger.warning("RAG query failed for '%s': %s", collection_name, exc)
            return []


# ── Chunking helpers (module-level pure functions) ────────────────────────────


def _chunk_entity(entity: DomainEntity) -> str:
    parts = [
        f"Domain Entity: {entity.name}",
        f"Type: {entity.type.value}",
    ]
    if entity.properties:
        props = ", ".join(
            f"{p.get('name', '')}: {p.get('type', '')}" for p in entity.properties
        )
        parts.append(f"Properties: {props}")
    if entity.business_rules:
        parts.append(f"Business Rules: {'; '.join(entity.business_rules)}")
    if entity.relationships:
        rels = ", ".join(
            f"{r.get('target', '')} ({r.get('type', '')})" for r in entity.relationships
        )
        parts.append(f"Relationships: {rels}")
    if entity.validation_rules:
        parts.append(f"Validations: {'; '.join(entity.validation_rules)}")
    if entity.lifecycle:
        parts.append(f"Lifecycle: {entity.lifecycle}")
    return "\n".join(parts)


def _chunk_rule(rule: BusinessRule) -> str:
    parts = [
        f"Business Rule: {rule.name}",
        f"Description: {rule.description}",
        f"Source: {rule.source_method}",
    ]
    if rule.conditions:
        parts.append(f"Conditions: {'; '.join(rule.conditions)}")
    if rule.actions:
        parts.append(f"Actions: {'; '.join(rule.actions)}")
    if rule.exceptions:
        parts.append(f"Exceptions: {'; '.join(rule.exceptions)}")
    return "\n".join(parts)


def _chunk_use_case(uc: UseCase) -> str:
    parts = [f"Use Case: {uc.name}", f"Description: {uc.description}"]
    if uc.actors:
        parts.append(f"Actors: {', '.join(uc.actors)}")
    if uc.entities_involved:
        parts.append(f"Entities: {', '.join(uc.entities_involved)}")
    if uc.steps:
        steps = "\n".join(f"  {i + 1}. {s}" for i, s in enumerate(uc.steps))
        parts.append(f"Steps:\n{steps}")
    if uc.preconditions:
        parts.append(f"Preconditions: {'; '.join(uc.preconditions)}")
    if uc.postconditions:
        parts.append(f"Postconditions: {'; '.join(uc.postconditions)}")
    if uc.error_scenarios:
        parts.append(f"Error Scenarios: {'; '.join(uc.error_scenarios)}")
    return "\n".join(parts)


def _chunk_endpoint(ep: APIEndpoint) -> str:
    parts = [
        f"API Endpoint: {ep.method} {ep.path}",
        f"Description: {ep.description}",
        f"Business Operation: {ep.business_operation}",
    ]
    if ep.path_parameters:
        params = ", ".join(
            f"{p.get('name', '')}: {p.get('type', '')}" for p in ep.path_parameters
        )
        parts.append(f"Path Params: {params}")
    if ep.query_parameters:
        params = ", ".join(
            f"{p.get('name', '')}: {p.get('type', '')}" for p in ep.query_parameters
        )
        parts.append(f"Query Params: {params}")
    if ep.validation_rules:
        parts.append(f"Validation: {'; '.join(ep.validation_rules)}")
    if ep.business_logic_summary:
        parts.append(f"Business Logic: {ep.business_logic_summary}")
    if ep.error_scenarios:
        errors = ", ".join(
            f"{e.get('status', '')} {e.get('description', '')}"
            for e in ep.error_scenarios
        )
        parts.append(f"Error Scenarios: {errors}")
    return "\n".join(parts)


# ── Formatting helpers ────────────────────────────────────────────────────────


def _join(docs: List[str]) -> str:
    return "\n---\n".join(docs)


def _format_context(sections: List[str]) -> str:
    if not sections:
        return ""
    header = "=== RAG Context: Retrieved Domain Knowledge ==="
    footer = "=== End of RAG Context ==="
    body = "\n\n".join(sections)
    return f"\n{header}\n\n{body}\n\n{footer}\n"
