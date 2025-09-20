from django_bolt import BoltAPI, JSON
from asgiref.sync import sync_to_async
import msgspec
from .models import User

api = BoltAPI(prefix="/users")


class UserFull(msgspec.Struct):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool


class UserMini(msgspec.Struct):
    id: int
    username: str


@api.get("/")
async def users_root():
    return {"ok": True}


@api.get("/full10", response_model=list[UserFull])
async def list_full_10() -> list[UserFull]:
    @sync_to_async
    def fetch():
        return list(User.objects.all()[:10])

    return await fetch()


@api.get("/mini10", response_model=list[UserMini])
async def list_mini_10() -> list[UserMini]:
    @sync_to_async
    def fetch():
        return list(User.objects.only("id", "username")[:10])

    return await fetch()

