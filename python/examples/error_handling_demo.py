"""Demo of Django-Bolt error handling and logging features.

This example shows how to use:
- Enhanced exception system
- Error handlers
- Logging middleware
- Health checks
"""

from django_bolt import BoltAPI
from django_bolt.exceptions import (
    HTTPException,
    NotFound,
    BadRequest,
    Unauthorized,
    InternalServerError,
    RequestValidationError,
)
from django_bolt.logging import LoggingConfig, create_logging_middleware
from django_bolt.health import register_health_checks, add_health_check
import msgspec


# Create API instance
api = BoltAPI()

# Configure logging (integrates with Django's settings.DEBUG)
logging_config = LoggingConfig(
    request_log_fields={"method", "path", "client_ip", "user_agent"},
    response_log_fields={"status_code", "duration"},
    obfuscate_headers={"authorization", "cookie", "x-api-key"},
    skip_paths={"/health", "/ready"},  # Don't log health checks
)

# Create logging middleware
logging_middleware = create_logging_middleware(
    log_level="INFO",  # Will use Django's DEBUG setting if not specified
)


# Example 1: Basic HTTP exceptions
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    """Endpoint that demonstrates error handling."""
    if user_id == 0:
        raise NotFound(detail="User not found")
    elif user_id < 0:
        raise BadRequest(detail="Invalid user ID")
    elif user_id == 999:
        # Unauthorized with extra data
        raise Unauthorized(
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"user_id": user_id, "name": f"User {user_id}"}


# Example 2: Validation errors
class CreateUserRequest(msgspec.Struct):
    username: str
    email: str
    age: int


@api.post("/users")
async def create_user(user: CreateUserRequest):
    """Endpoint with request validation.

    If validation fails, a 422 response with field-level errors is returned.
    """
    if user.age < 0:
        # Manual validation error
        raise RequestValidationError(
            errors=[{
                "loc": ["body", "age"],
                "msg": "Age must be positive",
                "type": "value_error",
            }]
        )

    return {"status": "created", "user": user}


# Example 3: Generic exceptions (converted to 500 errors)
@api.get("/internal-error")
async def internal_error():
    """Endpoint that raises a generic exception.

    In DEBUG mode, this will include a traceback.
    In production, it returns a generic 500 error.
    """
    # This will be caught and converted to an InternalServerError
    raise ValueError("Something went wrong internally")


# Example 4: Manual error responses with extra data
@api.get("/complex-error")
async def complex_error():
    """Endpoint demonstrating custom error with extra data."""
    raise HTTPException(
        status_code=422,
        detail="Complex validation failed",
        extra={
            "errors": [
                {"field": "email", "message": "Email already exists"},
                {"field": "username", "message": "Username too short"},
            ],
            "suggestion": "Please check your input and try again",
        }
    )


# Example 5: Health checks
register_health_checks(api)


# Add custom health check
async def check_redis():
    """Custom health check for Redis."""
    try:
        # Simulate Redis check
        # import redis
        # r = redis.Redis()
        # r.ping()
        return True, "Redis OK"
    except Exception as e:
        return False, f"Redis error: {str(e)}"


add_health_check(check_redis)


# Example 6: Using logging middleware (integrate this in your app)
"""
To use logging middleware in your Django-Bolt app:

from django_bolt import BoltAPI
from django_bolt.logging import create_logging_middleware

api = BoltAPI()

# Create logging middleware
logging_middleware = create_logging_middleware()

# In your handler, you can manually log:
@api.post("/items")
async def create_item(request, item: Item):
    # Log the request
    logging_middleware.log_request(request)

    try:
        # Process request
        result = process_item(item)

        # Log the response
        logging_middleware.log_response(request, 201, duration=0.5)

        return result
    except Exception as e:
        # Log the exception
        logging_middleware.log_exception(request, e)
        raise
"""


if __name__ == "__main__":
    print("Django-Bolt Error Handling Demo")
    print("=" * 50)
    print()
    print("Error Response Examples:")
    print()
    print("1. 404 Not Found:")
    print('   GET /users/0')
    print('   Response: {"detail": "User not found"}')
    print()
    print("2. 400 Bad Request:")
    print('   GET /users/-1')
    print('   Response: {"detail": "Invalid user ID"}')
    print()
    print("3. 401 Unauthorized:")
    print('   GET /users/999')
    print('   Response: {"detail": "Authentication required"}')
    print('   Headers: WWW-Authenticate: Bearer')
    print()
    print("4. 422 Validation Error:")
    print('   POST /users')
    print('   Body: {"username": "test", "email": "bad", "age": -1}')
    print('   Response: {"detail": [{"loc": ["body", "age"], "msg": "Age must be positive", "type": "value_error"}]}')
    print()
    print("5. 500 Internal Server Error (DEBUG=True):")
    print('   GET /internal-error')
    print('   Response: {"detail": "ValueError: Something went wrong", "extra": {"traceback": "..."}}')
    print()
    print("6. Health Checks:")
    print('   GET /health')
    print('   Response: {"status": "ok"}')
    print()
    print('   GET /ready')
    print('   Response: {"status": "healthy", "checks": {"check_database": {"healthy": true, "message": "Database connection OK"}}}')
