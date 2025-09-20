from django_bolt import BoltAPI, JSON
from asgiref.sync import sync_to_async
from .models import User

# API with prefix for users app
api = BoltAPI(prefix="/users")


@api.get("/")
async def list_users(req):
    """List all users from database"""
    @sync_to_async
    def get_users():
        return list(User.objects.values('id', 'username', 'email', 'is_active'))
    
    users = await get_users()
    return JSON({"users": users, "count": len(users)})


@api.get("/{user_id}")
async def get_user(req):
    """Get specific user from database"""
    user_id = req.get("params", {}).get("user_id")
    
    @sync_to_async
    def fetch_user():
        try:
            return User.objects.values('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'created_at').get(id=user_id)
        except User.DoesNotExist:
            return None
    
    user = await fetch_user()
    if user:
        return JSON({"user": user})
    else:
        return JSON({"error": "User not found"}, status_code=404)


@api.post("/")
async def create_user(req):
    """Create a new user in database"""
    # For demo purposes, create a user with incremental data
    @sync_to_async
    def create_user_db():
        import random
        count = User.objects.count()
        username = f"user{count + 1}"
        email = f"user{count + 1}@example.com"
        
        user = User.objects.create(
            username=username,
            email=email,
            first_name=f"First{count + 1}",
            last_name=f"Last{count + 1}"
        )
        return {"id": user.id, "username": user.username, "email": user.email}
    
    user_data = await create_user_db()
    return JSON({"message": "User created", "user": user_data})


@api.get("/seed")
async def seed_users(req):
    """Seed database with sample users for testing"""
    @sync_to_async
    def create_sample_users():
        # Clear existing users
        User.objects.all().delete()
        
        # Create sample users
        users = []
        for i in range(100):
            user = User.objects.create(
                username=f"user{i+1:03d}",
                email=f"user{i+1:03d}@example.com",
                first_name=f"First{i+1:03d}",
                last_name=f"Last{i+1:03d}",
                is_active=(i % 10 != 0)  # Every 10th user is inactive
            )
            users.append(user.username)
        return users
    
    usernames = await create_sample_users()
    return JSON({"message": f"Created {len(usernames)} sample users", "sample": usernames[:5]})


@api.get("/stats")
async def user_stats(req):
    """Get user statistics"""
    @sync_to_async
    def get_stats():
        total = User.objects.count()
        active = User.objects.filter(is_active=True).count()
        inactive = total - active
        return {"total": total, "active": active, "inactive": inactive}
    
    stats = await get_stats()
    return JSON(stats)
