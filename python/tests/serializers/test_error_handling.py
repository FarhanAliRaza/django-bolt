import pytest

from django_bolt.serializers.errors import (
    ErrorCollector,
    FieldError,
    ValidationError,
    format_field_path,
    parse_field_path,
)


class TestValidationError:
    """Test ValidationError class."""

    def test_init_defaults(self):
        e = ValidationError()
        assert e.detail == "Validation error"
        assert e.errors == {}

    def test_init_with_errors(self):
        errors = {"field": [FieldError("Error")]}
        e = ValidationError(errors=errors)
        assert e.errors == errors

    def test_str_representation(self):
        e = ValidationError(detail="Main error")
        assert str(e) == "Main error"
        
        e.add_error("field", "Field error")
        assert str(e) == "field: Field error"

    def test_add_error(self):
        e = ValidationError()
        e.add_error("field", "Error message", code="invalid")
        
        assert "field" in e.errors
        assert len(e.errors["field"]) == 1
        assert e.errors["field"][0].message == "Error message"
        assert e.errors["field"][0].code == "invalid"

    def test_merge(self):
        e1 = ValidationError()
        e1.add_error("f1", "Error 1")
        
        e2 = ValidationError()
        e2.add_error("f2", "Error 2")
        
        e1.merge(e2)
        assert "f1" in e1.errors
        assert "f2" in e1.errors
        
        # Test valid prefix merging
        e3 = ValidationError()
        e3.add_error("child_field", "Child error")
        
        e1.merge(e3, prefix="parent")
        assert "parent.child_field" in e1.errors

    def test_to_dict(self):
        e = ValidationError()
        e.add_error("f1", "Error 1", code="code1")
        
        data = e.to_dict()
        assert data["detail"] == "Validation error"
        assert data["errors"]["f1"][0]["message"] == "Error 1"
        assert data["errors"]["f1"][0]["code"] == "code1"


class TestErrorCollector:
    """Test ErrorCollector class."""

    def test_collect_and_raise(self):
        c = ErrorCollector()
        assert not c.has_errors()
        
        c.add_error("f1", "Error")
        assert c.has_errors()
        
        with pytest.raises(ValidationError) as exc:
            c.raise_if_errors()
            
        assert "f1" in exc.value.errors
        assert exc.value.errors["f1"][0].message == "Error"

    def test_no_raise_if_clean(self):
        c = ErrorCollector()
        c.raise_if_errors()  # Should not raise

    def test_merge(self):
        c1 = ErrorCollector()
        c1.add_error("f1", "E1")
        
        c2 = ErrorCollector()
        c2.add_error("f2", "E2")
        
        c1.merge(c2)
        assert "f1" in c1.errors
        assert "f2" in c1.errors


def test_field_path_utils():
    """Test field path formatting and parsing."""
    assert format_field_path("a", "b", "c") == "a.b.c"
    assert format_field_path("a", "", "c") == "a.c"
    
    assert parse_field_path("a.b.c") == ["a", "b", "c"]
