"""Error formatter app: RFC 9457 errors from Rust and from Python on a real server."""

from __future__ import annotations

from uuid import UUID

from django_bolt import BoltAPI
from django_bolt.auth import AllowAny, IsAuthenticated
from django_bolt.error_handlers import problem_details
from django_bolt.exceptions import HTTPException

api = BoltAPI(error_formatter=problem_details)


@api.get("/health")
async def health():
    return {"status": "ok"}


@api.get("/private", guards=[IsAuthenticated()])
async def private() -> dict:
    return {}


@api.get("/items/{item_id}", guards=[AllowAny()])
async def item(item_id: UUID) -> dict:
    return {}


@api.get("/conflict")
def conflict() -> dict:
    raise HTTPException(409, "Already exists")
