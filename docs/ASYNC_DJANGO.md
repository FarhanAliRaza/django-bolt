# Django Async ORM with Django-Bolt

Django-Bolt requires all handlers to be `async def` functions. This document explains how to work with Django's async ORM and what features are supported in async context.

## Table of Contents

- [Why Async-Only?](#why-async-only)
- [Django Async ORM Methods](#django-async-orm-methods)
- [Common Patterns](#common-patterns)
- [What Works](#what-works)
- [What Doesn't Work](#what-doesnt-work)
- [Workarounds](#workarounds)
- [Best Practices](#best-practices)

## Why Async-Only?

Django-Bolt enforces `async def` handlers for several reasons:

1. **Architecture**: The Rust/Actix server expects Python coroutines for optimal performance
2. **Django 5.0+ Support**: Modern Django has comprehensive async ORM support
3. **Performance**: Non-blocking I/O enables high concurrency (60k+ RPS)
4. **Future-Proof**: Django is moving toward async-first architecture

## Django Async ORM Methods

Django 5.2+ provides async versions of all QuerySet methods that execute database queries, prefixed with `a`:

### Single Object Operations

```python
# Get single object
user = await User.objects.aget(pk=1)

# Create object
user = await User.objects.acreate(
    username='john',
    email='john@example.com'
)

# Get or create
user, created = await User.objects.aget_or_create(
    username='john',
    defaults={'email': 'john@example.com'}
)

# Update or create
user, created = await User.objects.aupdate_or_create(
    username='john',
    defaults={'email': 'new@example.com'}
)

# Get first/last
first = await User.objects.afirst()
last = await User.objects.alast()

# Get earliest/latest by date field
earliest = await User.objects.aearliest('date_joined')
latest = await User.objects.alatest('date_joined')
```

### Bulk Operations

```python
# Bulk create
users = [
    User(username=f'user{i}', email=f'user{i}@example.com')
    for i in range(100)
]
created = await User.objects.abulk_create(users)

# Bulk update
users = await User.objects.filter(is_active=False).abulk_update(
    users,
    ['email', 'is_active']
)

# Get objects in bulk by IDs
users = await User.objects.ain_bulk([1, 2, 3, 4, 5])
```

### Query Operations

```python
# Count
total = await User.objects.acount()
active = await User.objects.filter(is_active=True).acount()

# Exists
exists = await User.objects.filter(username='john').aexists()

# Contains
contains = await User.objects.acontains(user_instance)

# Update
updated_count = await User.objects.filter(is_active=False).aupdate(is_active=True)

# Delete
deleted_count, _ = await User.objects.filter(username='temp').adelete()

# Aggregate
from django.db.models import Count, Avg
stats = await User.objects.aaggregate(
    total=Count('id'),
    avg_age=Avg('age')
)

# Query explanation
explanation = await User.objects.filter(is_active=True).aexplain()
```

### Iteration

```python
# Async iteration (Django 5.0+)
users = []
async for user in User.objects.filter(is_active=True):
    users.append(user)

# Async iterator for large datasets
async for user in User.objects.aiterator(chunk_size=1000):
    process(user)

# ✅ CONFIRMED: Works with values() and values_list()
async for data in User.objects.values('id', 'username'):
    print(data)  # {'id': 1, 'username': 'john'}

async for username in User.objects.values_list('username', flat=True):
    print(username)  # 'john'

# values_list() returns tuples when not flat
async for id, username in User.objects.values_list('id', 'username'):
    print(f"{id}: {username}")  # 1: john
```

### Model Instance Methods

```python
# Save instance
user = User(username='john', email='john@example.com')
await user.asave()

# Update and save
user.email = 'new@example.com'
await user.asave(update_fields=['email'])

# Delete instance
await user.adelete()

# Refresh from database
await user.arefresh_from_db()
```

### Related Object Methods

```python
# Many-to-Many operations
await user.groups.aset([group1, group2])
await user.groups.aadd(group3)
await user.groups.aremove(group1)
await user.groups.aclear()

# Get related objects
groups = []
async for group in user.groups.all():
    groups.append(group)
```

## Common Patterns

### Pagination

Django's `Paginator` class is sync-only. Build custom pagination instead:

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/users")
async def list_users(page: int = 1, page_size: int = 20):
    """Paginated user list"""
    offset = (page - 1) * page_size

    # Get total count
    total = await User.objects.acount()

    # Get page of users
    users = []
    async for user in User.objects.all()[offset:offset + page_size]:
        users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
```

### Filtering with Q Objects

```python
from django.db.models import Q

@api.get("/users/search")
async def search_users(q: str):
    """Search users by username or email"""
    results = []
    async for user in User.objects.filter(
        Q(username__icontains=q) | Q(email__icontains=q)
    )[:20]:
        results.append({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    return {"results": results, "count": len(results)}
```

### Aggregation

```python
from django.db.models import Count, Avg, Max, Min

@api.get("/users/stats")
async def user_stats():
    """Get user statistics"""
    stats = await User.objects.aaggregate(
        total_users=Count('id'),
        active_users=Count('id', filter=Q(is_active=True)),
        avg_age=Avg('age'),
        newest_user=Max('date_joined'),
        oldest_user=Min('date_joined')
    )

    return stats
```

### Authentication

```python
from django.contrib.auth import aauthenticate

@api.post("/login")
async def login(username: str, password: str):
    """Login endpoint using async auth"""
    user = await aauthenticate(username=username, password=password)

    if user is not None:
        return {
            "success": True,
            "user_id": user.id,
            "username": user.username
        }

    return {"success": False, "error": "Invalid credentials"}
```

### Returning QuerySets Directly

Django-Bolt automatically handles QuerySet async iteration when you return them:

```python
from users.models import User
import msgspec

class UserSchema(msgspec.Struct):
    id: int
    username: str
    email: str

@api.get("/users")
async def list_users() -> list[UserSchema]:
    """Return QuerySet directly - Django-Bolt handles iteration"""
    # This works! Django-Bolt uses async for iteration automatically
    return User.objects.all()[:10]
```

The binding layer (`python/django_bolt/binding.py:279-284`) detects QuerySets and uses `async for` to iterate them.

## What Works

### ✅ Fully Supported in Async Context

| Feature                    | Status   | Notes                                         |
| -------------------------- | -------- | --------------------------------------------- |
| **QuerySet iteration**     | ✅ Works | Use `async for`                               |
| **Filtering**              | ✅ Works | `filter()`, `exclude()`, `Q()` objects        |
| **Sorting**                | ✅ Works | `order_by()`, `distinct()`                    |
| **Aggregation**            | ✅ Works | Use `await .aaggregate()`, `await .acount()`  |
| **Single object ops**      | ✅ Works | Use `await .aget()`, `await .acreate()`, etc. |
| **Bulk operations**        | ✅ Works | Use `await .abulk_create()`, etc.             |
| **select_related()**       | ✅ Works | With `async for` iteration                    |
| **only()/defer()**         | ✅ Works | Query optimization works                      |
| **values()/values_list()** | ✅ Works | With `async for` iteration                    |
| **Django Cache**           | ✅ Works | All cache operations work                     |
| **Django Forms**           | ✅ Works | Validation and cleaning work                  |
| **Django Auth**            | ✅ Works | Use `await aauthenticate()`                   |

## What Doesn't Work

### ❌ Not Supported (Requires Workarounds)

| Feature                | Status   | Error                      | Workaround              |
| ---------------------- | -------- | -------------------------- | ----------------------- |
| **Paginator**          | ❌ Fails | `SynchronousOnlyOperation` | Build manual pagination |
| **Transactions**       | ❌ Fails | `SynchronousOnlyOperation` | Use `sync_to_async()`   |
| **prefetch_related()** | ❌ Fails | `SynchronousOnlyOperation` | Use `select_related()`  |
| **Sync ORM methods**   | ❌ Fails | `SynchronousOnlyOperation` | Use async versions      |

## Workarounds

### Transactions

Django doesn't support `async with transaction.atomic()` yet. Use `sync_to_async()`:

```python
from asgiref.sync import sync_to_async
from django.db import transaction

@api.post("/transfer")
async def transfer_funds(from_user_id: int, to_user_id: int, amount: float):
    """Transfer funds between users in a transaction"""

    @sync_to_async
    def do_transfer():
        with transaction.atomic():
            from_user = User.objects.get(pk=from_user_id)
            to_user = User.objects.get(pk=to_user_id)

            from_user.balance -= amount
            to_user.balance += amount

            from_user.save()
            to_user.save()

            return {"success": True}

    return await do_transfer()
```

### Prefetch Related

Use `select_related()` instead, or wrap in `sync_to_async()`:

```python
# ✅ GOOD: Use select_related
@api.get("/posts")
async def list_posts():
    """List posts with authors (using select_related)"""
    posts = []
    async for post in Post.objects.select_related('author').all()[:10]:
        posts.append({
            "id": post.id,
            "title": post.title,
            "author": post.author.username
        })
    return {"posts": posts}

# ⚠️ ALTERNATIVE: Use sync_to_async for prefetch_related
@api.get("/users-with-groups")
async def users_with_groups():
    """Get users with prefetched groups"""
    from asgiref.sync import sync_to_async

    @sync_to_async
    def get_users_with_groups():
        users = User.objects.prefetch_related('groups').all()[:10]
        return list(users)  # Force evaluation in sync context

    users = await get_users_with_groups()

    # Now process in async context
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "groups": [g.name for g in user.groups.all()]
        })

    return {"users": result}
```

### Blocking Operations

For CPU-intensive or blocking I/O operations, use `asyncio.to_thread()`:

```python
import asyncio
import requests  # Blocking HTTP library

@api.get("/external-data")
async def fetch_external():
    """Fetch data from external API"""
    # Run blocking request in thread pool
    response = await asyncio.to_thread(
        requests.get,
        'https://api.example.com/data'
    )
    return response.json()
```

## Best Practices

### DO ✅

1. **Use async ORM methods everywhere**

   ```python
   user = await User.objects.aget(pk=1)  # ✅
   ```

2. **Use `async for` to iterate QuerySets**

   ```python
   async for user in User.objects.all():  # ✅
       process(user)
   ```

3. **Use `select_related()` for joins**

   ```python
   async for post in Post.objects.select_related('author'):  # ✅
       print(post.author.name)
   ```

4. **Return QuerySets directly from handlers**

   ```python
   @api.get("/users")
   async def list_users() -> list[UserSchema]:
       return User.objects.all()[:10]  # ✅ Django-Bolt handles iteration
   ```

5. **Use `sync_to_async` for unsupported features**

   ```python
   from asgiref.sync import sync_to_async

   result = await sync_to_async(sync_function)()  # ✅
   ```

### DON'T ❌

1. **Don't use sync ORM methods**

   ```python
   user = User.objects.get(pk=1)  # ❌ Raises SynchronousOnlyOperation
   ```

2. **Don't use sync iteration**

   ```python
   for user in User.objects.all():  # ❌ Raises SynchronousOnlyOperation
       process(user)
   ```

3. **Don't use Django Paginator**

   ```python
   from django.core.paginator import Paginator
   paginator = Paginator(queryset, 20)  # ❌ Fails in async context
   ```

4. **Don't try async transactions**

   ```python
   async with transaction.atomic():  # ❌ Not supported
       await user.asave()
   ```

5. **Don't use `prefetch_related()`**
   ```python
   queryset.prefetch_related('groups')  # ❌ Fails in async context
   ```

### Performance Tips

1. **Minimize Database Queries**

   - Use `select_related()` for ForeignKey/OneToOne
   - Use `only()` to fetch specific fields
   - Use `defer()` to exclude heavy fields

2. **Use Bulk Operations**

   ```python
   # ✅ Good: Single query
   await User.objects.abulk_create(users)

   # ❌ Bad: N queries
   for user_data in users:
       await User.objects.acreate(**user_data)
   ```

3. **Batch Aggregations**

   ```python
   # ✅ Good: Single query
   stats = await User.objects.aaggregate(
       total=Count('id'),
       active=Count('id', filter=Q(is_active=True))
   )

   # ❌ Bad: Multiple queries
   total = await User.objects.acount()
   active = await User.objects.filter(is_active=True).acount()
   ```

4. **Use QuerySet Slicing**

   ```python
   # ✅ Good: Limit in database
   async for user in User.objects.all()[:100]:
       process(user)

   # ❌ Bad: Fetch all, limit in Python
   users = []
   async for user in User.objects.all():
       users.append(user)
       if len(users) >= 100:
           break
   ```

## Migration from Sync Django

If you're migrating from traditional Django views:

| Sync Code                  | Async Code                        |
| -------------------------- | --------------------------------- |
| `User.objects.get(pk=1)`   | `await User.objects.aget(pk=1)`   |
| `User.objects.create(...)` | `await User.objects.acreate(...)` |
| `User.objects.count()`     | `await User.objects.acount()`     |
| `for u in queryset:`       | `async for u in queryset:`        |
| `list(queryset)`           | `[u async for u in queryset]`     |
| `authenticate(...)`        | `await aauthenticate(...)`        |

## Django Version Compatibility

| Django Version | Async ORM Support                        |
| -------------- | ---------------------------------------- |
| Django 3.1     | Basic async views, no ORM                |
| Django 4.0     | Async ORM queries added                  |
| Django 4.1     | More async methods (acreate, aget, etc.) |
| Django 4.2     | Bulk async operations                    |
| Django 5.0     | **async for on QuerySets**               |
| Django 5.1     | Expanded async ORM coverage              |
| Django 5.2     | **Recommended for Django-Bolt**          |

**Minimum requirement**: Django 5.0+ for full async ORM support.

## Additional Resources

- [Django Async Documentation](https://docs.djangoproject.com/en/5.2/topics/async/)
- [QuerySet API Reference](https://docs.djangoproject.com/en/5.2/ref/models/querysets/)
- [Django-Bolt Examples](/python/example/testproject/api.py)

## Summary

Django-Bolt's `async def` requirement is not a limitation - it's a feature that leverages Django's modern async capabilities:

- ✅ All core API features work (CRUD, filtering, pagination, aggregation)
- ✅ High performance (60k+ RPS)
- ✅ Clean, explicit code
- ⚠️ Only limitations: transactions and prefetch (workarounds available)

**You don't need sync `def` handlers** - async covers all use cases!
