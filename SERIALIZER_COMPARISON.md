# Django-Bolt Serializer Feature Comparison

This document compares django-bolt's serializer features with Pydantic v2 and Django REST Framework (DRF) serializers.

---

## Executive Summary

**Django-Bolt's Positioning:**
- Built on **msgspec** (5-10x faster than stdlib JSON, comparable to Pydantic v2 Rust core)
- Provides a **hybrid approach**: DRF-like API with Pydantic-like performance
- Focused on **performance-critical paths**: validation runs in C (msgspec), auth/routing in Rust
- **Selective feature set**: Implements most common use cases, omits complex edge cases

**Performance Comparison:**
- **Django-Bolt**: msgspec-based, 5-10x faster than stdlib, thread-local caching
- **Pydantic v2**: Rust-based core, 5-50x faster than Pydantic v1
- **DRF**: Pure Python, slowest of the three but most Django-integrated

---

## Feature Matrix

### ✅ = Fully Supported | 🟡 = Partially Supported | ❌ = Not Supported

| Feature Category | Django-Bolt | Pydantic v2 | DRF |
|-----------------|-------------|-------------|-----|
| **Basic Validation** |
| Type validation | ✅ (msgspec) | ✅ (Rust core) | ✅ |
| Field validators | ✅ `@field_validator` | ✅ `@field_validator` | ✅ `validate_<field>` |
| Model validators | ✅ `@model_validator` | ✅ `@model_validator` | ✅ `validate()` |
| Custom validators | ✅ | ✅ | ✅ |
| **Declarative Constraints** |
| min/max length | ✅ (Meta) | ✅ (Field) | ✅ (field args) |
| min/max value (ge/le) | ✅ (Meta) | ✅ (Field) | ✅ (validators) |
| Regex patterns | ✅ (Meta) | ✅ (Field) | ✅ (RegexValidator) |
| Literal/Choices | ✅ (Literal type, O(1)) | ✅ (Literal) | ✅ (choices) |
| **Validation Modes** |
| Strict mode | ❌ | ✅ (Pydantic v2 major feature) | 🟡 (limited) |
| Coercion mode | ✅ (default) | ✅ | ✅ |
| Before/after validation | 🟡 (implicit) | ✅ (mode='before/after') | 🟡 |
| **Django Integration** |
| Model → Serializer | ✅ `.from_model()` | ❌ | ✅ `ModelSerializer` |
| Serializer → Model | ✅ `.to_model()` | ❌ | ✅ `.save()` |
| Update instance | ✅ `.update_instance()` | ❌ | ✅ `.save()` |
| QuerySet handling | ✅ (optimized async) | ❌ | ✅ (many=True) |
| Auto field generation | ✅ `create_serializer()` | ❌ | ✅ `ModelSerializer` |
| Django validators | ✅ | 🟡 (via adapters) | ✅ (native) |
| **Nested Serializers** |
| Basic nesting | ✅ `Nested()` | ✅ | ✅ |
| many=True | ✅ | ✅ (list[Model]) | ✅ |
| Depth control | 🟡 (Python recursion limit) | 🟡 | ✅ (depth=N) |
| Circular refs | ❌ | ✅ (forward refs) | 🟡 (limited) |
| Max items limit | ✅ (DoS protection) | ❌ | ❌ |
| **Field Configuration** |
| read_only | ❌ | ❌ (computed fields) | ✅ |
| write_only | ❌ | ❌ (exclude in dump) | ✅ |
| required/optional | ✅ (Optional[T]) | ✅ (Optional[T]) | ✅ |
| default values | ✅ (msgspec default) | ✅ (Field(default=)) | ✅ |
| source (field mapping) | ❌ | ✅ (alias) | ✅ |
| **Serialization Control** |
| Aliases (validation) | ❌ | ✅ (validation_alias) | ✅ (source) |
| Aliases (serialization) | ❌ | ✅ (serialization_alias) | ✅ (source) |
| exclude fields | ❌ | ✅ (model_dump exclude) | ✅ (fields/exclude) |
| include fields | ❌ | ✅ (model_dump include) | ✅ (fields) |
| exclude_unset | ❌ | ✅ | 🟡 |
| exclude_defaults | ✅ (omit_defaults=True) | ✅ (exclude_defaults) | 🟡 |
| exclude_none | ❌ | ✅ | 🟡 |
| by_alias | ❌ | ✅ (model_dump) | 🟡 |
| **Computed/Derived Fields** |
| Computed fields | ❌ | ✅ `@computed_field` | ✅ `SerializerMethodField` |
| Property serialization | ❌ | ✅ | ✅ |
| Cached properties | ❌ | ✅ | 🟡 |
| **Advanced Features** |
| Private attributes | ❌ | ✅ (PrivateAttr) | 🟡 |
| Generics | ❌ | ✅ (Generic[T]) | ❌ |
| Discriminated unions | ❌ | ✅ (tagged unions) | ❌ |
| Root validators | ✅ (model_validator) | ✅ | ✅ |
| Context passing | 🟡 | ✅ | ✅ |
| Custom encoders | ✅ (custom_enc_hook) | ✅ (custom serializers) | ✅ (to_representation) |
| **Performance Features** |
| Thread-local caching | ✅ | ✅ (v2) | ❌ |
| Compiled decoders | ✅ (msgspec) | ✅ (Rust) | ❌ |
| Zero-copy parsing | 🟡 | ✅ (v2) | ❌ |
| Batched validation | ✅ | ✅ | ❌ |
| **API Methods** |
| .model_validate() | ✅ | ✅ | ❌ (.is_valid()) |
| .model_validate_json() | ✅ | ✅ | ❌ |
| .model_dump() | ✅ (.to_dict()) | ✅ | ❌ (.data) |
| .model_dump_json() | ✅ (msgspec.json) | ✅ | ❌ |
| .create() | 🟡 (manual) | ❌ | ✅ |
| .update() | ✅ (.update_instance) | ❌ | ✅ |
| .save() | ❌ | ❌ | ✅ |
| **Error Handling** |
| Validation errors | ✅ | ✅ | ✅ |
| Error messages | ✅ | ✅ (detailed) | ✅ (detailed) |
| Custom error messages | 🟡 | ✅ | ✅ |
| Error location tracking | ✅ (msgspec) | ✅ | ✅ |
| **Data Types** |
| Standard types | ✅ | ✅ | ✅ |
| datetime/date/time | ✅ | ✅ | ✅ |
| UUID | ✅ | ✅ | ✅ |
| Decimal | ✅ | ✅ | ✅ |
| Path/URL | ✅ (Path) | ✅ (HttpUrl, etc.) | ✅ (URLField) |
| IPv4/IPv6 | ✅ | ✅ | ✅ |
| Email | ❌ | ✅ (EmailStr) | ✅ (EmailField) |
| Bytes/Files | ✅ | ✅ | ✅ |
| JSON | ✅ | ✅ (RawJson) | ✅ (JSONField) |
| **Schema Generation** |
| JSON Schema | ❌ | ✅ | ✅ (OpenAPI) |
| OpenAPI | ✅ (framework level) | ✅ | ✅ |
| Type hints | ✅ | ✅ | 🟡 |

