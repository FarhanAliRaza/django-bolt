"""
Tests for ModelSerializer validation.

This module tests DRF-style field-level and object-level validation
for ModelSerializer.
"""

import pytest
import msgspec
from decimal import Decimal
from datetime import date
from django.db import models
from django_bolt.serializers import ModelSerializer, ValidationError


# Test models
class Product(models.Model):
    """Product model for testing validation."""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    min_age = models.IntegerField(default=0)
    is_premium = models.BooleanField(default=False)
    email = models.EmailField(blank=True, default="")

    class Meta:
        app_label = 'django_bolt'


# Test serializers with validation
class ProductSerializer(ModelSerializer):
    """Serializer with field-level validators."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'min_age', 'is_premium', 'email']

    def validate_price(self, value):
        """Price must be positive."""
        if value <= 0:
            raise ValidationError("Price must be positive")
        if value > 10000:
            raise ValidationError("Price cannot exceed $10,000")
        return value

    def validate_stock(self, value):
        """Stock must be non-negative."""
        if value < 0:
            raise ValidationError("Stock cannot be negative")
        return value

    def validate_min_age(self, value):
        """Minimum age must be between 0 and 120."""
        if value < 0:
            raise ValidationError("Minimum age cannot be negative")
        if value > 120:
            raise ValidationError("Minimum age cannot exceed 120")
        return value

    def validate_email(self, value):
        """Email must end with @company.com if provided."""
        if value and not value.endswith('@company.com'):
            raise ValidationError("Must use company email (@company.com)")
        return value


class ProductWithObjectValidation(ModelSerializer):
    """Serializer with object-level validation."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'min_age', 'is_premium']

    def validate_price(self, value):
        """Price must be positive."""
        if value <= 0:
            raise ValidationError("Price must be positive")
        return value

    def validate(self, data):
        """Object-level validation: premium products must cost at least $100."""
        if data.get('is_premium') and data.get('price', 0) < 100:
            raise ValidationError("Premium products must cost at least $100")

        # Premium products must have minimum age 18+
        if data.get('is_premium') and data.get('min_age', 0) < 18:
            raise ValidationError("Premium products require minimum age 18+")

        return data


