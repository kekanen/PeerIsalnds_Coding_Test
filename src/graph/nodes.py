"""
LangGraph workflow nodes for Java-to-Node.js conversion.

Each node is a function that takes the state, performs an operation,
and returns an updated state.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from rich.console import Console

from src.graph.state import ConversionState
from src.analyzers.project_analyzer import ProjectAnalyzer
from src.analyzers.class_categorizer import ClassCategorizer
from src.analyzers.dependency_mapper import DependencyMapper
from src.llm.llm_domain_extractor import DomainExtractor
from src.config.settings import Settings

# Initialize logger and console
logger = logging.getLogger(__name__)
console = Console()


# ============================================================
# PHASE 1: Repository & Scanning Nodes
# ============================================================


def scan_codebase(state: ConversionState) -> ConversionState:
    """
    Scan the Java codebase and parse all Java files.

    Updates state with:
    - java_files: List of found Java file paths
    - java_classes: Parsed JavaClass objects
    - total_files, parsed_files, parse_errors
    """
    state["current_step"] = "scan_codebase"

    try:
        repo_path = state["repo_path"]
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Scanning codebase:[/bold cyan] {repo_path}\n")

        # Use ProjectAnalyzer to scan and parse
        analyzer = ProjectAnalyzer(repo_path)
        analysis = analyzer.analyze(verbose=verbose)

        # Update state with results
        state["java_classes"] = analysis.java_classes
        state["total_files"] = len(analysis.java_classes)
        state["parsed_files"] = len(analysis.java_classes)

        if verbose:
            console.print(f"[green]✓ Successfully parsed {len(analysis.java_classes)} Java classes[/green]\n")

        return state

    except Exception as e:
        error_msg = f"Failed to scan codebase: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "scan_codebase",
            "error": error_msg,
            "exception": str(e)
        })
        return state


def categorize_classes(state: ConversionState) -> ConversionState:
    """
    Categorize Java classes by type (Controller, Service, Entity, etc.).

    Updates state with:
    - classes_by_category: Dict mapping category -> list of classes
    """
    state["current_step"] = "categorize_classes"

    try:
        java_classes = state.get("java_classes", [])
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Categorizing classes...[/bold cyan]\n")

        # Use ClassCategorizer to categorize each class
        categorizer = ClassCategorizer()
        categories = {}

        for java_class in java_classes:
            category = categorizer.categorize(java_class)
            if category not in categories:
                categories[category] = []
            categories[category].append(java_class)

        state["classes_by_category"] = categories

        if verbose:
            console.print("[green]✓ Classes categorized:[/green]")
            for category, classes in categories.items():
                console.print(f"  • {category}: {len(classes)} classes")
            console.print()

        return state

    except Exception as e:
        error_msg = f"Failed to categorize classes: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "categorize_classes",
            "error": error_msg,
            "exception": str(e)
        })
        return state


def analyze_dependencies(state: ConversionState) -> ConversionState:
    """
    Analyze dependencies between Java classes.

    Updates state with:
    - dependency_graph: Dict mapping class -> list of dependencies
    - circular_dependencies: List of circular dependency chains
    """
    state["current_step"] = "analyze_dependencies"

    try:
        java_classes = state.get("java_classes", [])
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Analyzing dependencies...[/bold cyan]\n")

        # Use DependencyMapper
        mapper = DependencyMapper(java_classes)
        dependency_graph_obj = mapper.map_dependencies()

        # Convert DependencyGraph to simple dict for state
        dependency_graph = {}
        for dep in dependency_graph_obj.dependencies:
            if dep.from_class not in dependency_graph:
                dependency_graph[dep.from_class] = []
            dependency_graph[dep.from_class].append(dep.to_class)

        # TODO: Implement circular dependency detection
        circular_deps = []

        state["dependency_graph"] = dependency_graph
        state["circular_dependencies"] = circular_deps

        if verbose:
            total_deps = sum(len(deps) for deps in dependency_graph.values())
            console.print(f"[green]✓ Found {total_deps} dependencies[/green]")
            if circular_deps:
                console.print(f"[yellow]⚠ Found {len(circular_deps)} circular dependencies[/yellow]")
            console.print()

        return state

    except Exception as e:
        error_msg = f"Failed to analyze dependencies: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "analyze_dependencies",
            "error": error_msg,
            "exception": str(e)
        })
        return state


# ============================================================
# PHASE 2: Knowledge Extraction Nodes (LLM-powered)
# ============================================================


def extract_domain_knowledge(state: ConversionState) -> ConversionState:
    """
    Extract domain knowledge from Java classes using LLM.

    Updates state with:
    - domain_knowledge: Complete DomainKnowledge object
    """
    state["current_step"] = "extract_domain_knowledge"

    try:
        java_classes = state.get("java_classes", [])
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Extracting domain knowledge with LLM...[/bold cyan]\n")

        # Load settings and create domain extractor
        settings = Settings()
        extractor = DomainExtractor(settings)

        # Extract domain knowledge
        domain_knowledge = extractor.extract_domain_knowledge(
            java_classes=java_classes,
            verbose=verbose
        )

        state["domain_knowledge"] = domain_knowledge

        if verbose:
            console.print(f"[green]✓ Extracted domain knowledge:[/green]")
            console.print(f"  • Bounded Contexts: {len(domain_knowledge.bounded_contexts)}")
            console.print(f"  • Domain Entities: {len(domain_knowledge.entities)}")
            console.print(f"  • Use Cases: {len(domain_knowledge.use_cases)}")
            console.print(f"  • Business Rules: {len(domain_knowledge.business_rules)}")
            console.print(f"  • API Endpoints: {len(domain_knowledge.api_contracts)}")
            console.print()

        return state

    except Exception as e:
        error_msg = f"Failed to extract domain knowledge: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "extract_domain_knowledge",
            "error": error_msg,
            "exception": str(e)
        })
        return state


# ============================================================
# PHASE 3: Architecture Design Nodes
# ============================================================


def design_architecture(state: ConversionState) -> ConversionState:
    """
    Design the target Node.js architecture based on domain knowledge.

    Updates state with:
    - architecture: ModernArchitecture object
    """
    state["current_step"] = "design_architecture"

    try:
        domain_knowledge = state.get("domain_knowledge")
        target_framework = state.get("target_framework", "express")
        target_orm = state.get("target_orm", "typeorm")
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Designing architecture...[/bold cyan]\n")

        if not domain_knowledge:
            raise ValueError("Domain knowledge not found in state")

        # TODO: Implement architecture design logic
        # For now, create a placeholder
        from src.models.architecture_models import (
            ModernArchitecture,
            ArchitecturePattern,
            TechStack,
            ModuleStructure,
            LayerDefinition
        )

        # Create architecture based on domain knowledge
        architecture = ModernArchitecture(
            pattern=ArchitecturePattern.CLEAN_ARCHITECTURE,
            rationale=f"Clean Architecture chosen for {len(domain_knowledge.bounded_contexts)} bounded contexts with clear separation of concerns",
            tech_stack=TechStack(
                runtime="Node.js",
                language="TypeScript",
                framework=target_framework,
                orm=target_orm,
                testing_framework="jest",
                validation_library="class-validator",
                di_container="tsyringe" if target_framework == "express" else "built-in"
            ),
            layers=[
                LayerDefinition(
                    name="domain",
                    purpose="Core business logic and entities",
                    dependencies=[]
                ),
                LayerDefinition(
                    name="application",
                    purpose="Use cases and application services",
                    dependencies=["domain"]
                ),
                LayerDefinition(
                    name="infrastructure",
                    purpose="External services, database, etc.",
                    dependencies=["domain"]
                ),
                LayerDefinition(
                    name="presentation",
                    purpose="API controllers and routes",
                    dependencies=["application", "domain"]
                )
            ],
            modules=[],  # Will be populated based on bounded contexts
            folder_structure={}  # Will be populated
        )

        state["architecture"] = architecture

        if verbose:
            console.print(f"[green]✓ Architecture designed:[/green]")
            console.print(f"  • Pattern: {architecture.pattern.value}")
            console.print(f"  • Framework: {architecture.tech_stack.framework}")
            console.print(f"  • ORM: {architecture.tech_stack.orm}")
            console.print(f"  • Layers: {len(architecture.layers)}")
            console.print()

        return state

    except Exception as e:
        error_msg = f"Failed to design architecture: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "design_architecture",
            "error": error_msg,
            "exception": str(e)
        })
        return state


# ============================================================
# PHASE 4: Code Generation Nodes
# ============================================================


def generate_domain_layer(state: ConversionState) -> ConversionState:
    """
    Generate domain layer code using LLM (entities, repositories).

    Updates state with:
    - generated_files: Adds domain layer files
    """
    state["current_step"] = "generate_domain_layer"

    try:
        domain_knowledge = state.get("domain_knowledge")
        architecture = state.get("architecture")
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Generating domain layer with LLM...[/bold cyan]\n")

        if not domain_knowledge or not architecture:
            raise ValueError("Domain knowledge or architecture not found in state")

        # Initialize LLM code generator
        from src.generators.llm_code_creator import LLMCodeGenerator
        generator = LLMCodeGenerator()

        generated_files = state.get("generated_files", {})

        # Generate code for each entity using LLM
        for entity in domain_knowledge.entities:
            if verbose:
                console.print(f"  [cyan]→ Generating {entity.name}...[/cyan]")

            # Generate all files for this entity
            entity_files = generator.generate_all_for_entity(
                entity=entity,
                domain_knowledge=domain_knowledge,
                verbose=False,  # We're already showing progress
            )

            # Add to generated files
            generated_files.update(entity_files)

            if verbose:
                console.print(f"  [green]✓ Generated {len(entity_files)} files for {entity.name}[/green]")

        state["generated_files"] = generated_files

        if verbose:
            console.print(f"\n[green]✓ Generated domain layer: {len(generated_files)} files total[/green]\n")

        return state

    except Exception as e:
        error_msg = f"Failed to generate domain layer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "generate_domain_layer",
            "error": error_msg,
            "exception": str(e)
        })
        return state


def generate_application_layer(state: ConversionState) -> ConversionState:
    """
    Generate application layer code using LLM (use cases with business logic).

    Updates state with:
    - generated_files: Adds application layer files
    """
    state["current_step"] = "generate_application_layer"

    try:
        domain_knowledge = state.get("domain_knowledge")
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Generating application layer with LLM...[/bold cyan]\n")

        if not domain_knowledge:
            raise ValueError("Domain knowledge not found in state")

        # Initialize LLM code generator
        from src.generators.llm_code_creator import LLMCodeGenerator
        generator = LLMCodeGenerator()

        generated_files = state.get("generated_files", {})

        # Generate use cases with business logic
        for use_case in domain_knowledge.use_cases:
            if verbose:
                console.print(f"  [cyan]→ Generating use case: {use_case.name}...[/cyan]")

            try:
                use_case_code = generator.generate_use_case(
                    use_case=use_case,
                    domain_knowledge=domain_knowledge,
                )

                # Convert use case name to filename
                filename = use_case.name.lower().replace(' ', '-')
                file_path = f"src/application/use-cases/{filename}.use-case.ts"
                generated_files[file_path] = use_case_code

                if verbose:
                    console.print(f"  [green]✓ Generated {use_case.name}[/green]")

            except Exception as e:
                if verbose:
                    console.print(f"  [yellow]⚠ Skipped {use_case.name}: {str(e)}[/yellow]")
                logger.warning(f"Failed to generate use case {use_case.name}: {e}")

        state["generated_files"] = generated_files

        if verbose:
            console.print(f"\n[green]✓ Generated application layer: {len(domain_knowledge.use_cases)} use cases[/green]\n")

        return state

    except Exception as e:
        error_msg = f"Failed to generate application layer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "generate_application_layer",
            "error": error_msg,
            "exception": str(e)
        })
        return state


def generate_infrastructure_layer(state: ConversionState) -> ConversionState:
    """
    Generate infrastructure layer code (repository implementations, database config).

    Updates state with:
    - generated_files: Adds infrastructure layer files
    """
    state["current_step"] = "generate_infrastructure_layer"

    try:
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Generating infrastructure layer...[/bold cyan]\n")

        # TODO: Implement infrastructure layer generation

        if verbose:
            console.print(f"[green]✓ Generated infrastructure layer[/green]\n")

        return state

    except Exception as e:
        error_msg = f"Failed to generate infrastructure layer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "generate_infrastructure_layer",
            "error": error_msg,
            "exception": str(e)
        })
        return state


def generate_presentation_layer(state: ConversionState) -> ConversionState:
    """
    Generate presentation layer code using LLM (controllers with Express routing).

    Updates state with:
    - generated_files: Adds presentation layer files
    """
    state["current_step"] = "generate_presentation_layer"

    try:
        domain_knowledge = state.get("domain_knowledge")
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Generating presentation layer with LLM...[/bold cyan]\n")

        if not domain_knowledge:
            raise ValueError("Domain knowledge not found in state")

        # Initialize LLM code generator
        from src.generators.llm_code_creator import LLMCodeGenerator
        generator = LLMCodeGenerator()

        generated_files = state.get("generated_files", {})

        # Group API endpoints by resource/controller
        endpoints_by_resource = {}
        for endpoint in domain_knowledge.api_contracts:
            # Extract resource name from path (e.g., /owners -> owners)
            path_parts = endpoint.path.strip('/').split('/')
            resource = path_parts[0] if path_parts else 'root'

            # Handle special cases
            if not resource or resource == '':
                resource = 'welcome'  # Root path becomes welcome controller
            elif '.' in resource:
                # Handle paths like /vets.html -> extract base resource
                resource = resource.split('.')[0]

            if resource not in endpoints_by_resource:
                endpoints_by_resource[resource] = []
            endpoints_by_resource[resource].append(endpoint)

        # Generate controller for each resource
        for resource, endpoints in endpoints_by_resource.items():
            controller_name = f"{resource.capitalize()}Controller"

            if verbose:
                console.print(f"  [cyan]→ Generating {controller_name} ({len(endpoints)} endpoints)...[/cyan]")

            try:
                controller_code = generator.generate_controller(
                    endpoints=endpoints,
                    controller_name=controller_name,
                    domain_knowledge=domain_knowledge,
                )

                file_path = f"src/presentation/controllers/{resource}.controller.ts"
                generated_files[file_path] = controller_code

                if verbose:
                    console.print(f"  [green]✓ Generated {controller_name}[/green]")

            except Exception as e:
                if verbose:
                    console.print(f"  [yellow]⚠ Skipped {controller_name}: {str(e)}[/yellow]")
                logger.warning(f"Failed to generate controller {controller_name}: {e}")

        state["generated_files"] = generated_files

        if verbose:
            console.print(f"\n[green]✓ Generated presentation layer: {len(endpoints_by_resource)} controllers[/green]\n")

        return state

    except Exception as e:
        error_msg = f"Failed to generate presentation layer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "generate_presentation_layer",
            "error": error_msg,
            "exception": str(e)
        })
        return state


def generate_config_files(state: ConversionState) -> ConversionState:
    """
    Generate configuration files (package.json, tsconfig.json, etc.).

    Updates state with:
    - generated_files: Adds config files
    """
    state["current_step"] = "generate_config_files"

    try:
        architecture = state.get("architecture")
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Generating configuration files...[/bold cyan]\n")

        if not architecture:
            raise ValueError("Architecture not found in state")

        generated_files = state.get("generated_files", {})

        # TODO: Implement config file generation
        # For now, add placeholder package.json
        package_json = """{
  "name": "converted-nodejs-app",
  "version": "1.0.0",
  "description": "Auto-generated from Java codebase",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node-dev src/index.ts",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0",
    "typeorm": "^0.3.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "ts-node-dev": "^2.0.0",
    "jest": "^29.0.0"
  }
}
"""
        generated_files["package.json"] = package_json

        tsconfig_json = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
"""
        generated_files["tsconfig.json"] = tsconfig_json

        state["generated_files"] = generated_files

        if verbose:
            console.print(f"[green]✓ Generated configuration files[/green]\n")

        return state

    except Exception as e:
        error_msg = f"Failed to generate config files: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "generate_config_files",
            "error": error_msg,
            "exception": str(e)
        })
        return state


