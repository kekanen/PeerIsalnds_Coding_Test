"""
Tests for the tree-sitter Java parser.
"""

import pytest
from pathlib import Path
from src.parsers.tree_sitter_parser import TreeSitterJavaParser
from src.models.java_models import JavaClass, JavaMethod, JavaField


@pytest.fixture
def parser():
    """Create a parser instance for tests."""
    return TreeSitterJavaParser()


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures" / "sample_java"


class TestPackageAndImports:
    """Test package and import extraction."""

    def test_extract_package(self, parser, fixtures_dir):
        """Test package declaration extraction."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.package == "com.sakila.model"

    def test_extract_imports(self, parser, fixtures_dir):
        """Test import statements extraction."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert len(java_class.imports) > 0
        assert any("springframework" in imp for imp in java_class.imports)


class TestClassExtraction:
    """Test class metadata extraction."""

    def test_extract_class_name(self, parser, fixtures_dir):
        """Test class name extraction."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.name == "Customer"
        assert java_class.type == "class"

    def test_extract_interface(self, parser, fixtures_dir):
        """Test interface extraction."""
        file_path = fixtures_dir / "CustomerRepository.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.name == "CustomerRepository"
        assert java_class.type == "interface"

    def test_extract_class_modifiers(self, parser, fixtures_dir):
        """Test class modifiers extraction."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert "public" in java_class.modifiers


class TestAnnotations:
    """Test annotation extraction."""

    def test_extract_class_annotations(self, parser, fixtures_dir):
        """Test class-level annotations."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert len(java_class.annotations) >= 2
        annotation_names = [ann.name for ann in java_class.annotations]
        assert "RestController" in annotation_names
        assert "RequestMapping" in annotation_names

    def test_extract_field_annotations(self, parser, fixtures_dir):
        """Test field annotations."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        # Find the id field
        id_field = next((f for f in java_class.fields if f.name == "id"), None)
        assert id_field is not None

        annotation_names = [ann.name for ann in id_field.annotations]
        assert "Id" in annotation_names
        assert "GeneratedValue" in annotation_names

    def test_extract_method_annotations(self, parser, fixtures_dir):
        """Test method annotations."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        # Find getAllCustomers method
        method = next((m for m in java_class.methods if m.name == "getAllCustomers"), None)
        assert method is not None

        annotation_names = [ann.name for ann in method.annotations]
        assert "GetMapping" in annotation_names


class TestFieldExtraction:
    """Test field extraction."""

    def test_extract_fields(self, parser, fixtures_dir):
        """Test field extraction."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert len(java_class.fields) > 0

        field_names = [f.name for f in java_class.fields]
        assert "id" in field_names
        assert "firstName" in field_names
        assert "email" in field_names

    def test_field_types(self, parser, fixtures_dir):
        """Test field type extraction."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        id_field = next((f for f in java_class.fields if f.name == "id"), None)
        assert id_field is not None
        assert id_field.type == "Long"

        email_field = next((f for f in java_class.fields if f.name == "email"), None)
        assert email_field is not None
        assert email_field.type == "String"

    def test_field_modifiers(self, parser, fixtures_dir):
        """Test field modifier extraction."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        # Most fields should be private
        for field in java_class.fields:
            assert "private" in field.modifiers


class TestMethodExtraction:
    """Test method extraction."""

    def test_extract_methods(self, parser, fixtures_dir):
        """Test method extraction."""
        file_path = fixtures_dir / "CustomerService.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert len(java_class.methods) > 0

        method_names = [m.name for m in java_class.methods]
        assert "findAll" in method_names
        assert "findById" in method_names
        assert "save" in method_names

    def test_method_return_types(self, parser, fixtures_dir):
        """Test method return type extraction."""
        file_path = fixtures_dir / "CustomerService.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        find_all_method = next((m for m in java_class.methods if m.name == "findAll"), None)
        assert find_all_method is not None
        assert "List" in find_all_method.return_type

    def test_method_parameters(self, parser, fixtures_dir):
        """Test method parameter extraction."""
        file_path = fixtures_dir / "CustomerService.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        save_method = next((m for m in java_class.methods if m.name == "save"), None)
        assert save_method is not None
        assert len(save_method.parameters) == 1
        assert save_method.parameters[0].name == "customer"
        assert save_method.parameters[0].type == "Customer"

    def test_method_with_multiple_parameters(self, parser, fixtures_dir):
        """Test method with multiple parameters."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        update_method = next((m for m in java_class.methods if m.name == "updateCustomer"), None)
        assert update_method is not None
        assert len(update_method.parameters) == 2


class TestCategorization:
    """Test class categorization."""

    def test_categorize_controller(self, parser, fixtures_dir):
        """Test Controller categorization."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.category == "Controller"

    def test_categorize_service(self, parser, fixtures_dir):
        """Test Service categorization."""
        file_path = fixtures_dir / "CustomerService.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.category == "Service"

    def test_categorize_repository(self, parser, fixtures_dir):
        """Test Repository categorization."""
        file_path = fixtures_dir / "CustomerRepository.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.category == "DAO"

    def test_categorize_entity(self, parser, fixtures_dir):
        """Test Entity categorization."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.category == "Entity"


class TestHelperMethods:
    """Test JavaClass helper methods."""

    def test_is_controller(self, parser, fixtures_dir):
        """Test is_controller() method."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.is_controller() is True

    def test_is_service(self, parser, fixtures_dir):
        """Test is_service() method."""
        file_path = fixtures_dir / "CustomerService.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.is_service() is True

    def test_is_entity(self, parser, fixtures_dir):
        """Test is_entity() method."""
        file_path = fixtures_dir / "Customer.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        assert java_class.is_entity() is True

    def test_get_rest_endpoints(self, parser, fixtures_dir):
        """Test get_rest_endpoints() method."""
        file_path = fixtures_dir / "CustomerController.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        endpoints = java_class.get_rest_endpoints()
        assert len(endpoints) == 5  # GET, GET by ID, POST, PUT, DELETE

        endpoint_names = [e.name for e in endpoints]
        assert "getAllCustomers" in endpoint_names
        assert "getCustomerById" in endpoint_names

    def test_get_public_methods(self, parser, fixtures_dir):
        """Test get_public_methods() method."""
        file_path = fixtures_dir / "CustomerService.java"
        content = file_path.read_text()

        java_class = parser.parse_file(str(file_path), content)

        public_methods = java_class.get_public_methods()
        assert len(public_methods) > 0
