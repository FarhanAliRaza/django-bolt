# Django-Bolt ModelSerializer Validation

Django-Bolt's `ModelSerializer` includes DRF-style validation that allows you to add field-level and object-level validation to your serializers, just like Django REST Framework.

## Features

- **Field-Level Validation**: `validate_<fieldname>` methods for individual field validation
- **Object-Level Validation**: `validate()` method for cross-field validation
- **Value Transformation**: Validators can transform values before serialization
- **JSON Decoding with Validation**: `decode()` and `decode_json()` methods
- **Performance**: Validation runs efficiently without sacrificing msgspec's speed
- **DRF-Compatible**: Familiar API for DRF users

## Quick Start

###Field-Level Validation

Use `validate_<fieldname>(self, value)` methods to validate individual fields:

```python
from django_bolt.serializers import ModelSerializer, ValidationError

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age']

    def validate_age(self, value):
        """Validate that age is at least 18."""
        if value < 18:
            raise ValidationError("Must be 18 or older")
        return value

    def validate_email(self, value):
        """Validate that email uses company domain."""
        if not value.endswith('@company.com'):
            raise ValidationError("Must use company email address")
        return value
```

### Object-Level Validation

Use `validate(self, data)` method for multi-field validation:

```python
class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'is_premium', 'min_age']

    def validate_price(self, value):
        """Price must be positive."""
        if value <= 0:
            raise ValidationError("Price must be positive")
        return value

    def validate(self, data):
        """Premium products must cost at least $100."""
        if data.get('is_premium') and data.get('price', 0) < 100:
            raise ValidationError("Premium products must cost at least $100")

        # Premium products require age 18+
        if data.get('is_premium') and data.get('min_age', 0) < 18:
            raise ValidationError("Premium products require minimum age 18+")

        return data
```

## Using Validation

### With Django Models

Validation runs automatically when using `from_model()`:

```python
@api.get("/users/{id}")
async def get_user(id: int):
    user = await User.objects.aget(id=id)

    # Validation runs automatically
    return UserSerializer.from_model(user)

    # Skip validation if needed
    # return UserSerializer.from_model(user, validate=False)
```

### With JSON Request Bodies

Use `decode()` or `decode_json()` to parse and validate JSON:

```python
@api.post("/users")
async def create_user(request):
    # Decode JSON and run validation
    user_data = UserSerializer.decode(request['body'])

    # Data is validated and ready to use
    user = await User.objects.acreate(**msgspec.structs.asdict(user_data))

    return UserSerializer.from_model(user)
```

### Skipping Validation

You can skip validation by passing `validate=False`:

```python
# Skip validation on from_model
serialized = UserSerializer.from_model(user, validate=False)

# Skip validation on decode
data = UserSerializer.decode(json_bytes, validate=False)
```

## Validation Examples

### Example 1: Range Validation

```python
class AgeRestrictedSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'min_age', 'max_age']

    def validate_min_age(self, value):
        if value < 0:
            raise ValidationError("Minimum age cannot be negative")
        if value > 120:
            raise ValidationError("Minimum age cannot exceed 120")
        return value

    def validate_max_age(self, value):
        if value < 0:
            raise ValidationError("Maximum age cannot be negative")
        if value > 120:
            raise ValidationError("Maximum age cannot exceed 120")
        return value

    def validate(self, data):
        if data.get('max_age', 0) < data.get('min_age', 0):
            raise ValidationError("Maximum age must be greater than minimum age")
        return data
```

### Example 2: Format Validation

```python
import re

class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone', 'email', 'website']

    def validate_phone(self, value):
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        if not re.match(pattern, value):
            raise ValidationError("Invalid phone number format")
        return value

    def validate_website(self, value):
        """Validate URL format."""
        if value and not value.startswith(('http://', 'https://')):
            raise ValidationError("Website must start with http:// or https://")
        return value
```

### Example 3: Value Transformation

Validators can also transform values:

```python
class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price']

    def validate_name(self, value):
        """Normalize product name to title case."""
        return value.strip().title()

    def validate_description(self, value):
        """Remove extra whitespace from description."""
        return ' '.join(value.split())

    def validate_price(self, value):
        """Round price to 2 decimal places."""
        return round(value, 2)
```

### Example 4: Conditional Validation

```python
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'department']

    def validate_department(self, value):
        """Department is required for employees."""
        # Note: This would need access to role, better done in validate()
        return value

    def validate(self, data):
        """Validate based on user role."""
        role = data.get('role')

        if role == 'employee' and not data.get('department'):
            raise ValidationError("Employees must have a department")

        if role == 'admin' and not data.get('email'):
            raise ValidationError("Admin users must have an email")

        return data
```

### Example 5: Uniqueness Check

```python
class UsernameSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

    def validate_username(self, value):
        """Ensure username doesn't contain invalid characters."""
        if not value.replace('_', '').replace('-', '').isalnum():
            raise ValidationError(
                "Username can only contain letters, numbers, hyphens, and underscores"
            )

        # Username length check
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters")
        if len(value) > 30:
            raise ValidationError("Username cannot exceed 30 characters")

        return value.lower()  # Normalize to lowercase
```

## Complete API Usage Example

Here's a complete example showing validation in a real API:

