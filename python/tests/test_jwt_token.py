"""
Test JWT Token class for Django-Bolt.

Tests the Token dataclass for encoding/decoding JWTs with performance focus.
"""
from datetime import UTC, datetime, timedelta

import jwt as pyjwt
import pytest

from django_bolt.auth import Token


class TestTokenCreation:
    """Test Token creation and validation"""

    def test_create_basic_token(self):
        """Test creating a basic token"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
        )

        assert token.sub == "user123"
        assert token.exp == exp.replace(microsecond=0)  # Microseconds stripped
        assert token.iat <= datetime.now(UTC)

    def test_create_token_with_staff_flags(self):
        """Test creating token with staff/admin flags"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="admin123",
            exp=exp,
            is_staff=True,
            is_admin=True,
        )

        assert token.is_staff is True
        assert token.is_admin is True

    def test_create_token_with_permissions(self):
        """Test creating token with permissions list"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
            permissions=["users.view", "users.create", "posts.edit"],
        )

        assert len(token.permissions) == 3
        assert "users.view" in token.permissions

    def test_create_token_with_audience_issuer(self):
        """Test creating token with aud and iss claims"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
            aud="my-api",
            iss="auth-service",
        )

        assert token.aud == "my-api"
        assert token.iss == "auth-service"

    def test_create_token_with_extras(self):
        """Test creating token with custom extra claims"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
            extras={
                "tenant_id": "acme-corp",
                "role": "manager",
                "department": "engineering",
            }
        )

        assert token.extras["tenant_id"] == "acme-corp"
        assert token.extras["role"] == "manager"

    def test_create_factory_method(self):
        """Test Token.create() factory method"""
        token = Token.create(
            sub="user123",
            expires_delta=timedelta(minutes=30),
            issuer="my-service",
            is_staff=True,
            permissions=["read", "write"],
            tenant="acme",
        )

        assert token.sub == "user123"
        assert token.iss == "my-service"
        assert token.is_staff is True
        assert token.permissions == ["read", "write"]
        assert token.extras["tenant"] == "acme"

        # Check expiration is ~30 minutes from now
        now = datetime.now(UTC)
        exp_delta = (token.exp - now).total_seconds()
        assert 1790 < exp_delta < 1810  # ~30 minutes with some tolerance


class TestTokenValidation:
    """Test Token validation logic"""

    def test_empty_subject_raises_error(self):
        """Test that empty subject raises ValueError"""
        exp = datetime.now(UTC) + timedelta(hours=1)

        with pytest.raises(ValueError, match="sub.*must be.*non-empty"):
            Token(sub="", exp=exp)

    def test_past_expiration_raises_error(self):
        """Test that past expiration raises ValueError"""
        exp = datetime.now(UTC) - timedelta(hours=1)

        with pytest.raises(ValueError, match="exp.*must be in the future"):
            Token(sub="user123", exp=exp)

    def test_future_iat_raises_error(self):
        """Test that future iat raises ValueError"""
        exp = datetime.now(UTC) + timedelta(hours=2)
        iat = datetime.now(UTC) + timedelta(hours=1)

        with pytest.raises(ValueError, match="iat.*must be current or past"):
            Token(sub="user123", exp=exp, iat=iat)

    def test_datetime_normalization(self):
        """Test that datetimes are normalized to UTC without microseconds"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        exp_with_micros = exp.replace(microsecond=123456)

        token = Token(sub="user123", exp=exp_with_micros)

        # Should have microseconds stripped
        assert token.exp.microsecond == 0
        assert token.iat.microsecond == 0


