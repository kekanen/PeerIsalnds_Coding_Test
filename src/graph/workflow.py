"""
LangGraph workflow definition for Java-to-Node.js conversion.

This module defines the complete workflow graph that orchestrates
all conversion steps from Java analysis to Node.js code generation.
"""

from langgraph.graph import StateGraph, END
from src.graph.state import ConversionState
from src.graph import nodes


def create_conversion_workflow() -> StateGraph:
    """
    Create and configure the LangGraph workflow for Java-to-Node.js conversion.

    The workflow follows these steps:
    1. Scan codebase (parse Java files)
    2. Categorize classes (Controller, Service, Entity, etc.)
    3. Analyze dependencies (build dependency graph)
    4. Extract domain knowledge (using LLM)
    5. Design architecture (determine target structure)
    6. Generate domain layer (entities, value objects, repositories)
    7. Generate application layer (use cases, DTOs, services)
    8. Generate infrastructure layer (database, external services)
    9. Generate presentation layer (controllers, routes, API specs)
    10. Generate config files (package.json, tsconfig, etc.)
    11. Write outputs (write all files to disk)

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the state graph
    workflow = StateGraph(ConversionState)

    # ============================================================
    # Add all nodes to the graph
    # ============================================================

    # Phase 1: Repository & Scanning
    workflow.add_node("scan_codebase", nodes.scan_codebase)
    workflow.add_node("categorize_classes", nodes.categorize_classes)
    workflow.add_node("analyze_dependencies", nodes.analyze_dependencies)

    # Phase 2: Knowledge Extraction (LLM)
    workflow.add_node("extract_domain_knowledge", nodes.extract_domain_knowledge)

    # Phase 3: Architecture Design
    workflow.add_node("design_architecture", nodes.design_architecture)

    # Phase 4: Code Generation
    workflow.add_node("generate_domain_layer", nodes.generate_domain_layer)
    workflow.add_node("generate_application_layer", nodes.generate_application_layer)
    workflow.add_node("generate_infrastructure_layer", nodes.generate_infrastructure_layer)
    workflow.add_node("generate_presentation_layer", nodes.generate_presentation_layer)
    workflow.add_node("generate_config_files", nodes.generate_config_files)

    # Phase 5: Output
    workflow.add_node("write_outputs", nodes.write_outputs)

    # ============================================================
    # Define the workflow edges (execution order)
    # ============================================================

    # Set entry point
    workflow.set_entry_point("scan_codebase")

    # Phase 1: Scanning & Analysis
    workflow.add_edge("scan_codebase", "categorize_classes")
    workflow.add_edge("categorize_classes", "analyze_dependencies")

    # Phase 2: Domain Knowledge Extraction
    workflow.add_edge("analyze_dependencies", "extract_domain_knowledge")

    # Phase 3: Architecture Design
    workflow.add_edge("extract_domain_knowledge", "design_architecture")

    # Phase 4: Code Generation (sequential)
    workflow.add_edge("design_architecture", "generate_domain_layer")
    workflow.add_edge("generate_domain_layer", "generate_application_layer")
    workflow.add_edge("generate_application_layer", "generate_infrastructure_layer")
    workflow.add_edge("generate_infrastructure_layer", "generate_presentation_layer")
    workflow.add_edge("generate_presentation_layer", "generate_config_files")

    # Phase 5: Write outputs and finish
    workflow.add_edge("generate_config_files", "write_outputs")
    workflow.add_edge("write_outputs", END)

    # ============================================================
    # Compile and return the graph
    # ============================================================

    return workflow.compile()


def create_workflow_with_checkpoints(checkpoint_dir: str = "./.checkpoints") -> StateGraph:
    """
    Create a workflow with checkpointing enabled for resumability.

    Args:
        checkpoint_dir: Directory to store checkpoint files

    Returns:
        Compiled StateGraph with checkpointing enabled
    """
    from langgraph.checkpoint.sqlite import SqliteSaver
    from pathlib import Path

    # Create checkpoint directory
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

    # Create checkpoint saver
    checkpointer = SqliteSaver.from_conn_string(f"{checkpoint_dir}/checkpoints.db")

    # Create workflow
    workflow = StateGraph(ConversionState)

    # Add all nodes (same as above)
    workflow.add_node("scan_codebase", nodes.scan_codebase)
    workflow.add_node("categorize_classes", nodes.categorize_classes)
    workflow.add_node("analyze_dependencies", nodes.analyze_dependencies)
    workflow.add_node("extract_domain_knowledge", nodes.extract_domain_knowledge)
    workflow.add_node("design_architecture", nodes.design_architecture)
    workflow.add_node("generate_domain_layer", nodes.generate_domain_layer)
    workflow.add_node("generate_application_layer", nodes.generate_application_layer)
    workflow.add_node("generate_infrastructure_layer", nodes.generate_infrastructure_layer)
    workflow.add_node("generate_presentation_layer", nodes.generate_presentation_layer)
    workflow.add_node("generate_config_files", nodes.generate_config_files)
    workflow.add_node("write_outputs", nodes.write_outputs)

    # Add edges (same as above)
    workflow.set_entry_point("scan_codebase")
    workflow.add_edge("scan_codebase", "categorize_classes")
    workflow.add_edge("categorize_classes", "analyze_dependencies")
    workflow.add_edge("analyze_dependencies", "extract_domain_knowledge")
    workflow.add_edge("extract_domain_knowledge", "design_architecture")
    workflow.add_edge("design_architecture", "generate_domain_layer")
    workflow.add_edge("generate_domain_layer", "generate_application_layer")
    workflow.add_edge("generate_application_layer", "generate_infrastructure_layer")
    workflow.add_edge("generate_infrastructure_layer", "generate_presentation_layer")
    workflow.add_edge("generate_presentation_layer", "generate_config_files")
    workflow.add_edge("generate_config_files", "write_outputs")
    workflow.add_edge("write_outputs", END)

    # Compile with checkpointing
    return workflow.compile(checkpointer=checkpointer)


# Create default workflow instance
conversion_workflow = create_conversion_workflow()

__all__ = [
    "create_conversion_workflow",
    "create_workflow_with_checkpoints",
    "conversion_workflow",
]