```python
from django_bolt import BoltAPI, ModelViewSet
from django_bolt.serializers import ModelSerializer, ValidationError
from myapp.models import Product

api = BoltAPI()

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'is_active']
        read_only_fields = ['id']

    def validate_price(self, value):
        if value <= 0:
            raise ValidationError("Price must be positive")
        if value > 100000:
            raise ValidationError("Price cannot exceed $100,000")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise ValidationError("Stock cannot be negative")
        return value

    def validate_name(self, value):
        # Normalize and validate
        value = value.strip()
        if len(value) < 3:
            raise ValidationError("Name must be at least 3 characters")
        return value.title()

    def validate(self, data):
        # Can't have active products with no stock
        if data.get('is_active') and data.get('stock', 0) == 0:
            raise ValidationError("Active products must have stock")
        return data

@api.viewset("/products")
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # All CRUD operations automatically use validation!
    # - GET /products (list with validation)
    # - POST /products (create with validation)
    # - GET /products/{id} (retrieve with validation)
    # - PUT /products/{id} (update with validation)
    # - PATCH /products/{id} (partial update with validation)
    # - DELETE /products/{id} (delete)

# Or use in function-based views:
@api.post("/products/create")
async def create_product(request):
    try:
        # Decode and validate request body
        product_data = ProductSerializer.decode(request['body'])

        # Create product (data is already validated and transformed)
        product = await Product.objects.acreate(
            name=product_data.name,
            price=product_data.price,
            stock=product_data.stock,
            is_active=product_data.is_active
        )

        # Return validated response
        return ProductSerializer.from_model(product)

    except ValidationError as e:
        # ValidationError is automatically handled by django-bolt
        # Returns 400 Bad Request with error details
        raise
```

## ValidationError Format

The `ValidationError` exception accepts three formats:

### String Message
```python
raise ValidationError("Simple error message")
# Returns: {"detail": "Simple error message"}
```

### Dictionary (Field Errors)
```python
raise ValidationError({
    "email": "Invalid email format",
    "age": "Must be 18 or older"
})
# Returns: {"email": "Invalid email format", "age": "Must be 18 or older"}
```

### List (Multiple Errors)
```python
raise ValidationError([
    "Error 1",
    "Error 2"
])
# Returns: {"detail": ["Error 1", "Error 2"]}
```

## How Validation Works

1. **Field Validators Run First**: Each field with a `validate_<fieldname>` method is validated
2. **Object Validator Runs Last**: The `validate()` method runs after all field validators pass
3. **Transformation Applied**: Validated/transformed values are used to create the struct
4. **Errors Propagate**: ValidationError exceptions stop processing and return to the caller

## Performance Considerations

- **Minimal Overhead**: Validation only runs when data needs to be validated
- **Skip When Needed**: Use `validate=False` for trusted data sources
- **Efficient**: Validation runs before struct creation, not on every field access
- **Msgspec Speed**: Still benefits from msgspec's fast JSON parsing

## Comparison with DRF

### Django REST Framework
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'age']

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("Must be 18+")
        return value

    def validate(self, data):
        # object validation
        return data
```

### Django-Bolt (Same API!)
```python
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'age']

    def validate_age(self, value):
        if value < 18:
            raise ValidationError("Must be 18+")
        return value

    def validate(self, data):
        # object validation
        return data
```

The API is nearly identical - just import from `django_bolt.serializers` instead!

## Best Practices

1. **Keep validators simple** - Each validator should do one thing
2. **Use field validators for single-field checks** - min/max, format, etc.
3. **Use object validator for cross-field checks** - relationships between fields
4. **Transform early** - Normalize values in field validators
5. **Provide clear error messages** - Users need to understand what's wrong
6. **Use validate=False for trusted data** - Skip validation when reading from DB

## Limitations & Future Features

### Current Limitations
- Validators must be synchronous (no `async def validate_*`)
- No built-in validators library yet (coming soon)
- No field-level `required` override (use Meta.read_only_fields)

### Coming Soon
- Async validator support
- Built-in validators (EmailValidator, URLValidator, RegexValidator, etc.)
- Custom error codes
- Nested serializer validation
- Source field mapping with validation

## Error Handling Integration

Django-Bolt automatically handles `ValidationError` exceptions in your API endpoints and returns appropriate HTTP responses:

```python
@api.post("/users")
async def create_user(request):
    try:
        user_data = UserSerializer.decode(request['body'])
        # ... create user
    except ValidationError as e:
        # Automatically returns 400 Bad Request with error details
        raise  # Let django-bolt handle it

# Client receives:
# HTTP 400 Bad Request
# {"detail": "Must be 18 or older"}
```

## Migration from Manual Validation

### Before (Manual Validation)
```python
@api.post("/users")
async def create_user(request):
    data = msgspec.json.decode(request['body'])

    # Manual validation
    if data['age'] < 18:
        raise HTTPException(400, "Must be 18 or older")

    if not data['email'].endswith('@company.com'):
        raise HTTPException(400, "Must use company email")

    user = await User.objects.acreate(**data)
    return UserSchema.from_model(user)
```

### After (With Validators)
```python
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age']

    def validate_age(self, value):
        if value < 18:
            raise ValidationError("Must be 18 or older")
        return value

    def validate_email(self, value):
        if not value.endswith('@company.com'):
            raise ValidationError("Must use company email")
        return value

@api.post("/users")
async def create_user(request):
    # Validation happens automatically
    user_data = UserSerializer.decode(request['body'])

    user = await User.objects.acreate(**msgspec.structs.asdict(user_data))
    return UserSerializer.from_model(user)
```

Much cleaner and more maintainable!

## Contributing

Found a bug or want a feature? Open an issue on [GitHub](https://github.com/yourusername/django-bolt)!
