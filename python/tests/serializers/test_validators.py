import re
import pytest
from unittest.mock import MagicMock

from django_bolt.serializers import (
    ChoicesValidator,
    EmailValidator,
    ExistsValidator,
    LengthValidator,
    MaxLengthValidator,
    MinLengthValidator,
    MaxValueValidator,
    MinValueValidator,
    PhoneValidator,
    RangeValidator,
    RegexValidator,
    SlugValidator,
    UniqueValidator,
    URLValidator,
    UUIDValidator,
    validator,
)


class TestValidators:
    """Test functionality of built-in validators."""

    def test_min_length_validator(self):
        v = MinLengthValidator(3)
        assert v("abc") == "abc"
        assert v("abcd") == "abcd"
        
        with pytest.raises(ValueError, match="Must be at least 3 characters long"):
            v("ab")
            
        # None pass through
        assert v(None) is None

    def test_max_length_validator(self):
        v = MaxLengthValidator(3)
        assert v("abc") == "abc"
        assert v("ab") == "ab"
        
        with pytest.raises(ValueError, match="Must be at most 3 characters long"):
            v("abcd")

    def test_length_validator(self):
        v = LengthValidator(min_length=2, max_length=4)
        assert v("ab") == "ab"
        assert v("abcd") == "abcd"
        
        with pytest.raises(ValueError, match="Must be at least 2 characters long"):
            v("a")
            
        with pytest.raises(ValueError, match="Must be at most 4 characters long"):
            v("abcde")

    def test_regex_validator(self):
        v = RegexValidator(r"^[a-z]+$")
        assert v("abc") == "abc"
        
        with pytest.raises(ValueError, match="Value must match pattern"):
            v("123")
            
        # Inverse match
        v_inv = RegexValidator(r"^[a-z]+$", inverse_match=True)
        assert v_inv("123") == "123"
        
        with pytest.raises(ValueError, match="Value must not match pattern"):
            v_inv("abc")
            
        # Compiled regex
        v_comp = RegexValidator(re.compile(r"^[a-z]+$"))
        assert v_comp("abc") == "abc"

    def test_min_value_validator(self):
        v = MinValueValidator(10)
        assert v(10) == 10
        assert v(11) == 11
        
        with pytest.raises(ValueError, match="Must be at least 10"):
            v(9)

    def test_max_value_validator(self):
        v = MaxValueValidator(10)
        assert v(10) == 10
        assert v(9) == 9
        
        with pytest.raises(ValueError, match="Must be at most 10"):
            v(11)

    def test_range_validator(self):
        v = RangeValidator(min_value=5, max_value=10)
        assert v(5) == 5
        assert v(10) == 10
        assert v(7) == 7
        
        with pytest.raises(ValueError, match="Must be at least 5"):
            v(4)
            
        with pytest.raises(ValueError, match="Must be at most 10"):
            v(11)

    def test_choices_validator(self):
        v = ChoicesValidator(("A", "B", "C"))
        assert v("A") == "A"
        
        with pytest.raises(ValueError, match="Must be one of: 'A', 'B', 'C'"):
            v("D")

    def test_email_validator(self):
        assert EmailValidator("test@example.com") == "test@example.com"
        
        with pytest.raises(ValueError, match="Enter a valid email address"):
            EmailValidator("invalid-email")

    def test_url_validator(self):
        assert URLValidator("https://example.com") == "https://example.com"
        
        with pytest.raises(ValueError, match="Enter a valid URL"):
            URLValidator("not-a-url")

    def test_slug_validator(self):
        assert SlugValidator("my-slug_123") == "my-slug_123"
        
        with pytest.raises(ValueError, match="Enter a valid slug"):
            SlugValidator("Invalid Slug")

    def test_uuid_validator(self):
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        assert UUIDValidator(uuid_str) == uuid_str
        
        with pytest.raises(ValueError, match="Enter a valid UUID"):
            UUIDValidator("not-a-uuid")
            
    def test_phone_validator(self):
        assert PhoneValidator("+1234567890") == "+1234567890"
        
        with pytest.raises(ValueError, match="Enter a valid phone number"):
            PhoneValidator("abc")


class TestDatabaseValidators:
    """Test validators that require database access (mocked)."""
    
    def test_unique_validator(self):
        queryset = MagicMock()
        queryset.filter.return_value.exists.return_value = False
        
        v = UniqueValidator(queryset, "username")
        assert v("newuser") == "newuser"
        queryset.filter.assert_called_with(username__exact="newuser")
        
        queryset.filter.return_value.exists.return_value = True
        with pytest.raises(ValueError, match="A record with this username already exists"):
            v("existing")

    def test_exists_validator(self):
        queryset = MagicMock()
        queryset.filter.return_value.exists.return_value = True
        
        v = ExistsValidator(queryset)
        assert v(1) == 1
        queryset.filter.assert_called_with(id=1)
        
        queryset.filter.return_value.exists.return_value = False
        with pytest.raises(ValueError, match="Object with id=1 does not exist"):
            v(1)


def test_validator_decorator():
    """Test the @validator decorator."""
    
    @validator("field1")
    def validate_one(cls, value):
        return value
        
    assert validate_one.__validator_fields__ == ("field1",)
    assert validate_one.__validator_field__ == "field1"
    
    @validator("field1", "field2")
    def validate_two(cls, value):
        return value
        
    assert validate_two.__validator_fields__ == ("field1", "field2")
    assert not hasattr(validate_two, "__validator_field__")
