"""Error formatter app with a lifespan: runbolt starts the server in another branch for it."""

from __future__ import annotations

from contextlib import asynccontextmanager

from django_bolt import BoltAPI
from django_bolt.error_handlers import problem_details
from django_bolt.exceptions import HTTPException


@asynccontextmanager
async def lifespan(app: BoltAPI):
    yield


api = BoltAPI(error_formatter=problem_details, lifespan=lifespan)


@api.get("/health")
async def health():
    return {"status": "ok"}


@api.get("/conflict")
async def conflict() -> dict:
    raise HTTPException(409, "Already exists")