class TestTokenEncoding:
    """Test Token encoding to JWT strings"""

    def test_encode_basic_token(self):
        """Test encoding a basic token"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(sub="user123", exp=exp)

        secret = "test-secret"
        encoded = token.encode(secret=secret)

        # Should be a valid JWT string (3 parts separated by dots)
        assert isinstance(encoded, str)
        parts = encoded.split('.')
        assert len(parts) == 3

        # Decode to verify contents
        decoded = pyjwt.decode(encoded, secret, algorithms=["HS256"])
        assert decoded["sub"] == "user123"
        assert "exp" in decoded
        assert "iat" in decoded

    def test_encode_with_claims(self):
        """Test encoding token with all claims"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
            is_staff=True,
            is_admin=False,
            permissions=["read", "write"],
            aud="my-api",
            iss="auth-service",
        )

        secret = "test-secret"
        encoded = token.encode(secret=secret)

        decoded = pyjwt.decode(
            encoded,
            secret,
            algorithms=["HS256"],
            audience="my-api",
            issuer="auth-service"
        )

        assert decoded["sub"] == "user123"
        assert decoded["is_staff"] is True
        assert decoded["is_admin"] is False
        assert decoded["permissions"] == ["read", "write"]
        assert decoded["aud"] == "my-api"
        assert decoded["iss"] == "auth-service"

    def test_encode_with_different_algorithms(self):
        """Test encoding with different algorithms"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(sub="user123", exp=exp)

        for algorithm in ["HS256", "HS384", "HS512"]:
            secret = "test-secret-for-" + algorithm
            encoded = token.encode(secret=secret, algorithm=algorithm)

            decoded = pyjwt.decode(encoded, secret, algorithms=[algorithm])
            assert decoded["sub"] == "user123"

    def test_encode_with_custom_headers(self):
        """Test encoding with custom JWT headers"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(sub="user123", exp=exp)

        secret = "test-secret"
        headers = {"kid": "key-id-123", "typ": "JWT"}
        encoded = token.encode(secret=secret, headers=headers)

        # Decode without verification to check headers
        unverified = pyjwt.get_unverified_header(encoded)
        assert unverified["kid"] == "key-id-123"


