"""
Tests for code analysis components.
"""

import pytest
from pathlib import Path

from src.analyzers.code_scanner import CodeScanner
from src.analyzers.class_categorizer import ClassCategorizer
from src.analyzers.dependency_mapper import DependencyMapper, ClassDependency
from src.analyzers.project_analyzer import ProjectAnalyzer
from src.parsers.tree_sitter_parser import TreeSitterJavaParser
from src.models.java_models import JavaClass


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures" / "sample_java"


@pytest.fixture
def parser():
    """Create a parser instance for tests."""
    return TreeSitterJavaParser()


@pytest.fixture
def sample_classes(parser, fixtures_dir):
    """Parse all sample Java files."""
    java_files = list(fixtures_dir.glob("*.java"))
    classes = []

    for file_path in java_files:
        content = file_path.read_text()
        java_class = parser.parse_file(str(file_path), content)
        classes.append(java_class)

    return classes


class TestCodeScanner:
    """Test the CodeScanner class."""

    def test_scanner_initialization(self, fixtures_dir):
        """Test scanner initialization."""
        scanner = CodeScanner(str(fixtures_dir))
        assert scanner.repository_path.exists()
        assert scanner.repository_path.is_dir()

    def test_invalid_path_raises_error(self):
        """Test that invalid path raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            CodeScanner("/nonexistent/path")

    def test_find_java_files(self, fixtures_dir):
        """Test finding Java files."""
        scanner = CodeScanner(str(fixtures_dir))
        java_files = scanner.find_java_files()

        assert len(java_files) > 0
        assert all(f.suffix == ".java" for f in java_files)

    def test_scan_repository(self, fixtures_dir):
        """Test scanning repository."""
        scanner = CodeScanner(str(fixtures_dir))
        java_classes = scanner.scan_repository(verbose=False)

        assert len(java_classes) > 0
        assert all(isinstance(cls, JavaClass) for cls in java_classes)

    def test_get_controllers(self, fixtures_dir):
        """Test getting controllers."""
        scanner = CodeScanner(str(fixtures_dir))
        scanner.scan_repository(verbose=False)

        controllers = scanner.get_controllers()
        assert len(controllers) > 0
        assert all(cls.category == "Controller" for cls in controllers)

    def test_get_services(self, fixtures_dir):
        """Test getting services."""
        scanner = CodeScanner(str(fixtures_dir))
        scanner.scan_repository(verbose=False)

        services = scanner.get_services()
        assert len(services) > 0
        assert all(cls.category == "Service" for cls in services)

    def test_get_repositories(self, fixtures_dir):
        """Test getting repositories."""
        scanner = CodeScanner(str(fixtures_dir))
        scanner.scan_repository(verbose=False)

        repositories = scanner.get_repositories()
        assert len(repositories) > 0
        assert all(cls.category == "DAO" for cls in repositories)

    def test_get_entities(self, fixtures_dir):
        """Test getting entities."""
        scanner = CodeScanner(str(fixtures_dir))
        scanner.scan_repository(verbose=False)

        entities = scanner.get_entities()
        assert len(entities) > 0
        assert all(cls.category == "Entity" for cls in entities)

    def test_get_statistics(self, fixtures_dir):
        """Test getting statistics."""
        scanner = CodeScanner(str(fixtures_dir))
        scanner.scan_repository(verbose=False)

        stats = scanner.get_statistics()

        assert "total_files" in stats
        assert "parsed_successfully" in stats
        assert "total_classes" in stats
        assert "total_methods" in stats
        assert "total_fields" in stats
        assert stats["parsed_successfully"] > 0


class TestClassCategorizer:
    """Test the ClassCategorizer class."""

    def test_categorizer_initialization(self):
        """Test categorizer initialization."""
        categorizer = ClassCategorizer()
        assert categorizer is not None

    def test_categorize_controller(self, sample_classes):
        """Test categorizing a controller."""
        categorizer = ClassCategorizer()

        # Find CustomerController
        controller = next(
            (cls for cls in sample_classes if cls.name == "CustomerController"), None
        )
        assert controller is not None

        category = categorizer.categorize(controller)
        assert category == "Controller"

    def test_categorize_service(self, sample_classes):
        """Test categorizing a service."""
        categorizer = ClassCategorizer()

        # Find CustomerService
        service = next(
            (cls for cls in sample_classes if cls.name == "CustomerService"), None
        )
        assert service is not None

        category = categorizer.categorize(service)
        assert category == "Service"

    def test_categorize_repository(self, sample_classes):
        """Test categorizing a repository."""
        categorizer = ClassCategorizer()

        # Find CustomerRepository
        repository = next(
            (cls for cls in sample_classes if cls.name == "CustomerRepository"), None
        )
        assert repository is not None

        category = categorizer.categorize(repository)
        assert category == "DAO"

    def test_categorize_entity(self, sample_classes):
        """Test categorizing an entity."""
        categorizer = ClassCategorizer()

        # Find Customer entity
        entity = next((cls for cls in sample_classes if cls.name == "Customer"), None)
        assert entity is not None

        category = categorizer.categorize(entity)
        assert category == "Entity"

    def test_get_category_confidence(self, sample_classes):
        """Test getting category confidence scores."""
        categorizer = ClassCategorizer()

        # Test with CustomerController
        controller = next(
            (cls for cls in sample_classes if cls.name == "CustomerController"), None
        )
        assert controller is not None

        confidence = categorizer.get_category_confidence(controller)

        assert "Controller" in confidence
        assert "Service" in confidence
        assert confidence["Controller"] > confidence["Service"]


class TestDependencyMapper:
    """Test the DependencyMapper class."""

    def test_mapper_initialization(self, sample_classes):
        """Test mapper initialization."""
        mapper = DependencyMapper(sample_classes)
        assert mapper is not None
        assert len(mapper.java_classes) == len(sample_classes)

    def test_map_dependencies(self, sample_classes):
        """Test mapping dependencies."""
        mapper = DependencyMapper(sample_classes)
        graph = mapper.map_dependencies()

        assert graph is not None
        assert len(graph.dependencies) > 0

    def test_field_injection_dependencies(self, sample_classes):
        """Test detecting field injection dependencies."""
        mapper = DependencyMapper(sample_classes)
        graph = mapper.map_dependencies()

        injection_deps = mapper.get_injection_dependencies()
        assert len(injection_deps) > 0

        # Verify injection types
        for dep in injection_deps:
            assert dep.dependency_type == "field_injection"

    def test_extract_base_type_from_generic(self, sample_classes):
        """Test extracting base type from generic types."""
        mapper = DependencyMapper(sample_classes)

        # Test with List<Customer>
        base_type = mapper._extract_base_type("List<Customer>")
        # Should return Customer if it's in our codebase, otherwise List
        assert base_type in ["List", "Customer"]

        # Test with arrays
        base_type = mapper._extract_base_type("Customer[]")
        assert base_type == "Customer"

    def test_get_class_hierarchy(self, sample_classes):
        """Test getting class hierarchy."""
        mapper = DependencyMapper(sample_classes)
        mapper.map_dependencies()

        hierarchy = mapper.get_class_hierarchy()
        assert isinstance(hierarchy, dict)

    def test_get_interface_implementations(self, sample_classes):
        """Test getting interface implementations."""
        mapper = DependencyMapper(sample_classes)
        mapper.map_dependencies()

        implementations = mapper.get_interface_implementations()
        assert isinstance(implementations, dict)

        # CustomerRepository should implement JpaRepository
        if "JpaRepository" in implementations:
            assert "CustomerRepository" in implementations["JpaRepository"]

    def test_dependency_statistics(self, sample_classes):
        """Test getting dependency statistics."""
        mapper = DependencyMapper(sample_classes)
        mapper.map_dependencies()

        stats = mapper.get_dependency_statistics()

        assert "total_dependencies" in stats
        assert "injection_dependencies" in stats
        assert "dependencies_by_type" in stats
        assert stats["total_dependencies"] > 0


class TestProjectAnalyzer:
    """Test the ProjectAnalyzer class."""

    def test_analyzer_initialization(self, fixtures_dir):
        """Test analyzer initialization."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        assert analyzer is not None
        assert analyzer.repository_path.exists()

    def test_analyze_project(self, fixtures_dir):
        """Test analyzing a project."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analysis = analyzer.analyze(verbose=False)

        assert analysis is not None
        assert len(analysis.java_classes) > 0
        assert analysis.dependency_graph is not None
        assert analysis.statistics is not None
        assert analysis.categories is not None

    def test_get_controllers(self, fixtures_dir):
        """Test getting controllers from analysis."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analyzer.analyze(verbose=False)

        controllers = analyzer.get_controllers()
        assert len(controllers) > 0

    def test_get_services(self, fixtures_dir):
        """Test getting services from analysis."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analyzer.analyze(verbose=False)

        services = analyzer.get_services()
        assert len(services) > 0

    def test_get_repositories(self, fixtures_dir):
        """Test getting repositories from analysis."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analyzer.analyze(verbose=False)

        repositories = analyzer.get_repositories()
        assert len(repositories) > 0

    def test_get_entities(self, fixtures_dir):
        """Test getting entities from analysis."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analyzer.analyze(verbose=False)

        entities = analyzer.get_entities()
        assert len(entities) > 0

    def test_export_analysis(self, fixtures_dir, tmp_path):
        """Test exporting analysis to JSON."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analyzer.analyze(verbose=False)

        output_path = tmp_path / "analysis.json"
        analyzer.export_analysis(str(output_path))

        assert output_path.exists()

        # Verify JSON content
        import json

        with output_path.open() as f:
            data = json.load(f)

        assert "project_path" in data
        assert "statistics" in data
        assert "categories" in data
        assert "dependencies" in data

    def test_analysis_statistics(self, fixtures_dir):
        """Test analysis statistics."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analysis = analyzer.analyze(verbose=False)

        stats = analysis.statistics

        assert stats["total_files"] > 0
        assert stats["parsed_successfully"] > 0
        assert stats["total_classes"] > 0
        assert stats["total_methods"] > 0
        assert stats["total_fields"] > 0
        assert stats["total_dependencies"] > 0

    def test_category_grouping(self, fixtures_dir):
        """Test category grouping."""
        analyzer = ProjectAnalyzer(str(fixtures_dir))
        analysis = analyzer.analyze(verbose=False)

        categories = analysis.categories

        assert "Controller" in categories
        assert "Service" in categories
        assert "DAO" in categories
        assert "Entity" in categories

        # Verify all classes are categorized
        total_categorized = sum(len(classes) for classes in categories.values())
        assert total_categorized == len(analysis.java_classes)
