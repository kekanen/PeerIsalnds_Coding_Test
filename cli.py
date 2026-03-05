#!/usr/bin/env python3
"""
SAKILA AI AGENT CLI

Command-line interface for converting Java/Spring applications to Node.js/TypeScript
using LLM-based code generation.
"""

import click
from pathlib import Path
import sys
import os
import tempfile
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time
import git

# Add src to Python path - must be absolute path
cli_dir = Path(__file__).parent.resolve()
src_dir = cli_dir / "src"
sys.path.insert(0, str(cli_dir))
sys.path.insert(0, str(src_dir.parent))

from src.graph.workflow import create_conversion_workflow
from src.graph.state import ConversionState
from src.config.settings import Settings
from src.analyzers.code_scanner import CodeScanner
from src.analyzers.class_categorizer import ClassCategorizer
from src.analyzers.dependency_mapper import DependencyMapper
from src.llm.llm_domain_extractor import DomainExtractor

console = Console()


def is_git_url(path: str) -> bool:
    """Check if the path is a Git URL."""
    git_patterns = [
        path.startswith('http://'),
        path.startswith('https://'),
        path.startswith('git@'),
        path.startswith('ssh://'),
        path.endswith('.git')
    ]
    return any(git_patterns)


def clone_repository(git_url: str, branch: str = None) -> Path:
    """
    Clone a Git repository to a temporary directory.

    Args:
        git_url: Git repository URL
        branch: Optional branch name

    Returns:
        Path to the cloned repository
    """
    temp_dir = Path(tempfile.mkdtemp(prefix='peermod_'))

    console.print(f"[cyan]Cloning repository: {git_url}[/cyan]")

    try:
        if branch:
            console.print(f"[cyan]Branch: {branch}[/cyan]")
            git.Repo.clone_from(git_url, temp_dir, branch=branch)
        else:
            git.Repo.clone_from(git_url, temp_dir)

        console.print(f"[green]✓ Repository cloned to: {temp_dir}[/green]")
        console.print()
        return temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        console.print(f"[red]✗ Failed to clone repository: {e}[/red]")
        sys.exit(1)


@click.group()
@click.version_option(version="1.0.0", prog_name="SAKILA AI AGENT")
def cli():
    """
    SAKILA AI AGENT

    Convert Java/Spring applications to modern Node.js/TypeScript
    using AI-powered code generation.
    """
    pass