class TestTokenDecoding:
    """Test Token decoding from JWT strings"""

    def test_decode_basic_token(self):
        """Test decoding a basic token"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        original = Token(sub="user123", exp=exp)

        secret = "test-secret"
        encoded = original.encode(secret=secret)

        # Decode back
        decoded = Token.decode(encoded, secret=secret)

        assert decoded.sub == "user123"
        assert decoded.exp.timestamp() == pytest.approx(original.exp.timestamp(), abs=1)
        assert decoded.iat.timestamp() == pytest.approx(original.iat.timestamp(), abs=1)

    def test_decode_with_all_claims(self):
        """Test decoding token with all claims"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        original = Token(
            sub="admin123",
            exp=exp,
            is_staff=True,
            is_admin=True,
            permissions=["full-access"],
            aud="my-api",
            iss="auth-service",
            jti="unique-id-123",
        )

        secret = "test-secret"
        encoded = original.encode(secret=secret)

        decoded = Token.decode(
            encoded,
            secret=secret,
            audience="my-api",
            issuer="auth-service"
        )

        assert decoded.sub == "admin123"
        assert decoded.is_staff is True
        assert decoded.is_admin is True
        assert decoded.permissions == ["full-access"]
        assert decoded.aud == "my-api"
        assert decoded.iss == "auth-service"
        assert decoded.jti == "unique-id-123"

    def test_decode_with_extras(self):
        """Test decoding token with extra claims"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        original = Token(
            sub="user123",
            exp=exp,
            extras={"tenant": "acme", "role": "admin", "level": 5}
        )

        secret = "test-secret"
        encoded = original.encode(secret=secret)

        decoded = Token.decode(encoded, secret=secret)

        assert decoded.extras["tenant"] == "acme"
        assert decoded.extras["role"] == "admin"
        assert decoded.extras["level"] == 5

    def test_decode_expired_token_raises_error(self):
        """Test that decoding expired token raises ValueError"""
        # Create token that will be expired
        payload = {
            "sub": "user123",
            "exp": int((datetime.now(UTC) - timedelta(hours=1)).timestamp()),
            "iat": int((datetime.now(UTC) - timedelta(hours=2)).timestamp()),
        }

        secret = "test-secret"
        encoded = pyjwt.encode(payload, secret, algorithm="HS256")

        with pytest.raises(ValueError, match="Failed to decode token"):
            Token.decode(encoded, secret=secret)

    def test_decode_with_wrong_secret_raises_error(self):
        """Test that decoding with wrong secret raises ValueError"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(sub="user123", exp=exp)

        encoded = token.encode(secret="secret1")

        with pytest.raises(ValueError, match="Failed to decode token"):
            Token.decode(encoded, secret="wrong-secret")

    def test_decode_with_audience_mismatch_raises_error(self):
        """Test that audience mismatch raises ValueError"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(sub="user123", exp=exp, aud="api1")

        secret = "test-secret"
        encoded = token.encode(secret=secret)

        with pytest.raises(ValueError, match="Failed to decode token"):
            Token.decode(encoded, secret=secret, audience="wrong-audience")

    def test_decode_skip_expiry_verification(self):
        """Test decoding with expiry verification disabled"""
        # Create expired token
        payload = {
            "sub": "user123",
            "exp": int((datetime.now(UTC) - timedelta(hours=1)).timestamp()),
            "iat": int((datetime.now(UTC) - timedelta(hours=2)).timestamp()),
        }

        secret = "test-secret"
        encoded = pyjwt.encode(payload, secret, algorithm="HS256")

        # Should succeed with verify_exp=False
        decoded = Token.decode(encoded, secret=secret, verify_exp=False)
        assert decoded.sub == "user123"


class TestTokenToDictConversion:
    """Test Token.to_dict() conversion"""

    def test_to_dict_basic(self):
        """Test converting token to dict"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(sub="user123", exp=exp)

        d = token.to_dict()

        assert d["sub"] == "user123"
        assert isinstance(d["exp"], int)  # Unix timestamp
        assert isinstance(d["iat"], int)
        assert d["exp"] > d["iat"]

    def test_to_dict_with_optional_fields(self):
        """Test to_dict with optional fields"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
            aud="my-api",
            iss="auth",
            jti="unique",
            is_staff=True,
        )

        d = token.to_dict()

        assert d["aud"] == "my-api"
        assert d["iss"] == "auth"
        assert d["jti"] == "unique"
        assert d["is_staff"] is True

    def test_to_dict_excludes_none_values(self):
        """Test that None values are excluded from dict"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
            aud=None,
            iss=None,
        )

        d = token.to_dict()

        assert "aud" not in d
        assert "iss" not in d

    def test_to_dict_includes_extras(self):
        """Test that extras are included in dict"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(
            sub="user123",
            exp=exp,
            extras={"custom1": "value1", "custom2": 42}
        )

        d = token.to_dict()

        assert d["custom1"] == "value1"
        assert d["custom2"] == 42


class TestTokenRoundTrip:
    """Test encoding and decoding round-trip"""

    def test_round_trip_preserves_data(self):
        """Test that encode->decode preserves all data"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        original = Token(
            sub="user123",
            exp=exp,
            is_staff=True,
            is_admin=False,
            permissions=["read", "write", "delete"],
            aud="my-api",
            iss="auth-service",
            extras={"tenant": "acme", "role": "manager"}
        )

        secret = "test-secret"
        encoded = original.encode(secret=secret)
        decoded = Token.decode(
            encoded,
            secret=secret,
            audience="my-api",
            issuer="auth-service"
        )

        # Compare all fields (timestamps may differ slightly due to rounding)
        assert decoded.sub == original.sub
        assert decoded.exp.timestamp() == pytest.approx(original.exp.timestamp(), abs=1)
        assert decoded.is_staff == original.is_staff
        assert decoded.is_admin == original.is_admin
        assert decoded.permissions == original.permissions
        assert decoded.aud == original.aud
        assert decoded.iss == original.iss
        assert decoded.extras == original.extras

    def test_multiple_round_trips(self):
        """Test multiple encode/decode cycles"""
        exp = datetime.now(UTC) + timedelta(hours=1)
        token = Token(sub="user123", exp=exp, is_staff=True)

        secret = "test-secret"

        # Multiple round trips
        for _ in range(3):
            encoded = token.encode(secret=secret)
            token = Token.decode(encoded, secret=secret)

            assert token.sub == "user123"
            assert token.is_staff is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
