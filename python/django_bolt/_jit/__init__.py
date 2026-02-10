"""
JIT-style dispatch compiler for Django-Bolt.

Inspired by Elysia.js, this module generates specialized dispatch functions
for each handler at registration time, eliminating runtime branching.

Instead of a generic _dispatch function with 15+ conditionals, we generate
code like:

    async def _dispatch_123(handler, request):
        # Inline: extract path param 'id' as int
        id_param = request["params"]["id"]
        # Inline: no auth needed for this handler
        # Inline: async handler, direct call
        result = await handler(id=id_param)
        # Inline: JSON serialization (most common)
        return (200, ("json", None, None, None), _json.encode(result))

This eliminates:
- Function call overhead (injector, serialize_response)
- Runtime type checking (isinstance chains)
- Conditional branching (if needs_auth, if is_async, etc.)
- Dict lookups for metadata
"""

from __future__ import annotations

from .generator import compile_jit_dispatcher, JIT_DISPATCHERS

__all__ = ["compile_jit_dispatcher", "JIT_DISPATCHERS"]
