"""
Test that JWT authentication uses Django SECRET_KEY when not specified
"""
import pytest
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication
from django_bolt.permissions import IsAuthenticated


def test_jwt_auth_uses_django_secret_key():
    """Test that JWTAuthentication uses Django SECRET_KEY when secret not provided"""
    # Configure Django with a SECRET_KEY
    from django.conf import settings
    settings.configure(
        SECRET_KEY='test-django-secret-key-12345',
        DEBUG=True,
        INSTALLED_APPS=['django_bolt'],
    )

    # Create JWT auth without explicit secret
    auth = JWTAuthentication()  # No secret specified

    # Should use Django's SECRET_KEY
    assert auth.secret == 'test-django-secret-key-12345'
    print("✓ JWTAuthentication uses Django SECRET_KEY when not specified")


def test_jwt_auth_explicit_secret_overrides():
    """Test that explicit secret overrides Django SECRET_KEY"""
    from django.conf import settings
    settings.configure(
        SECRET_KEY='django-key',
        DEBUG=True,
        INSTALLED_APPS=['django_bolt'],
    )

    # Create with explicit secret
    auth = JWTAuthentication(secret="custom-secret")

    # Should use the explicit secret, not Django's
    assert auth.secret == 'custom-secret'
    assert auth.secret != settings.SECRET_KEY
    print("✓ Explicit secret overrides Django SECRET_KEY")


def test_route_with_django_secret():
    """Test that route-level auth uses Django SECRET_KEY"""
    from django.conf import settings
    settings.configure(
        SECRET_KEY='route-test-key',
        DEBUG=True,
        INSTALLED_APPS=['django_bolt'],
    )

    api = BoltAPI()

    @api.get(
        "/protected",
        auth=[JWTAuthentication()],  # No secret - should use Django's
        guards=[IsAuthenticated()]
    )
    async def protected_endpoint():
        return {"message": "Protected"}

    # Check that metadata has Django SECRET_KEY
    handler_id = 0
    if handler_id in api._handler_middleware:
        metadata = api._handler_middleware[handler_id]
        auth_backends = metadata.get('auth_backends', [])
        assert len(auth_backends) > 0
        assert auth_backends[0]['secret'] == 'route-test-key'
        print("✓ Route-level JWT auth uses Django SECRET_KEY")


def test_global_auth_with_django_secret():
    """Test global auth configuration with Django SECRET_KEY"""
    from django.conf import settings
    import django

    # Configure settings first, then create auth instance
    settings.configure(
        SECRET_KEY='global-test-key',
        DEBUG=True,
        INSTALLED_APPS=['django_bolt'],
        BOLT_AUTHENTICATION_CLASSES=[],  # Will be set after
        BOLT_DEFAULT_PERMISSION_CLASSES=[IsAuthenticated()],
    )

    # Now set auth classes after settings are configured
    settings.BOLT_AUTHENTICATION_CLASSES = [
        JWTAuthentication()  # No secret - should use Django's
    ]

    django.setup()

    from django_bolt.auth import get_default_authentication_classes

    auth_classes = get_default_authentication_classes()
    assert len(auth_classes) > 0
    assert auth_classes[0].secret == 'global-test-key'
    print("✓ Global auth configuration uses Django SECRET_KEY")


if __name__ == "__main__":
    test_jwt_auth_uses_django_secret_key()
    test_jwt_auth_explicit_secret_overrides()
    test_route_with_django_secret()
    test_global_auth_with_django_secret()

    print("\n✅ All Django SECRET_KEY integration tests passed!")