---

## Detailed Feature Analysis

### 1. **Validation System**

#### **Django-Bolt** ✅ Strong
```python
class UserSerializer(Serializer):
    email: str
    age: int

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

    @model_validator
    def validate_model(cls, values):
        if values['age'] < 18:
            raise ValueError('Must be 18+')
        return values
```

**Strengths:**
- Fast (msgspec C implementation)
- Familiar API (Pydantic-like decorators)
- Batched validation (performance optimization)
- Meta constraints (min_length, max_length, pattern, ge, le)

**Missing:**
- ❌ Strict mode (no type coercion)
- ❌ Before/after mode control
- ❌ ValidationInfo context
- ❌ Field-level error customization

#### **Pydantic v2** ✅ Most Complete
```python
class UserModel(BaseModel):
    email: EmailStr
    age: int = Field(ge=18, le=120)

    @field_validator('email', mode='before')
    def validate_email(cls, v, info: ValidationInfo):
        # Access validation context
        return v.lower()

    model_config = ConfigDict(strict=True)
```

**Strengths:**
- Strict mode (v2 major feature)
- Before/after validation modes
- ValidationInfo for context
- Rich built-in types (EmailStr, HttpUrl, etc.)
- Rust-powered performance

#### **DRF** ✅ Most Django-Integrated
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'age']

    def validate_email(self, value):
        if '@' not in value:
            raise ValidationError('Invalid email')
        return value

    def validate(self, data):
        if data['age'] < 18:
            raise ValidationError('Must be 18+')
        return data
