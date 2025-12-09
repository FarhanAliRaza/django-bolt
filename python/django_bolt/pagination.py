"""
Pagination utilities for Django-Bolt.

Provides Django Paginator-based pagination that works with both functional
and class-based views, leveraging Django's built-in pagination while integrating
with Bolt's parameter extraction and serialization systems.

Example (Functional View):
    @api.get("/users")
    @paginate(PageNumberPagination)
    async def list_users():
        return User.objects.all()

Example (Class-Based View):
    @api.viewset("/articles")
    class ArticleViewSet(ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema
        pagination_class = PageNumberPagination
"""
from __future__ import annotations

import base64
import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import msgspec
from asgiref.sync import sync_to_async

from . import _json

__all__ = [
    "PaginationBase",
    "PageNumberPagination",
    "LimitOffsetPagination",
    "CursorPagination",
    "PaginatedResponse",
    "paginate",
]

T = TypeVar("T")


class PaginatedResponse[T](msgspec.Struct):
    """
    Standard paginated response structure.

    Attributes:
        items: List of paginated items
        total: Total number of items across all pages
        page: Current page number (for PageNumber pagination)
        page_size: Number of items per page
        total_pages: Total number of pages
        has_next: Whether there is a next page
        has_previous: Whether there is a previous page
        next_page: Next page number (None if no next page)
        previous_page: Previous page number (None if no previous page)
    """
    items: list[T]
    total: int
    page: int | None = None
    page_size: int | None = None
    total_pages: int | None = None
    has_next: bool = False
    has_previous: bool = False
    next_page: int | None = None
    previous_page: int | None = None

    # For LimitOffset pagination
    limit: int | None = None
    offset: int | None = None

    # For Cursor pagination
    next_cursor: str | None = None
    previous_cursor: str | None = None


