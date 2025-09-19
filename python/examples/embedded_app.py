from django_bolt import BoltAPI, JSON

api = BoltAPI()


@api.get("/hello")
async def hello(req):
    return JSON({"ok": True})


@api.get("/users")
async def list_users(req):
    from django.contrib.auth.models import User
    from asgiref.sync import sync_to_async
    
    # Use sync_to_async for ORM operations until Django async ORM is ready
    @sync_to_async
    def get_users():
        return list(
            User.objects.all()
            .only("id", "username", "is_staff")
            .values("id", "username", "is_staff")
        )
    
    data = await get_users()
    return data


@api.get("/users/{user_id}")
async def get_user(req, user_id: str):
    """Example with path parameters"""
    return JSON({
        "user_id": user_id,
        "query": req.get("query", {}),
        "message": f"Fetched user {user_id}"
    })


@api.get("/search")
async def search(req):
    """Example with query parameters"""
    query = req.get("query", {})
    q = query.get("q", "")
    limit = query.get("limit", "10")
    
    return {
        "search_term": q,
        "limit": limit,
        "results": []
    }


if __name__ == "__main__":
    api.serve("0.0.0.0", 8000)
