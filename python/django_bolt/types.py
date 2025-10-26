"""
Type definitions for Django-Bolt.

This module provides type hints and protocols for Django-Bolt objects,
enabling full IDE autocomplete and static type checking.
"""
from typing import Protocol, Any, Dict, Optional, overload, runtime_checkable


@runtime_checkable
class Request(Protocol):
    """
    Django-Bolt request object (Rust-backed PyRequest).

    Provides dict-like access to HTTP request data with full type safety.
    This is a Protocol that matches the Rust PyRequest implementation,
    enabling proper type hints and IDE autocomplete.

    Example:
        ```python
        from django_bolt import BoltAPI, Request
        import msgspec

        class UserCreate(msgspec.Struct):
            name: str
            email: str

        api = BoltAPI()

        # With request object and validated body
        @api.post("/users")
        async def create_user(request: Request, user: UserCreate):
            # Type-safe access to request data
            method = request.method          # str
            auth = request.get("auth")       # Optional[Dict[str, Any]]
            headers = request["headers"]     # Dict[str, str]

            # Validated body with full type safety
            name = user.name                 # str
            email = user.email               # str

            return {"id": 1, "name": name}

        # With just request object
        @api.get("/users/{user_id}")
        async def get_user(request: Request, user_id: int):
            auth = request.get("auth", {})
            user_id = auth.get("user_id")
            return {"user_id": user_id}
        ```

    Available Keys (for .get() and [] access):
        - "method": HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
        - "path": Request path (/users/123)
        - "body": Raw request body (bytes)
        - "params": Path parameters from URL pattern (Dict[str, str])
        - "query": Query string parameters (Dict[str, str])
        - "headers": HTTP headers (Dict[str, str])
        - "cookies": Parsed cookies (Dict[str, str])
        - "auth": Authentication context (Optional[Dict[str, Any]])
        - "context": Same as "auth" (alias)

    Auth Context Structure (when authentication is present):
        ```python
        {
            "user_id": "123",                # User identifier (str)
            "is_staff": False,               # Staff status (bool)
            "is_admin": False,               # Admin/superuser status (bool)
            "auth_backend": "jwt",           # Backend used: jwt, api_key, etc.
            "permissions": ["read", "write"], # User permissions (List[str], optional)
            "auth_claims": {                 # Full JWT claims (optional, JWT only)
                "sub": "123",
                "exp": 1234567890,
                "iat": 1234567800,
                # ... additional claims
            }
        }
        ```
    """

    # Properties (from Rust #[getter])
    @property
    def method(self) -> str:
        """
        HTTP method.

        Returns:
            HTTP method string: "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"

        Example:
            ```python
            if request.method == "POST":
                # Handle POST request
                pass
            ```
        """
        ...

    @property
    def path(self) -> str:
        """
        Request path.

        Returns:
            Request path string (e.g., "/users/123")

        Example:
            ```python
            path = request.path  # "/api/users/123"
            ```
        """
        ...

    @property
    def body(self) -> bytes:
        """
        Raw request body.

        Returns:
            Request body as bytes

        Note:
            For JSON requests, the framework automatically decodes this
            when you use msgspec.Struct parameter types. You typically
            don't need to access this directly.

        Example:
            ```python
            raw_body = request.body
            # b'{"name": "John", "email": "john@example.com"}'
            ```
        """
        ...

    @property
    def context(self) -> Optional[Dict[str, Any]]:
        """
        Authentication/middleware context.

        Returns:
            Context dictionary when authentication is present, None otherwise.

            When present, contains:
            - user_id (str): User identifier
            - is_staff (bool): Staff status
            - is_admin (bool): Admin/superuser status
            - auth_backend (str): Backend used (jwt, api_key, etc.)
            - permissions (List[str]): User permissions (if available)
            - auth_claims (Dict): Full JWT claims (if JWT authentication)

        Example:
            ```python
            ctx = request.context
            if ctx:
                user_id = ctx.get("user_id")
                is_admin = ctx.get("is_admin", False)
            ```
        """
        ...

    # Methods
    @overload
    def get(self, key: str) -> Any:
        """Get request attribute (returns None if not found)."""
        ...

    @overload
    def get(self, key: str, default: Any) -> Any:
        """Get request attribute with default value."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get request attribute with optional default value.

        This method provides dict-like .get() access to request data,
        with support for default values when keys don't exist.

        Args:
            key: Attribute name to retrieve. Available keys:
                - "method": HTTP method (str)
                - "path": Request path (str)
                - "body": Raw body (bytes)
                - "params": Path parameters (Dict[str, str])
                - "query": Query parameters (Dict[str, str])
                - "headers": HTTP headers (Dict[str, str])
                - "cookies": Parsed cookies (Dict[str, str])
                - "auth": Auth context (Optional[Dict[str, Any]])
                - "context": Same as "auth"
            default: Default value to return if key doesn't exist or is None.
                     Defaults to None.

        Returns:
            Attribute value if present, otherwise default value.

        Special Behavior:
            For "auth" and "context" keys, if authentication is not configured
            or no credentials provided, returns the default value (not an empty dict).

        Example:
            ```python
            # Get with None as default
            auth = request.get("auth")  # None if no auth

            # Get with custom default
            auth = request.get("auth", {})  # {} if no auth

            # Get method (always present)
            method = request.get("method")  # "GET", "POST", etc.

            # Get query params
            query = request.get("query", {})
            page = query.get("page", "1")
            ```
        """
        ...

    def __getitem__(self, key: str) -> Any:
        """
        Dict-style access to request attributes.

        Args:
            key: Attribute name (same keys as .get())

        Returns:
            Attribute value

        Raises:
            KeyError: If key doesn't exist

        Example:
            ```python
            method = request["method"]      # "GET"
            headers = request["headers"]    # Dict[str, str]
            params = request["params"]      # Dict[str, str]

            # Raises KeyError if no auth
            context = request["context"]

            # Safe alternative with .get()
            context = request.get("context", {})
            ```
        """
        ...


__all__ = ["Request"]