class PaginationBase(ABC):
    """
    Base class for all pagination schemes.

    Subclasses must implement:
        - get_page_params(): Extract pagination params from request
        - paginate_queryset(): Apply pagination to queryset
    """

    # Default page size
    page_size: int = 100

    # Maximum allowed page size (prevents abuse)
    max_page_size: int = 1000

    # Name of the page size query parameter
    page_size_query_param: str | None = None

    @abstractmethod
    async def get_page_params(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Extract pagination parameters from request.

        Args:
            request: Request dictionary

        Returns:
            Dictionary of pagination parameters
        """
        raise NotImplementedError

    @abstractmethod
    async def paginate_queryset(
        self,
        queryset: Any,
        request: dict[str, Any],
        **params: Any
    ) -> PaginatedResponse:
        """
        Apply pagination to a queryset and return paginated response.

        Args:
            queryset: Django QuerySet to paginate
            request: Request dictionary
            **params: Additional parameters

        Returns:
            PaginatedResponse with items and metadata
        """
        raise NotImplementedError

    async def _get_queryset_count(self, queryset: Any) -> int:
        """
        Get total count of queryset items.

        Handles both sync and async querysets.

        Args:
            queryset: Django QuerySet

        Returns:
            Total count
        """
        # Check if queryset has acount (async count)
        if hasattr(queryset, 'acount'):
            return await queryset.acount()
        # Fallback to sync count wrapped in sync_to_async
        elif hasattr(queryset, 'count'):
            return await sync_to_async(queryset.count)()
        # For lists or other iterables
        else:
            return len(queryset)

    async def _evaluate_queryset_slice(self, queryset: Any) -> list[Any]:
        """
        Evaluate a queryset slice to a list.

        Handles both sync and async querysets.
        Converts Django model instances to dicts for serialization.

        Args:
            queryset: Django QuerySet or iterable

        Returns:
            List of items (Django models converted to dicts)
        """
        items = []

        # Check if it's an async iterable (has __aiter__)
        if hasattr(queryset, '__aiter__'):
            async for item in queryset:
                items.append(self._model_to_dict(item))
            return items
        # Check if it's a Django QuerySet with async support
        elif hasattr(queryset, '_iterable_class') and hasattr(queryset, 'model'):
            # It's a QuerySet - check if we can iterate async
            try:
                async for item in queryset:
                    items.append(self._model_to_dict(item))
                return items
            except TypeError:
                # Not async iterable, use sync_to_async
                raw_items = await sync_to_async(list)(queryset)
                return [self._model_to_dict(item) for item in raw_items]
        # Regular iterable or list
        else:
            result = list(queryset)
            return [self._model_to_dict(item) for item in result]

    def _model_to_dict(self, item: Any) -> Any:
        """
        Convert Django model instance to dict for serialization.

        Args:
            item: Django model instance or any object

        Returns:
            Dict if item is a Django model, otherwise returns item unchanged
        """
        # Check if it's a Django model instance
        if hasattr(item, '_meta') and hasattr(item, '_state'):
            # It's a Django model - convert to dict
            # Get all field values - use __dict__ which is safe in async context
            data = {}
            # Use model's __dict__ to avoid accessing _meta in async context
            for key, value in item.__dict__.items():
                # Skip private attributes and Django internal state
                if not key.startswith('_'):
                    data[key] = value
            return data
        # Not a model, return as-is
        return item

    def _get_page_size(self, request: dict[str, Any]) -> int:
        """
        Get page size from request, with validation.

        Args:
            request: Request dictionary

        Returns:
            Validated page size
        """
        if self.page_size_query_param:
            query = request.get('query', {})
            page_size_str = query.get(self.page_size_query_param)
            if page_size_str:
                try:
                    page_size = int(page_size_str)
                    # Enforce max_page_size limit
                    if page_size > self.max_page_size:
                        return self.max_page_size
                    if page_size < 1:
                        return self.page_size
                    return page_size
                except (ValueError, TypeError):
                    pass

        return self.page_size


class PageNumberPagination(PaginationBase):
    """
    Page number-based pagination.

    Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (optional, default: 100)

    Example:
        /api/users?page=2&page_size=20

    Attributes:
        page_size: Default number of items per page (default: 100)
        max_page_size: Maximum allowed page size (default: 1000)
        page_size_query_param: Query param name for page size (default: "page_size")
    """

    page_size: int = 100
    max_page_size: int = 1000
    page_size_query_param: str = "page_size"

    async def get_page_params(self, request: dict[str, Any]) -> dict[str, Any]:
        """Extract page number and page_size from request."""
        query = request.get('query', {})

        # Get page number (default to 1)
        page_str = query.get('page', '1')
        try:
            page = int(page_str)
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1

        # Get page size
        page_size = self._get_page_size(request)

        return {'page': page, 'page_size': page_size}

    async def paginate_queryset(
        self,
        queryset: Any,
        request: dict[str, Any],
        **params: Any
    ) -> PaginatedResponse:
        """
        Paginate queryset using page numbers.

        Args:
            queryset: Django QuerySet to paginate
            request: Request dictionary
            **params: Additional parameters (unused)

        Returns:
            PaginatedResponse with pagination metadata
        """
        page_params = await self.get_page_params(request)
        page_number = page_params['page']
        page_size = page_params['page_size']

        # Get total count
        total = await self._get_queryset_count(queryset)

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # Validate page number
        if page_number > total_pages and total_pages > 0:
            page_number = total_pages

        # Calculate offset
        offset = (page_number - 1) * page_size

        # Slice queryset
        items = await self._evaluate_queryset_slice(queryset[offset:offset + page_size])

        # Build response
        return PaginatedResponse(
            items=items,
            total=total,
            page=page_number,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page_number < total_pages,
            has_previous=page_number > 1,
            next_page=page_number + 1 if page_number < total_pages else None,
            previous_page=page_number - 1 if page_number > 1 else None,
        )


class LimitOffsetPagination(PaginationBase):
    """
    Limit-offset based pagination.

    Query parameters:
        - limit: Number of items to return (default: 100)
        - offset: Starting position (default: 0)

    Example:
        /api/users?limit=20&offset=40

    Attributes:
        page_size: Default limit when not specified (default: 100)
        max_page_size: Maximum allowed limit (default: 1000)
    """

    page_size: int = 100
    max_page_size: int = 1000

    async def get_page_params(self, request: dict[str, Any]) -> dict[str, Any]:
        """Extract limit and offset from request."""
        query = request.get('query', {})

        # Get limit (default to page_size)
        limit_str = query.get('limit', None)
        if limit_str is None:
            # No limit specified, use default
            limit = self.page_size
        else:
            try:
                limit = int(limit_str)
                if limit < 1:
                    limit = self.page_size
                if limit > self.max_page_size:
                    limit = self.max_page_size
            except (ValueError, TypeError):
                limit = self.page_size

        # Get offset (default to 0)
        offset_str = query.get('offset', '0')
        try:
            offset = int(offset_str)
            if offset < 0:
                offset = 0
        except (ValueError, TypeError):
            offset = 0

        return {'limit': limit, 'offset': offset}

    async def paginate_queryset(
        self,
        queryset: Any,
        request: dict[str, Any],
        **params: Any
    ) -> PaginatedResponse:
        """
        Paginate queryset using limit/offset.

        Args:
            queryset: Django QuerySet to paginate
            request: Request dictionary
            **params: Additional parameters (unused)

        Returns:
            PaginatedResponse with pagination metadata
        """
        page_params = await self.get_page_params(request)
        limit = page_params['limit']
        offset = page_params['offset']

        # Get total count
        total = await self._get_queryset_count(queryset)

        # Slice queryset
        items = await self._evaluate_queryset_slice(queryset[offset:offset + limit])

        # Calculate page info
        has_next = (offset + limit) < total
        has_previous = offset > 0

        return PaginatedResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next,
            has_previous=has_previous,
        )


class CursorPagination(PaginationBase):
    """
    Cursor-based pagination for large datasets.

    More efficient than offset-based pagination for large datasets
    as it doesn't require counting all records or scanning through skipped records.

    Query parameters:
        - cursor: Opaque cursor string (optional)
        - page_size: Items per page (optional)

    Example:
        /api/users?cursor=eyJpZCI6MTAwfQ==&page_size=20

    Attributes:
        page_size: Default number of items per page (default: 100)
        max_page_size: Maximum allowed page size (default: 1000)
        page_size_query_param: Query param name for page size (default: "page_size")
        ordering: Field to order by (default: "-id" for descending ID)
    """

    page_size: int = 100
    max_page_size: int = 1000
    page_size_query_param: str = "page_size"
    ordering: str = "-id"  # Default ordering field

    def _encode_cursor(self, value: Any) -> str:
        """
        Encode cursor value to base64 string.

        Args:
            value: Cursor value (typically an ID)

        Returns:
            Base64-encoded cursor string
        """
        cursor_data = _json.encode({"v": value})
        return base64.b64encode(cursor_data).decode('utf-8')

    def _decode_cursor(self, cursor: str) -> Any:
        """
        Decode cursor string to value.

        Args:
            cursor: Base64-encoded cursor string

        Returns:
            Decoded cursor value
        """
        try:
            cursor_data = base64.b64decode(cursor.encode('utf-8'))
            data = msgspec.json.decode(cursor_data)
            return data.get("v")
        except Exception:
            return None

    async def get_page_params(self, request: dict[str, Any]) -> dict[str, Any]:
        """Extract cursor and page_size from request."""
        query = request.get('query', {})

        # Get cursor (optional)
        cursor_str = query.get('cursor')
        cursor_value = self._decode_cursor(cursor_str) if cursor_str else None

        # Get page size
        page_size = self._get_page_size(request)

        return {'cursor': cursor_value, 'page_size': page_size}

    async def paginate_queryset(
        self,
        queryset: Any,
        request: dict[str, Any],
        **params: Any
    ) -> PaginatedResponse:
        """
        Paginate queryset using cursor-based pagination.

        Args:
            queryset: Django QuerySet to paginate
            request: Request dictionary
            **params: Additional parameters (unused)

        Returns:
            PaginatedResponse with cursor metadata
        """
        page_params = await self.get_page_params(request)
        cursor_value = page_params['cursor']
        page_size = page_params['page_size']

        # Apply ordering
        ordering = self.ordering
        is_descending = ordering.startswith('-')
        ordering_field = ordering.lstrip('-')

        # Apply ordering to queryset
        ordered_qs = queryset.order_by(ordering)

        # Apply cursor filter if present
        if cursor_value is not None:
            if is_descending:
                # For descending order, we want items less than cursor
                filter_kwargs = {f"{ordering_field}__lt": cursor_value}
            else:
                # For ascending order, we want items greater than cursor
                filter_kwargs = {f"{ordering_field}__gt": cursor_value}

            ordered_qs = ordered_qs.filter(**filter_kwargs)

        # Fetch page_size + 1 items to determine if there's a next page
        items = await self._evaluate_queryset_slice(ordered_qs[:page_size + 1])

        # Check if there are more items
        has_next = len(items) > page_size
        if has_next:
            items = items[:page_size]  # Trim to page_size

        # Generate next cursor from last item
        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            # Items are now dicts (converted from models), so use dict access
            if isinstance(last_item, dict):
                last_value = last_item.get(ordering_field)
            else:
                last_value = getattr(last_item, ordering_field, None)

            if last_value is not None:
                next_cursor = self._encode_cursor(last_value)

        return PaginatedResponse(
            items=items,
            total=0,  # Cursor pagination doesn't provide total count for efficiency
            page_size=page_size,
            has_next=has_next,
            has_previous=cursor_value is not None,
            next_cursor=next_cursor,
        )


def paginate(pagination_class: type[PaginationBase] = PageNumberPagination):
    """
    Decorator to apply pagination to a route handler.

    The decorated handler should return a Django QuerySet or list.
    The decorator will automatically apply pagination and return a PaginatedResponse.

    Args:
        pagination_class: Pagination class to use (default: PageNumberPagination)

    Example:
        @api.get("/users")
        @paginate(PageNumberPagination)
        async def list_users():
            return User.objects.all()

        @api.get("/articles")
        @paginate(LimitOffsetPagination)
        async def list_articles(status: str = "published"):
            return Article.objects.filter(status=status)

    Returns:
        Decorated handler function
    """
    def decorator(handler: Callable) -> Callable:
        # Create pagination instance
        paginator = pagination_class()

        # Store original handler for introspection
        original_handler = handler

        @wraps(handler)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            # Request can be in:
            # 1. kwargs['request'] - most common
            # 2. args[0] - for single-param handlers
            # 3. args[1] - for ViewSet methods (args[0] is self)
            request = None

            # Try kwargs first (most reliable)
            if 'request' in kwargs:
                request = kwargs['request']
            # Check if this is a method with self as first arg
            elif len(args) >= 2:
                # Could be (self, request, ...) or (request, other_params...)
                # If args[0] looks like a view instance, args[1] is request
                first_arg = args[0]
                if (hasattr(first_arg, '__class__') and
                    hasattr(first_arg.__class__, '__mro__') and
                    any('View' in cls.__name__ for cls in first_arg.__class__.__mro__)):
                    request = args[1]
                else:
                    # args[0] is request, args[1] is another parameter
                    request = args[0]
            elif len(args) == 1:
                # Single arg - should be request
                request = args[0]

            if request is None:
                raise ValueError(
                    f"Pagination decorator on {handler.__name__} could not find request. "
                    f"Args: {[type(a).__name__ for a in args]}, kwargs: {list(kwargs.keys())}"
                )

            # Convert PyRequest to dict if needed for pagination
            # PyRequest objects from Rust layer behave like dicts
            if not isinstance(request, dict) and hasattr(request, '__getitem__'):
                # It's a PyRequest object - convert to dict for pagination methods
                request_dict = {
                    'method': request.get('method', 'GET'),
                    'query': request.get('query', {}),
                    'params': request.get('params', {}),
                    'headers': request.get('headers', {}),
                    'cookies': request.get('cookies', {}),
                }
            elif isinstance(request, dict):
                request_dict = request
            else:
                raise ValueError(
                    f"Unexpected request type: {type(request)}. "
                    f"Args: {[type(a).__name__ for a in args]}, kwargs: {list(kwargs.keys())}"
                )

            # Call original handler to get queryset
            # Pass all args along (including self for methods)
            queryset = await handler(*args, **kwargs)

            # Apply pagination using dict version
            paginated = await paginator.paginate_queryset(
                queryset, request_dict
            )

            return paginated

        # Preserve signature so framework knows to pass request
        wrapper.__signature__ = inspect.signature(original_handler)
        wrapper.__name__ = original_handler.__name__
        wrapper.__doc__ = original_handler.__doc__
        wrapper.__module__ = original_handler.__module__

        # Mark that this handler returns PaginatedResponse for serialization
        wrapper.__paginated__ = True
        wrapper.__pagination_class__ = pagination_class

        return wrapper

    return decorator