```

**Strengths:**
- Native Django integration
- Field-level validators
- Object-level validators
- Built-in model validators (unique_together, etc.)

**Weaknesses:**
- Slow (pure Python)
- Verbose API

---

### 2. **Django Model Integration**

#### **Django-Bolt** ✅ Excellent (Optimized)
```python
# Auto-generate from model
UserSerializer = create_serializer(User)

# Manual definition
class UserSerializer(Serializer):
    username: str
    email: str

# Convert model → serializer
user = await User.objects.aget(pk=1)
data = UserSerializer.from_model(user)

# Convert serializer → model
user = data.to_model(User)  # Unsaved instance
await user.asave()

# Update existing instance
data.update_instance(user)
await user.asave()

# QuerySet optimization (100-1000x fewer context switches)
users = User.objects.filter(is_active=True)
data = await sync_to_thread(list)(UserSerializer.from_model(u) for u in users.values())
```

**Strengths:**
- `.from_model()` / `.to_model()` / `.update_instance()`
- `create_serializer()` auto-generation
- QuerySet async optimization
- Familiar Pydantic-like API

**Missing:**
- ❌ No `.save()` method (must manually call `.asave()`)
- ❌ No automatic relationship handling in `.save()`
- ❌ No field source mapping

#### **Pydantic v2** ❌ No Native Support
- Requires third-party libraries (djantic, drf-pydantic)
- Not designed for Django ORM

#### **DRF** ✅ Best-in-Class
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

# Full CRUD with .save()
serializer = UserSerializer(data=request.data)
if serializer.is_valid():
    user = serializer.save()  # Automatic create/update
```

**Strengths:**
- Auto field generation from models
- `.save()` handles create/update automatically
- Nested relationship handling
- Depth control for related objects

---

### 3. **Nested Serializers**

#### **Django-Bolt** ✅ Good (with DoS protection)
```python
class ProfileSerializer(Serializer):
    bio: str
    avatar: str

class UserSerializer(Serializer):
    username: str
    profile: Nested(ProfileSerializer)  # Single object
    posts: Nested(PostSerializer, many=True, max_items=1000)  # List with limit
```

**Strengths:**
- `Nested()` helper
- `many=True` support
- `max_items` DoS protection
- Accepts dicts or Serializer instances

**Missing:**
- ❌ No circular reference support
- ❌ No depth control (only Python recursion limit ~1000)
- ❌ No lazy loading

#### **Pydantic v2** ✅ Excellent
```python
class ProfileModel(BaseModel):
    bio: str
    user: 'UserModel'  # Forward reference for circular refs

class UserModel(BaseModel):
    username: str
    profile: ProfileModel
    posts: list[PostModel]
```

**Strengths:**
- Forward references for circular deps
- Type-safe with `list[T]`
- Generic support

#### **DRF** ✅ Most Flexible
```python
class UserSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        depth = 2  # Auto-expand relationships 2 levels deep
```

**Strengths:**
- `depth` parameter
- Automatic relationship expansion
- Handles circular refs better

---

### 4. **Field-Level Control (read_only, write_only, source)**

#### **Django-Bolt** ❌ Missing
```python
# NO support for:
# - read_only fields
# - write_only fields
# - source mapping (field name != model attribute)
```

**Workaround:**
- Create separate serializers for read/write
- Use `create_serializer_set()` to generate Public/Create/Update variants

#### **Pydantic v2** 🟡 Partial
```python
class UserModel(BaseModel):
    password: str  # Included in validation

    @computed_field
    @property
    def full_name(self) -> str:  # Read-only computed
        return f"{self.first_name} {self.last_name}"

    # Exclude from serialization
    user_dict = user.model_dump(exclude={'password'})
```

**Strengths:**
- `@computed_field` for read-only
- Runtime `exclude`/`include` in `.model_dump()`
- Aliases (validation_alias, serialization_alias)

**Missing:**
- ❌ No declarative write_only

#### **DRF** ✅ Best-in-Class
```python
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()  # Read-only
    profile_bio = serializers.CharField(source='profile.bio')  # Field mapping

    class Meta:
        model = User
        fields = ['username', 'password', 'full_name', 'profile_bio']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
```