@cli.command()
@click.argument('java_repo_path')
@click.option(
    '--output',
    '-o',
    default='./output',
    help='Output directory for generated code',
    type=click.Path()
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output'
)
@click.option(
    '--branch',
    '-b',
    default=None,
    help='Git branch to analyze (for Git URLs)'
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    help='Skip confirmation prompt'
)
def convert(java_repo_path: str, output: str, verbose: bool, branch: str, yes: bool):
    """
    Convert a Java/Spring application to Node.js/TypeScript.

    JAVA_REPO_PATH: Path to the Java repository OR Git URL

    Examples:
        cli.py convert /path/to/spring-petclinic --output ./my-output -v
        cli.py convert https://github.com/spring-projects/spring-petclinic -v
        cli.py convert git@github.com:user/repo.git --branch develop
    """
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SAKILA AI AGENT[/bold cyan]\n"
        "AI-Powered Java -> Node.js Conversion",
        border_style="cyan"
    ))
    console.print()

    # Handle Git URLs
    is_git = is_git_url(java_repo_path)
    temp_clone = None

    if is_git:
        # Clone repository
        java_path = clone_repository(java_repo_path, branch)
        temp_clone = java_path
    else:
        # Use local path
        java_path = Path(java_repo_path).resolve()
        if not java_path.exists():
            console.print(f"[red]✗ Error: Java repository path does not exist: {java_path}[/red]")
            sys.exit(1)

    output_path = Path(output).resolve()

    # Display configuration
    config_table = Table(show_header=False, box=None)
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="white")

    config_table.add_row("📂 Java Repository", str(java_path))
    config_table.add_row("📤 Output Directory", str(output_path))
    if branch:
        config_table.add_row("🌿 Git Branch", branch)
    config_table.add_row("🔊 Verbose Mode", "Enabled" if verbose else "Disabled")

    console.print(config_table)
    console.print()

    # Confirm execution
    if not yes and not click.confirm("Start conversion?", default=True):
        console.print("[yellow]Conversion cancelled.[/yellow]")
        sys.exit(0)

    console.print()
    console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
    console.print()

    try:
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Initialize state
        start_time = time.time()

        initial_state: ConversionState = {
            "repo_path": str(java_path),
            "branch": branch,
            "output_directory": str(output_path),
            "java_files": [],
            "java_classes": [],
            "domain_knowledge": None,
            "architecture": None,
            "generated_files": {},
            "current_step": "initialized",
            "errors": [],
            "start_time": start_time,
            "verbose": verbose,
        }

        # Create and run workflow
        workflow = create_conversion_workflow()

        console.print("[bold green]Running conversion workflow...[/bold green]")
        console.print()

        # Execute workflow
        result = workflow.invoke(initial_state)

        # Calculate duration
        end_time = time.time()
        duration = end_time - start_time

        console.print()
        console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
        console.print()

        # Display results
        if result.get("errors"):
            console.print("[yellow]⚠️  Conversion completed with warnings:[/yellow]")
            console.print()
            for error in result["errors"]:
                console.print(f"  [yellow]• {error.get('step', 'unknown')}: {error.get('error', 'unknown error')}[/yellow]")
            console.print()

        # Summary statistics
        stats_table = Table(title="[bold green]✅ Conversion Summary[/bold green]", show_header=True)
        stats_table.add_column("Metric", style="cyan", no_wrap=True)
        stats_table.add_column("Value", style="white", justify="right")

        stats_table.add_row("Java Classes Parsed", str(len(result.get("java_classes", []))))

        if result.get("domain_knowledge"):
            dk = result["domain_knowledge"]
            stats_table.add_row("Bounded Contexts", str(len(dk.bounded_contexts)))
            stats_table.add_row("Domain Entities", str(len(dk.entities)))
            stats_table.add_row("Use Cases", str(len(dk.use_cases)))
            stats_table.add_row("Business Rules", str(len(dk.business_rules)))
            stats_table.add_row("API Endpoints", str(len(dk.api_contracts)))

        stats_table.add_row("Generated Files", str(len(result.get("generated_files", {}))))
        stats_table.add_row("Execution Time", f"{duration:.2f} seconds")

        console.print(stats_table)
        console.print()

        console.print(f"[bold green]✓ Output written to:[/bold green] {output_path}")
        console.print()

        # Next steps
        console.print("[bold cyan]Next Steps:[/bold cyan]")
        console.print("  1. Review generated code in the output directory")
        console.print("  2. Check domain_knowledge.json for extracted business rules")
        console.print("  3. Install dependencies: cd output && npm install")
        console.print("  4. Configure database connection in generated config files")
        console.print("  5. Run tests and start development server")
        console.print()

    except Exception as e:
        console.print()
        console.print(f"[bold red]✗ Conversion failed:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")

        if verbose:
            console.print()
            console.print("[yellow]Stack trace:[/yellow]")
            import traceback
            console.print(traceback.format_exc())

        sys.exit(1)

    finally:
        # Cleanup temporary clone if it was created
        if temp_clone:
            console.print(f"[dim]Cleaning up temporary clone: {temp_clone}[/dim]")
            shutil.rmtree(temp_clone, ignore_errors=True)