# ============================================================
# PHASE 5: Output & Finalization Nodes
# ============================================================


def write_outputs(state: ConversionState) -> ConversionState:
    """
    Write all generated files to disk.

    Creates the output directory structure and writes all files.
    Also exports domain knowledge to JSON.
    """
    state["current_step"] = "write_outputs"

    try:
        output_dir = state.get("output_directory", "./output")
        generated_files = state.get("generated_files", {})
        domain_knowledge = state.get("domain_knowledge")
        verbose = state.get("verbose", False)

        if verbose:
            console.print(f"\n[bold cyan]Writing generated files to {output_dir}...[/bold cyan]\n")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Write each file
        for file_path, content in generated_files.items():
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            if verbose:
                console.print(f"  ✓ {file_path}")

        # Export domain knowledge to JSON
        if domain_knowledge:
            import json
            domain_json_path = output_path / "domain_knowledge.json"
            with open(domain_json_path, "w", encoding="utf-8") as f:
                json.dump(domain_knowledge.model_dump(), f, indent=2)

            if verbose:
                console.print(f"  ✓ domain_knowledge.json")

        if verbose:
            total_files = len(generated_files) + (1 if domain_knowledge else 0)
            console.print(f"\n[green]✓ Wrote {total_files} files to {output_dir}[/green]\n")

        # Update end time
        import time
        state["end_time"] = time.time()

        return state

    except Exception as e:
        error_msg = f"Failed to write outputs: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"].append({
            "step": "write_outputs",
            "error": error_msg,
            "exception": str(e)
        })
        return state
