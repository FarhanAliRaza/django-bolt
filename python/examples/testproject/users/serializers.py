"""
User serializers using django-bolt's ModelSerializer.

This file demonstrates how to use ModelSerializer to automatically
generate msgspec.Struct classes from Django models.

These serializers replace the manual msgspec.Struct definitions
in api.py with automatically generated ones.
"""

from django_bolt.serializers import ModelSerializer
from .models import User


class UserFullSerializer(ModelSerializer):
    """
    Full user serializer with all fields.

    Automatically generates msgspec.Struct with:
    - id: int
    - username: str
    - email: str
    - first_name: str
    - last_name: str
    - is_active: bool
    - created_at: datetime
    """
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class UserMiniSerializer(ModelSerializer):
    """
    Minimal user serializer with just id and username.

    Perfect for list endpoints where you don't need all user data.
    """
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id']


class UserCreateSerializer(ModelSerializer):
    """
    Serializer for creating new users.

    Excludes auto-generated fields (id, created_at).
    """
    class Meta:
        model = User
        exclude = ['id', 'created_at']


class UserUpdateSerializer(ModelSerializer):
    """
    Serializer for updating users.

    All fields are optional for PATCH requests.
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_active']


# Alternative: You can also create serializers dynamically
from django_bolt.serializers import create_serializer

# Create a serializer on-the-fly
UserListSerializer = create_serializer(
    User,
    fields=['id', 'username', 'email', 'is_active'],
    read_only_fields=['id'],
    name='UserListSerializer'
)


# Usage examples in comments:
"""
# In your API endpoints:

from .serializers import UserFullSerializer, UserMiniSerializer

@api.get("/users/{id}")
async def get_user(id: int):
    user = await User.objects.aget(id=id)
    return UserFullSerializer.from_model(user)

@api.get("/users")
async def list_users():
    users = User.objects.all()[:10]
    return UserMiniSerializer.from_models(users)

# Or with ModelViewSet:

@api.viewset("/users")
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserFullSerializer
    list_serializer_class = UserMiniSerializer

    # All CRUD operations automatically use the serializers!
"""