@cli.command()
@click.argument('java_repo_path')
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Show detailed analysis'
)
@click.option(
    '--branch',
    '-b',
    default=None,
    help='Git branch to analyze (for Git URLs)'
)
def analyze(java_repo_path: str, verbose: bool, branch: str):
    """
    Analyze a Java repository without generating code.

    This performs domain knowledge extraction and displays insights
    about the codebase structure, entities, and business rules.

    Examples:
        cli.py analyze /path/to/spring-petclinic -v
        cli.py analyze https://github.com/spring-projects/spring-petclinic -v
    """
    console.print()
    console.print("[bold cyan]Analyzing Java Repository...[/bold cyan]")
    console.print()

    # Handle Git URLs
    is_git = is_git_url(java_repo_path)
    temp_clone = None

    if is_git:
        # Clone repository
        java_path = clone_repository(java_repo_path, branch)
        temp_clone = java_path
    else:
        # Use local path
        java_path = Path(java_repo_path).resolve()
        if not java_path.exists():
            console.print(f"[red]✗ Error: Path does not exist: {java_path}[/red]")
            sys.exit(1)

    console.print(f"📂 Repository: {java_path}")
    console.print()

    try:
        # Scan Java files
        with console.status("[cyan]Scanning Java files..."):
            scanner = CodeScanner(str(java_path))
            java_classes = scanner.scan_repository(verbose=False)

        console.print(f"[green]✓ Found {len(java_classes)} Java classes[/green]")
        console.print()

        # Categorize classes
        with console.status("[cyan]Categorizing classes..."):
            categorizer = ClassCategorizer()
            categories = {}
            for java_class in java_classes:
                category = categorizer.categorize(java_class)
                if category not in categories:
                    categories[category] = []
                categories[category].append(java_class)

        # Display categories
        cat_table = Table(title="Class Categories", show_header=True)
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count", justify="right", style="white")

        for category, classes in sorted(categories.items()):
            cat_table.add_row(category, str(len(classes)))

        console.print(cat_table)
        console.print()

        # Analyze dependencies
        with console.status("[cyan]Analyzing dependencies..."):
            mapper = DependencyMapper(java_classes)
            dep_graph = mapper.map_dependencies()

        console.print(f"[green]✓ Found {len(dep_graph.dependencies)} dependencies[/green]")
        console.print()

        # Extract domain knowledge
        if click.confirm("🤖 Extract domain knowledge using LLM?", default=True):
            console.print()
            settings = Settings()
            extractor = DomainExtractor(settings)
            domain_knowledge = extractor.extract_domain_knowledge(
                java_classes=java_classes,
                verbose=verbose
            )

            console.print()

            # Display domain knowledge
            dk_table = Table(title="[bold green]Domain Knowledge[/bold green]", show_header=True)
            dk_table.add_column("Aspect", style="cyan")
            dk_table.add_column("Count", justify="right", style="white")

            dk_table.add_row("Bounded Contexts", str(len(domain_knowledge.bounded_contexts)))
            dk_table.add_row("Domain Entities", str(len(domain_knowledge.entities)))
            dk_table.add_row("Use Cases", str(len(domain_knowledge.use_cases)))
            dk_table.add_row("Business Rules", str(len(domain_knowledge.business_rules)))
            dk_table.add_row("API Endpoints", str(len(domain_knowledge.api_contracts)))

            console.print(dk_table)
            console.print()

            if verbose:
                # Show entities
                console.print("[bold cyan]Entities:[/bold cyan]")
                for entity in domain_knowledge.entities:
                    console.print(f"  • {entity.name} ({entity.type})")
                console.print()

                # Show use cases
                console.print("[bold cyan]Use Cases:[/bold cyan]")
                for uc in domain_knowledge.use_cases[:5]:  # Show first 5
                    console.print(f"  • {uc.name}")
                if len(domain_knowledge.use_cases) > 5:
                    console.print(f"  ... and {len(domain_knowledge.use_cases) - 5} more")
                console.print()

        console.print("[bold green]✓ Analysis complete![/bold green]")
        console.print()

    except Exception as e:
        console.print(f"[bold red]✗ Analysis failed:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")

        if verbose:
            import traceback
            console.print()
            console.print(traceback.format_exc())

        sys.exit(1)

    finally:
        # Cleanup temporary clone if it was created
        if temp_clone:
            console.print(f"[dim]Cleaning up temporary clone: {temp_clone}[/dim]")
            shutil.rmtree(temp_clone, ignore_errors=True)


