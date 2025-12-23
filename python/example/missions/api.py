from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from msgspec import Meta

from django_bolt import BoltAPI
from django_bolt.exceptions import NotFound
from django_bolt.param_functions import Cookie, File, Form, Header, Query
from django_bolt.serializers import Serializer, field_validator

from missions.models import Astronaut, Mission

api = BoltAPI()


# Schemas
class CreateMission(Serializer):
    name: Annotated[str, Meta(min_length=1, max_length=100)]
    description: Annotated[str, Meta(max_length=500)] = ""
    launch_date: datetime | None = None

    @field_validator("name")
    def validate_name(cls, value):
        if value.lower().startswith("test"):
            raise ValueError("Mission name cannot start with 'test'")
        return value


class UpdateMission(Serializer):
    name: Annotated[str, Meta(min_length=1, max_length=100)] | None = None
    status: Literal["planned", "active", "completed", "aborted"] | None = None
    description: Annotated[str, Meta(max_length=500)] | None = None


class MissionResponse(Serializer):
    id: int
    name: str
    status: str
    launch_date: datetime | None = None
    description: str = ""


class AstronautResponse(Serializer):
    id: int
    name: str
    role: str
    mission_id: int


# Query parameter model for filtering missions
class MissionFilters(Serializer):
    status: Literal["planned", "active", "completed", "aborted"] | None = None
    limit: Annotated[int, Meta(ge=1, le=100)] = 10


# Form model for creating astronauts
class CreateAstronaut(Serializer):
    name: Annotated[str, Meta(min_length=1, max_length=100)]
    role: Annotated[str, Meta(min_length=1, max_length=50)]

    @field_validator("role")
    def validate_role(cls, value):
        valid_roles = ["Commander", "Pilot", "Mission Specialist", "Flight Engineer", "Payload Specialist"]
        if value not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return value


# Endpoints
@api.get("/missions")
async def list_missions(filters: Annotated[MissionFilters, Query()]):
    """List all missions with optional filtering."""
    queryset = Mission.objects.all()
    if filters.status:
        queryset = queryset.filter(status=filters.status)
    missions = []
    async for mission in queryset[:filters.limit]:
        missions.append({
            "id": mission.id,
            "name": mission.name,
            "status": mission.status,
        })
    return {"missions": missions, "count": len(missions)}


@api.get("/missions/{mission_id}")
async def get_mission(mission_id: int):
    """Get a specific mission by ID."""
    try:
        mission = await Mission.objects.aget(id=mission_id)
        return {
            "id": mission.id,
            "name": mission.name,
            "status": mission.status,
            "launch_date": str(mission.launch_date) if mission.launch_date else None,
            "description": mission.description,
        }
    except Mission.DoesNotExist:
        raise NotFound(detail=f"Mission {mission_id} not found")


@api.post("/missions")
async def create_mission(mission: CreateMission):
    """Create a new mission."""
    new_mission = await Mission.objects.acreate(
        name=mission.name,
        description=mission.description,
        launch_date=mission.launch_date,
        status="planned",
    )
    return {
        "id": new_mission.id,
        "name": new_mission.name,
        "status": new_mission.status,
        "message": "Mission created successfully",
    }


@api.put("/missions/{mission_id}")
async def update_mission(mission_id: int, data: UpdateMission):
    """Update a mission."""
    try:
        mission = await Mission.objects.aget(id=mission_id)
    except Mission.DoesNotExist:
        raise NotFound(detail=f"Mission {mission_id} not found")

    if data.name is not None:
        mission.name = data.name
    if data.status is not None:
        mission.status = data.status
    if data.description is not None:
        mission.description = data.description

    await mission.asave()
    return {"id": mission.id, "name": mission.name, "status": mission.status}


@api.delete("/missions/{mission_id}", status_code=204)
async def delete_mission(mission_id: int):
    """Delete a mission."""
    try:
        mission = await Mission.objects.aget(id=mission_id)
    except Mission.DoesNotExist:
        raise NotFound(detail=f"Mission {mission_id} not found")

    await mission.adelete()


# Astronaut endpoints
@api.post("/missions/{mission_id}/astronauts")
async def add_astronaut(
    mission_id: int,
    data: Annotated[CreateAstronaut, Form()],
):
    """Add an astronaut to a mission."""
    try:
        mission = await Mission.objects.aget(id=mission_id)
    except Mission.DoesNotExist:
        raise NotFound(detail=f"Mission {mission_id} not found")

    astronaut = await Astronaut.objects.acreate(
        name=data.name,
        role=data.role,
        mission=mission,
    )
    return {
        "id": astronaut.id,
        "name": astronaut.name,
        "role": astronaut.role,
        "mission": mission.name,
    }


@api.get("/missions/{mission_id}/astronauts")
async def list_astronauts(mission_id: int):
    """List all astronauts for a mission."""
    try:
        mission = await Mission.objects.aget(id=mission_id)
    except Mission.DoesNotExist:
        raise NotFound(detail=f"Mission {mission_id} not found")

    astronauts = []
    async for astronaut in Astronaut.objects.filter(mission=mission):
        astronauts.append({
            "id": astronaut.id,
            "name": astronaut.name,
            "role": astronaut.role,
        })
    return {"mission": mission.name, "astronauts": astronauts}


# Header model for API metadata
class APIHeaders(Serializer):
    x_api_key: str
    x_request_id: str | None = None


# Cookie model for user preferences
class UserPreferences(Serializer):
    theme: str = "light"
    language: str = "en"


# File upload endpoint
@api.post("/missions/{mission_id}/documents")
async def upload_document(
    mission_id: int,
    title: Annotated[str, Form()],
    files: Annotated[list[dict], File(alias="file")],
):
    """Upload documents for a mission."""
    try:
        mission = await Mission.objects.aget(id=mission_id)
    except Mission.DoesNotExist:
        raise NotFound(detail=f"Mission {mission_id} not found")

    uploaded = []
    for f in files:
        uploaded.append({
            "filename": f.get("filename"),
            "content_type": f.get("content_type"),
            "size": f.get("size"),
        })

    return {
        "mission": mission.name,
        "title": title,
        "documents": uploaded,
        "count": len(uploaded),
    }


# Header struct endpoint
@api.get("/missions/secure")
async def secure_endpoint(headers: Annotated[APIHeaders, Header()]):
    """Endpoint requiring API key header."""
    return {
        "api_key": headers.x_api_key,
        "request_id": headers.x_request_id,
        "message": "Access granted",
    }


# Cookie struct endpoint
@api.get("/missions/preferences")
async def get_preferences(cookies: Annotated[UserPreferences, Cookie()]):
    """Get user preferences from cookies."""
    return {
        "theme": cookies.theme,
        "language": cookies.language,
    }


# Mixed form and file upload
@api.post("/missions/{mission_id}/report")
async def submit_report(
    mission_id: int,
    title: Annotated[str, Form()],
    summary: Annotated[str, Form()] = "",
    attachments: Annotated[list[dict], File(alias="file")] = [],
):
    """Submit a mission report with optional attachments."""
    try:
        mission = await Mission.objects.aget(id=mission_id)
    except Mission.DoesNotExist:
        raise NotFound(detail=f"Mission {mission_id} not found")

    return {
        "mission": mission.name,
        "title": title,
        "summary": summary,
        "attachments": len(attachments),
    }