**Strengths:**
- Declarative `read_only_fields`
- `write_only` via `extra_kwargs`
- `source` for field mapping
- `SerializerMethodField` for computed fields

---

### 5. **Serialization Control (exclude, include, by_alias)**

#### **Django-Bolt** ❌ Very Limited
```python
# Only supports:
data.to_dict(omit_defaults=True)  # Exclude default values

# NO support for:
# - exclude specific fields
# - include specific fields
# - exclude_none, exclude_unset
# - field aliases
```

**Workaround:**
- Define separate serializer classes
- Manually filter dict after `.to_dict()`

#### **Pydantic v2** ✅ Excellent
```python
class UserModel(BaseModel):
    username: str
    password: str
    email: str = Field(serialization_alias='email_address')

# Runtime control
user.model_dump(
    exclude={'password'},
    include={'username', 'email'},
    exclude_unset=True,  # Only set fields
    exclude_defaults=True,  # Non-default values
    exclude_none=True,  # No None values
    by_alias=True  # Use serialization aliases
)
```

**Strengths:**
- Runtime `exclude`/`include`
- Multiple exclude modes
- Alias support (validation vs serialization)
- Nested exclude/include

#### **DRF** 🟡 Declarative Only
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']  # Include only these
        # OR
        exclude = ['password']  # Exclude these

# Limited runtime control
serializer.data  # Returns all defined fields
```

**Strengths:**
- Declarative field selection
- Clean Meta API

**Missing:**
- ❌ No runtime exclude/include
- ❌ No exclude_none, exclude_unset

---

### 6. **Computed/Derived Fields**

#### **Django-Bolt** ❌ Not Supported
```python
# NO native support for:
# - Computed fields
# - Properties in serialization
# - SerializerMethodField equivalent
```

**Workaround:**
- Add fields manually before serialization
- Use custom field validators to transform data

#### **Pydantic v2** ✅ Excellent
```python
class UserModel(BaseModel):
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field(alias='display_name')
    @cached_property
    def cached_full_name(self) -> str:
        return self.full_name.upper()
```

**Strengths:**
- `@computed_field` decorator
- Works with `@property` and `@cached_property`
- Included in serialization and schema
- Alias support

#### **DRF** ✅ Excellent
```python
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
```

**Strengths:**
- `SerializerMethodField` for custom logic
- Access to full object context
- Flexible method naming

---

### 7. **Advanced Type System**

#### **Django-Bolt** 🟡 Basic Types
**Supported:**
- Standard types (str, int, float, bool, None)
- Collections (list, dict)
- datetime, date, time
- Decimal, UUID, Path
- IPv4/IPv6 addresses
- msgspec.Struct subclasses
- Django models/QuerySets

**Missing:**
- ❌ Email validation type
- ❌ URL validation type
- ❌ Constrained types (constr, conint)
- ❌ Discriminated unions
- ❌ Generics

#### **Pydantic v2** ✅ Richest Type System
```python
from pydantic import EmailStr, HttpUrl, constr, conint
from typing import Literal, Union

class UserModel(BaseModel):
    email: EmailStr  # Built-in email validation
    website: HttpUrl  # URL validation
    username: constr(min_length=3, max_length=20)  # Constrained string
    age: conint(ge=18, le=120)  # Constrained int
    role: Literal['admin', 'user', 'guest']  # Literal type

    # Discriminated union (tagged union)
    animal: Union[Cat, Dog] = Field(discriminator='type')
```

**Strengths:**
- Rich built-in types
- Constrained types
- Discriminated unions
- Generic types
- Custom types

#### **DRF** 🟡 Django-Focused Types
**Supported:**
- Standard field types
- EmailField, URLField
- RegexField, SlugField
- FileField, ImageField
- Model relationship fields

**Missing:**
- ❌ No Literal types
- ❌ No discriminated unions
- ❌ No generics

---

### 8. **Performance Optimizations**

#### **Django-Bolt** ✅ Excellent
```python
# Thread-local cached encoders
_json.py: Thread-local encoders/decoders

# Pre-compiled extractors (route registration time)
binding.py: ExtractorConfig compiled once

# Batched validation (minimize getattr/setattr)
base.py: Single validator fast path, batched multi-validators

