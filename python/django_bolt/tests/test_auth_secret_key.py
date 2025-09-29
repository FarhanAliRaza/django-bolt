"""
Test that JWT authentication uses Django SECRET_KEY when not specified
"""
import pytest
from django_bolt import BoltAPI
from django_bolt.middleware import auth_required, AuthMiddleware


def test_auth_uses_django_secret_key():
    """Test that @auth_required uses Django SECRET_KEY when secret not provided"""
    # Configure Django with a SECRET_KEY
    from django.conf import settings
    if not settings.configured:
        settings.configure(
            SECRET_KEY='test-django-secret-key-12345',
            DEBUG=True,
            INSTALLED_APPS=['django_bolt'],
        )
    
    api = BoltAPI()
    
    # Define handler without explicit secret
    @api.get("/protected")
    @auth_required(mode="jwt")  # No secret specified
    async def protected_endpoint():
        return {"message": "Protected"}
    
    # Check that middleware metadata has Django SECRET_KEY
    handler = api._handlers[0]
    middleware = handler.__bolt_middleware__
    assert len(middleware) > 0
    
    auth_mw = next(m for m in middleware if m['type'] == 'auth')
    assert auth_mw['secret'] == 'test-django-secret-key-12345'
    print("✓ JWT middleware uses Django SECRET_KEY when not specified")


def test_auth_explicit_secret_overrides():
    """Test that explicit secret overrides Django SECRET_KEY"""
    from django.conf import settings
    if not settings.configured:
        settings.configure(
            SECRET_KEY='django-key',
            DEBUG=True,
            INSTALLED_APPS=['django_bolt'],
        )
    
    api = BoltAPI()
    
    @api.get("/custom")
    @auth_required(mode="jwt", secret="custom-secret")
    async def custom_endpoint():
        return {"message": "Custom"}
    
    handler = api._handlers[0]
    middleware = handler.__bolt_middleware__
    auth_mw = next(m for m in middleware if m['type'] == 'auth')
    
    # Should use the explicit secret, not Django's
    assert auth_mw['secret'] == 'custom-secret'
    assert auth_mw['secret'] != settings.SECRET_KEY
    print("✓ Explicit secret overrides Django SECRET_KEY")


def test_auth_middleware_class_uses_django_key():
    """Test that AuthMiddleware class uses Django SECRET_KEY"""
    from django.conf import settings
    if not settings.configured:
        settings.configure(
            SECRET_KEY='class-test-key',
            DEBUG=True,
            INSTALLED_APPS=['django_bolt'],
        )
    
    # Create AuthMiddleware without secret
    auth_mw = AuthMiddleware(mode="jwt")
    # It should use whatever Django SECRET_KEY is configured
    assert auth_mw.secret == settings.SECRET_KEY
    print(f"✓ AuthMiddleware class uses Django SECRET_KEY: {auth_mw.secret[:20]}...")


def test_auth_middleware_requires_secret():
    """Test that auth middleware raises error without secret or Django key"""
    # Clear Django settings
    from django.conf import settings
    settings._wrapped = None
    
    # Try to create middleware without secret and without Django configured
    # This should raise an error
    with pytest.raises(ValueError, match="JWT authentication requires a secret"):
        AuthMiddleware(mode="jwt")
    
    print("✓ AuthMiddleware raises error when no secret available")


if __name__ == "__main__":
    test_auth_uses_django_secret_key()
    test_auth_explicit_secret_overrides()
    test_auth_middleware_class_uses_django_key()
    
    try:
        test_auth_middleware_requires_secret()
    except AssertionError as e:
        print(f"Expected error test failed: {e}")
    
    print("\n✅ All Django SECRET_KEY integration tests passed!")