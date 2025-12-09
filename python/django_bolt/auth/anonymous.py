"""
Anonymous user fallback for when Django middleware is not configured.

This module provides the auser_fallback async function that returns
AnonymousUser, matching Django's behavior when AuthenticationMiddleware
is not configured.
"""
from __future__ import annotations

from django.contrib.auth.models import AnonymousUser


async def auser_fallback() -> AnonymousUser:
    """
    Async fallback that returns AnonymousUser.

    This is used when Django's AuthenticationMiddleware is not configured,
    ensuring that `await request.auser()` always returns a valid user object
    (either the authenticated user or AnonymousUser).

    Returns:
        AnonymousUser instance
    """
    return AnonymousUser()


__all__ = ["auser_fallback"]