# QuerySet async optimization
sync_to_thread(list)(queryset.values())  # 100-1000x fewer context switches
```

**Performance Characteristics:**
- 5-10x faster than stdlib JSON (msgspec)
- Zero-allocation for common types
- Pre-computed field configurations
- Cached decoders per type
- Rust-based routing/auth/middleware

#### **Pydantic v2** ✅ Excellent
```python
# Rust core (5-50x faster than v1)
# Schema build caching (v2.11: 10x faster imports)
# Zero-copy validation

model_config = ConfigDict(
    # Performance options
    defer_build=True,  # Lazy schema building
    cache_strings=True  # String interning
)
```

**Performance Characteristics:**
- Rust-based validation core
- 5-50x faster than Pydantic v1
- 10x faster schema builds (v2.11)
- Zero-copy where possible

#### **DRF** ❌ Slowest
- Pure Python
- No caching optimizations
- No compiled validation
- Can be 5-10x slower than django-bolt/Pydantic

---

## Missing Features in Django-Bolt

### **Critical Missing Features** (High Impact)

1. **❌ read_only / write_only fields**
   - **Use Case:** Password fields, computed fields, auto-generated IDs
   - **DRF:** `read_only_fields`, `extra_kwargs={'password': {'write_only': True}}`
   - **Pydantic:** `@computed_field`, `.model_dump(exclude={'password'})`
   - **Impact:** HIGH - Common in most APIs
   - **Workaround:** Create separate serializers for read/write

2. **❌ Field source mapping**
   - **Use Case:** Map API field names to different model attributes
   - **DRF:** `field = CharField(source='model.attribute')`
   - **Pydantic:** `alias`, `validation_alias`, `serialization_alias`
   - **Impact:** HIGH - Required for API versioning, legacy compatibility
   - **Workaround:** None - must match field names exactly

3. **❌ Runtime exclude/include fields**
   - **Use Case:** Different field sets for different contexts (public vs admin)
   - **DRF:** Declarative via `fields`/`exclude` in Meta
   - **Pydantic:** `.model_dump(exclude={...}, include={...})`
   - **Impact:** MEDIUM - Can use separate serializers
   - **Workaround:** Define multiple serializer classes

4. **❌ Computed/derived fields**
   - **Use Case:** Full name, formatted dates, derived calculations
   - **DRF:** `SerializerMethodField`
   - **Pydantic:** `@computed_field`
   - **Impact:** HIGH - Very common pattern
   - **Workaround:** Add fields manually before serialization

5. **❌ Strict mode (no coercion)**
   - **Use Case:** API contracts requiring exact types
   - **Pydantic v2:** `model_config = ConfigDict(strict=True)`
   - **Impact:** MEDIUM - Important for strict APIs
   - **Workaround:** Custom validators

### **Important Missing Features** (Medium Impact)

6. **❌ exclude_none / exclude_unset / exclude_defaults options**
   - **Use Case:** Partial updates, sparse fieldsets
   - **Pydantic:** `.model_dump(exclude_none=True, exclude_unset=True)`
   - **Impact:** MEDIUM - Common in PATCH endpoints
   - **Workaround:** `omit_defaults=True` covers some cases

7. **❌ Before/after validation modes**
   - **Use Case:** Pre-process input before validation
   - **Pydantic:** `@field_validator(mode='before')`
   - **Impact:** MEDIUM - Useful for data transformation
   - **Workaround:** Custom validators

8. **❌ Circular nested serializer support**
   - **Use Case:** User → Profile → User relationships
   - **Pydantic:** Forward references
   - **Impact:** MEDIUM - Can design around it
   - **Workaround:** Use ID-only fields for reverse relationships

9. **❌ Rich built-in types (Email, URL, etc.)**
   - **Use Case:** Common validation patterns
   - **Pydantic:** `EmailStr`, `HttpUrl`, `constr`, etc.
   - **Impact:** MEDIUM - Can write custom validators
   - **Workaround:** Custom field validators with regex

10. **❌ Discriminated unions (tagged unions)**
    - **Use Case:** Polymorphic types (e.g., different event types)
    - **Pydantic v2:** `Field(discriminator='type')`
    - **Impact:** LOW - Niche use case
    - **Workaround:** Manual validation in `@model_validator`

### **Nice-to-Have Features** (Low Impact)

11. **❌ Generics support**
    - **Use Case:** Reusable paginated response types
    - **Pydantic:** `class Response(BaseModel, Generic[T])`
    - **Impact:** LOW - Can define concrete classes

12. **❌ Private attributes**
    - **Use Case:** Internal state not serialized
    - **Pydantic:** `PrivateAttr`
    - **Impact:** LOW - Can use instance variables

13. **❌ Custom field aliases**
    - **Use Case:** camelCase API with snake_case Python
    - **Pydantic:** `alias='firstName'`, `by_alias=True`
    - **Impact:** LOW - Can manually transform

14. **❌ Depth control for nested serializers**
    - **Use Case:** Auto-expand relationships N levels deep
    - **DRF:** `Meta: depth = 2`
    - **Impact:** LOW - Can define explicit nesting

15. **❌ Context passing to validators**
    - **Use Case:** Access request, user, etc. in validation
    - **Pydantic:** `ValidationInfo.context`
    - **DRF:** `self.context['request']`
    - **Impact:** MEDIUM - Can pass as dependency injection
    - **Workaround:** Use `Depends()` for request context

---

## Recommendations for Django-Bolt

### **Priority 1: Critical Features** (Implement First)

1. **read_only / write_only fields**
   ```python
   class UserSerializer(Serializer):
       id: int = Field(read_only=True)
       password: str = Field(write_only=True)
       full_name: str = Field(read_only=True, computed=True)
   ```

2. **Computed fields (SerializerMethodField equivalent)**
   ```python
   class UserSerializer(Serializer):
       username: str

       @computed_field
       def full_name(self) -> str:
           return f"{self.first_name} {self.last_name}"
   ```

3. **Field source mapping**
   ```python
   class UserSerializer(Serializer):
       email_address: str = Field(source='email')
       user_bio: str = Field(source='profile.bio')
   ```

4. **exclude_none / exclude_unset support**
   ```python
   data.to_dict(exclude_none=True, exclude_unset=True)
   ```

### **Priority 2: Important Enhancements** (Next Phase)

5. **Runtime exclude/include**
   ```python
   data.to_dict(exclude={'password'}, include={'username', 'email'})
   ```

6. **Strict validation mode**
   ```python
   class UserSerializer(Serializer, strict=True):
       age: int  # "18" string would fail, must be int
   ```

7. **Before/after validation modes**
   ```python
   @field_validator('email', mode='before')
   def lowercase_email(cls, v):
       return v.lower()
   ```

8. **Rich built-in types**
   ```python
   from django_bolt import EmailStr, HttpUrl

   class UserSerializer(Serializer):
       email: EmailStr
       website: HttpUrl
   ```

### **Priority 3: Advanced Features** (Future)

9. **Discriminated unions**
10. **Circular nested serializer support**
11. **Generics**
12. **Context passing to validators**

---

## Conclusion

### **Django-Bolt's Current Position:**

**Strengths:**
- ✅ **Performance**: msgspec-based, comparable to Pydantic v2
- ✅ **Django Integration**: Better than Pydantic, simpler than DRF
- ✅ **Developer Experience**: Pydantic-like API, type-safe
- ✅ **Core Validation**: Comprehensive field/model validators
- ✅ **Production-Ready**: Handles most common use cases

**Gaps:**
- ❌ **Field-Level Control**: Missing read_only, write_only, source
- ❌ **Computed Fields**: No equivalent to SerializerMethodField
- ❌ **Serialization Control**: Limited exclude/include options
- ❌ **Type System**: Missing Email, URL, constrained types

### **Strategic Direction:**

1. **Implement Critical Features (Priority 1)** - read_only/write_only, computed fields, source mapping
2. **Maintain Performance Advantage** - Don't sacrifice speed for features
3. **Stay True to Design Philosophy** - Explicit over implicit, simple over complex
4. **Focus on Common Use Cases** - 80/20 rule - cover 80% of needs well

### **Feature Implementation Approach:**

- **Keep msgspec core** - Don't switch to pure Python
- **Compile-time optimization** - Pre-compute configurations at route registration
- **Optional complexity** - Advanced features should be opt-in
- **Zero GIL overhead** - Keep performance-critical paths in Rust/C

Django-Bolt currently provides a **strong foundation** with excellent performance and good Django integration. Adding Priority 1 features would make it competitive with DRF for most use cases while maintaining the performance advantage.