@cli.command()
def config():
    """
    Display current configuration settings.

    Shows LLM provider, API keys (masked), and other settings.
    """
    console.print()
    console.print("[bold cyan]Configuration Settings[/bold cyan]")
    console.print()

    try:
        settings = Settings()

        config_table = Table(show_header=True)
        config_table.add_column("Setting", style="cyan", no_wrap=True)
        config_table.add_column("Value", style="white")
        config_table.add_column("Status", style="green")

        # LLM Provider
        config_table.add_row(
            "LLM Provider",
            settings.llm_provider,
            "✓" if settings.llm_provider else "✗"
        )

        # API Key (masked)
        api_key = settings.azure_openai_api_key or settings.openai_api_key
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            config_table.add_row("API Key", masked_key, "✓")
        else:
            config_table.add_row("API Key", "Not set", "✗")

        # Azure settings
        if settings.llm_provider == "azure":
            config_table.add_row("Azure Endpoint", settings.azure_openai_endpoint or "Not set",
                               "✓" if settings.azure_openai_endpoint else "✗")
            config_table.add_row("Deployment Name", settings.azure_openai_deployment_name or "Not set",
                               "✓" if settings.azure_openai_deployment_name else "✗")
            config_table.add_row("API Version", settings.azure_openai_api_version, "✓")

        # Model settings
        config_table.add_row("Model Name", settings.model_name, "✓")
        config_table.add_row("Temperature", str(settings.temperature), "✓")
        config_table.add_row("Max Tokens", str(settings.max_tokens), "✓")

        console.print(config_table)
        console.print()

        # Environment file check
        env_file = Path(".env")
        if env_file.exists():
            console.print(f"[green]✓ Environment file found:[/green] {env_file.absolute()}")
        else:
            console.print(f"[yellow]⚠️  No .env file found. Using environment variables or defaults.[/yellow]")

        console.print()

    except Exception as e:
        console.print(f"[red]✗ Error loading configuration:[/red]")
        console.print(f"[red]{str(e)}[/red]")
        sys.exit(1)


@cli.command()
def examples():
    """
    Show example usage commands.
    """
    console.print()
    console.print("[bold cyan]Example Commands[/bold cyan]")
    console.print()

    examples_text = """
[bold]1. Convert a Java repository (local path):[/bold]
   [cyan]uv run python cli.py convert /path/to/spring-petclinic[/cyan]

[bold]2. Convert from Git URL:[/bold]
   [cyan]uv run python cli.py convert https://github.com/spring-projects/spring-petclinic[/cyan]

[bold]3. Convert from Git URL with specific branch:[/bold]
   [cyan]uv run python cli.py convert https://github.com/user/repo.git --branch develop[/cyan]

[bold]4. Convert with custom output directory:[/bold]
   [cyan]uv run python cli.py convert /path/to/java-app --output ./my-nodejs-app[/cyan]

[bold]5. Convert with verbose output:[/bold]
   [cyan]uv run python cli.py convert /path/to/java-app -v[/cyan]

[bold]6. Analyze repository from Git URL:[/bold]
   [cyan]uv run python cli.py analyze https://github.com/user/repo -v[/cyan]

[bold]7. Analyze local repository:[/bold]
   [cyan]uv run python cli.py analyze /path/to/java-app -v[/cyan]

[bold]8. Check configuration:[/bold]
   [cyan]uv run python cli.py config[/cyan]

[bold]9. Show help for a command:[/bold]
   [cyan]uv run python cli.py convert --help[/cyan]
"""

    console.print(examples_text)
    console.print()


if __name__ == "__main__":
    cli()