class ProductValueTransformer(ModelSerializer):
    """Serializer that transforms values in validators."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

    def validate_name(self, value):
        """Transform name to uppercase."""
        return value.upper()

    def validate_price(self, value):
        """Round price to 2 decimal places."""
        return round(value, 2)


# Tests
class TestFieldValidation:
    """Test field-level validation (validate_<fieldname>)."""

    def test_field_validator_is_detected(self):
        """Test that validate_<fieldname> methods are detected."""
        assert hasattr(ProductSerializer, '_field_validators')
        assert 'price' in ProductSerializer._field_validators
        assert 'stock' in ProductSerializer._field_validators
        assert 'min_age' in ProductSerializer._field_validators

    def test_valid_data_passes_validation(self):
        """Test that valid data passes field validation."""
        # Create mock product
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('99.99')
            stock = 10
            min_age = 18
            is_premium = False
            email = "test@company.com"

        # Should not raise
        result = ProductSerializer.from_model(MockProduct())

        assert isinstance(result, msgspec.Struct)
        assert result.price == Decimal('99.99')
        assert result.stock == 10

    def test_invalid_price_raises_validation_error(self):
        """Test that invalid price raises ValidationError."""
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('-10.00')  # Invalid: negative
            stock = 10
            min_age = 18
            is_premium = False
            email = ""

        with pytest.raises(ValidationError, match="Price must be positive"):
            ProductSerializer.from_model(MockProduct())

    def test_price_too_high_raises_validation_error(self):
        """Test that price over limit raises ValidationError."""
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('15000.00')  # Invalid: too high
            stock = 10
            min_age = 18
            is_premium = False
            email = ""

        with pytest.raises(ValidationError, match="cannot exceed"):
            ProductSerializer.from_model(MockProduct())

    def test_negative_stock_raises_validation_error(self):
        """Test that negative stock raises ValidationError."""
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('99.99')
            stock = -5  # Invalid: negative
            min_age = 18
            is_premium = False
            email = ""

        with pytest.raises(ValidationError, match="Stock cannot be negative"):
            ProductSerializer.from_model(MockProduct())

    def test_invalid_age_raises_validation_error(self):
        """Test that invalid age raises ValidationError."""
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('99.99')
            stock = 10
            min_age = 150  # Invalid: too high
            is_premium = False
            email = ""

        with pytest.raises(ValidationError, match="cannot exceed 120"):
            ProductSerializer.from_model(MockProduct())

    def test_invalid_email_raises_validation_error(self):
        """Test that invalid email raises ValidationError."""
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('99.99')
            stock = 10
            min_age = 18
            is_premium = False
            email = "test@gmail.com"  # Invalid: not @company.com

        with pytest.raises(ValidationError, match="Must use company email"):
            ProductSerializer.from_model(MockProduct())

    def test_validation_can_be_skipped(self):
        """Test that validation can be skipped with validate=False."""
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('-10.00')  # Invalid, but validation skipped
            stock = 10
            min_age = 18
            is_premium = False
            email = ""

        # Should not raise when validation is disabled
        result = ProductSerializer.from_model(MockProduct(), validate=False)
        assert isinstance(result, msgspec.Struct)
        assert result.price == Decimal('-10.00')


class TestObjectValidation:
    """Test object-level validation (validate method)."""

    def test_object_validator_is_detected(self):
        """Test that validate() method is detected."""
        assert hasattr(ProductWithObjectValidation, '_object_validator')

    def test_valid_object_passes_validation(self):
        """Test that valid object passes validation."""
        class MockProduct:
            id = 1
            name = "Test Product"
            price = Decimal('99.99')
            stock = 10
            min_age = 0
            is_premium = False

        result = ProductWithObjectValidation.from_model(MockProduct())
        assert isinstance(result, msgspec.Struct)

    def test_premium_product_below_min_price_fails(self):
        """Test that premium products below $100 fail validation."""
        class MockProduct:
            id = 1
            name = "Premium Product"
            price = Decimal('50.00')  # Invalid: premium but < $100
            stock = 10
            min_age = 18
            is_premium = True

        with pytest.raises(ValidationError, match="must cost at least"):
            ProductWithObjectValidation.from_model(MockProduct())

    def test_premium_product_below_min_age_fails(self):
        """Test that premium products with min_age < 18 fail validation."""
        class MockProduct:
            id = 1
            name = "Premium Product"
            price = Decimal('150.00')
            stock = 10
            min_age = 12  # Invalid: premium requires 18+
            is_premium = True

        with pytest.raises(ValidationError, match="minimum age 18"):
            ProductWithObjectValidation.from_model(MockProduct())

    def test_field_and_object_validation_both_run(self):
        """Test that both field and object validators run."""
        class MockProduct:
            id = 1
            name = "Premium Product"
            price = Decimal('-10.00')  # Invalid: negative (field validation)
            stock = 10
            min_age = 18
            is_premium = True

        # Should fail on field validation before reaching object validation
        with pytest.raises(ValidationError, match="Price must be positive"):
            ProductWithObjectValidation.from_model(MockProduct())


class TestValueTransformation:
    """Test that validators can transform values."""

    def test_name_is_uppercased(self):
        """Test that name validator transforms to uppercase."""
        class MockProduct:
            id = 1
            name = "test product"
            price = Decimal('99.999')

        result = ProductValueTransformer.from_model(MockProduct())
        assert result.name == "TEST PRODUCT"

    def test_price_is_rounded(self):
        """Test that price validator rounds to 2 decimals."""
        class MockProduct:
            id = 1
            name = "Test"
            price = Decimal('99.999')

        result = ProductValueTransformer.from_model(MockProduct())
        assert result.price == Decimal('100.00')


class TestJSONDecodingWithValidation:
    """Test decode() and decode_json() with validation."""

    def test_decode_valid_json(self):
        """Test decoding valid JSON with validation."""
        json_data = b'{"id": 1, "name": "Test", "price": 99.99, "stock": 10, "min_age": 18, "is_premium": false, "email": "test@company.com"}'

        result = ProductSerializer.decode(json_data)

        assert isinstance(result, msgspec.Struct)
        assert result.name == "Test"
        assert result.price == Decimal('99.99')

    def test_decode_invalid_json_raises_validation_error(self):
        """Test that decoding invalid data raises ValidationError."""
        json_data = b'{"id": 1, "name": "Test", "price": -10, "stock": 10, "min_age": 18, "is_premium": false, "email": ""}'

        with pytest.raises(ValidationError, match="Price must be positive"):
            ProductSerializer.decode(json_data)

    def test_decode_with_validation_disabled(self):
        """Test decode with validation=False."""
        json_data = b'{"id": 1, "name": "Test", "price": -10, "stock": 10, "min_age": 18, "is_premium": false, "email": ""}'

        # Should not raise with validation disabled
        result = ProductSerializer.decode(json_data, validate=False)
        assert isinstance(result, msgspec.Struct)
        assert result.price == -10

    def test_decode_json_string(self):
        """Test decoding JSON string."""
        json_str = '{"id": 1, "name": "Test", "price": 99.99, "stock": 10, "min_age": 18, "is_premium": false, "email": "test@company.com"}'

        result = ProductSerializer.decode_json(json_str)

        assert isinstance(result, msgspec.Struct)
        assert result.name == "Test"

    def test_decode_with_object_validation(self):
        """Test decode with object-level validation."""
        # Valid data
        json_data = b'{"id": 1, "name": "Premium", "price": 150, "stock": 10, "min_age": 18, "is_premium": true}'
        result = ProductWithObjectValidation.decode(json_data)
        assert result.is_premium is True

        # Invalid: premium but price too low
        json_data = b'{"id": 1, "name": "Premium", "price": 50, "stock": 10, "min_age": 18, "is_premium": true}'
        with pytest.raises(ValidationError, match="must cost at least"):
            ProductWithObjectValidation.decode(json_data)


class TestValidationWithQuerysets:
    """Test validation with multiple instances."""

    def test_from_models_with_validation(self):
        """Test from_models() runs validation on all instances."""
        class MockProduct1:
            id = 1
            name = "Product 1"
            price = Decimal('99.99')
            stock = 10
            min_age = 0
            is_premium = False
            email = ""

        class MockProduct2:
            id = 2
            name = "Product 2"
            price = Decimal('49.99')
            stock = 5
            min_age = 0
            is_premium = False
            email = ""

        products = [MockProduct1(), MockProduct2()]
        results = ProductSerializer.from_models(products)

        assert len(results) == 2
        assert all(isinstance(r, msgspec.Struct) for r in results)

    def test_from_models_raises_on_invalid_item(self):
        """Test that from_models() raises on first invalid item."""
        class MockProduct1:
            id = 1
            name = "Product 1"
            price = Decimal('99.99')
            stock = 10
            min_age = 0
            is_premium = False
            email = ""

        class MockProduct2:
            id = 2
            name = "Product 2"
            price = Decimal('-10.00')  # Invalid!
            stock = 5
            min_age = 0
            is_premium = False
            email = ""

        products = [MockProduct1(), MockProduct2()]

        with pytest.raises(ValidationError, match="Price must be positive"):
            ProductSerializer.from_models(products)


def test_validation_error_format():
    """Test ValidationError can be raised with different formats."""
    # String message
    err1 = ValidationError("Simple error")
    assert str(err1) == "Simple error"
    assert err1.detail == "Simple error"

    # Dict message
    err2 = ValidationError({"field": "error message"})
    assert err2.detail == {"field": "error message"}

    # List message
    err3 = ValidationError(["error1", "error2"])
    assert err3.detail == ["error1", "error2"]


def test_documentation_example():
    """
    Documentation example showing validation usage.

    This demonstrates the DRF-style validation API.
    """
    example_code = """
    from django_bolt.serializers import ModelSerializer, ValidationError

    class UserSerializer(ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'age', 'is_premium']

        def validate_age(self, value):
            if value < 18:
                raise ValidationError("Must be 18 or older")
            return value

        def validate_email(self, value):
            if not value.endswith('@company.com'):
                raise ValidationError("Must use company email")
            return value

        def validate(self, data):
            # Multi-field validation
            if data.get('is_premium') and data.get('age', 0) < 21:
                raise ValidationError("Premium users must be 21+")
            return data

    # In API endpoints:
    @api.post("/users")
    async def create_user(request):
        # Decode and validate request body
        user_data = UserSerializer.decode(request['body'])

        # Create user (data is already validated)
        user = await User.objects.acreate(**msgspec.structs.asdict(user_data))

        # Return serialized response
        return UserSerializer.from_model(user)
    """
    assert example_code is not None
