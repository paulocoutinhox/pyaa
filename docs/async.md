# Async Support

This project supports asynchronous execution for high-performance API endpoints using FastAPI with async/await patterns.

## Overview

PyAA provides both synchronous and asynchronous route support, allowing you to choose the right approach based on your specific needs:

- **Synchronous routes** - Traditional blocking I/O, suitable for most use cases
- **Asynchronous routes** - For high-volume endpoints with heavy I/O operations

## When to Use Async

Use async routes when:

- High volume of concurrent requests
- Heavy I/O operations (external APIs, file processing, etc.)
- Real-time features requiring concurrency
- Performance optimization is critical

## When NOT to Use Async

Avoid async routes when:

- Simple CRUD operations
- Low traffic endpoints
- Internal admin tools
- Maintenance scripts
- Complex legacy ORM code that's difficult to adapt

Async is **optional and strategic**, not mandatory. Use it where it provides clear benefits.

## 1. Route Definitions

### Rule

- Synchronous routes use `def`
- Asynchronous routes use `async def`

### Pattern

```python
@router.get("/example")
async def example_async(request):
    # async implementation
    ...
```

### Example

```python
from fastapi import APIRouter
from apps.api.banner.schemas import BannerSchema
from apps.banner.helpers import BannerHelper

router = APIRouter()

@router.get("/", response_model=list[BannerSchema])
async def list_banners(zone: str, language: str = None, site: int = None):
    banners = await BannerHelper.get_banners_async(
        zone=zone,
        language=language,
        site_id=site,
    )
    return banners
```

## 2. ORM Usage (Django 5+/6)

### Rule

- **DO NOT** use synchronous ORM inside `async def` functions
- **USE** async ORM methods provided by Django

### Correct Usage

```python
# single object
banner = await Banner.objects.aget(token=token)

# filter and get all
banners = await Banner.objects.filter(active=True).aall()

# check existence
exists = await Banner.objects.filter(token=token).aexists()

# count
count = await Banner.objects.filter(active=True).acount()

# update
await Banner.objects.filter(id=banner_id).aupdate(views=F('views') + 1)

# delete
await Banner.objects.filter(id=banner_id).adelete()

# async comprehension
banners = [b async for b in Banner.objects.filter(zone=zone)]
```

### Incorrect Usage

```python
# ❌ this blocks the event loop
banner = Banner.objects.get(token=token)

# ❌ synchronous iteration
for banner in Banner.objects.all():
    ...
```

## 3. Bridging Async and Sync Code

Django provides utilities to convert between async and sync code when necessary. These are essential when:

- Using sync code that doesn't have async support
- Working with ORM features not yet async-compatible
- Integrating legacy synchronous code in async routes
- Calling async functions from synchronous contexts

### sync_to_async

Use `sync_to_async` to call synchronous functions from async code.

#### When to Use

- ORM operations without async support (complex queries, aggregations)
- Django features not yet async-compatible
- Third-party libraries that are synchronous
- Complex transactions with multiple related objects
- Legacy code that cannot be easily converted

#### Basic Usage

```python
from asgiref.sync import sync_to_async

# convert a synchronous function
@sync_to_async
def get_banner_with_relations(token):
    return Banner.objects.select_related('site', 'language').get(token=token)

# use in async route
@router.get("/banner/{token}")
async def get_banner(token: str):
    banner = await get_banner_with_relations(token)
    return banner
```

#### Inline Usage

```python
# convert on-the-fly
async def process_banner(token):
    banner = await sync_to_async(Banner.objects.get)(token=token)
    return banner
```

#### Thread-Safe Option

By default, `sync_to_async` runs in a thread pool. Use `thread_sensitive=True` for database operations:

```python
@sync_to_async(thread_sensitive=True)
def complex_database_operation():
    # multiple related queries
    banner = Banner.objects.select_related('site').prefetch_related('tags').get(id=1)
    # ... more operations
    return banner
```

#### Class Methods

```python
class BannerHelper:

    @staticmethod
    @sync_to_async
    def get_banner_with_complex_query(filters):
        # complex query not available in async ORM
        return Banner.objects.filter(
            **filters
        ).select_related(
            'site', 'language'
        ).prefetch_related(
            'tags', 'images'
        ).annotate(
            click_rate=F('clicks') / F('views')
        ).first()
```

#### Real-World Examples

**Example 1: Complex Aggregation**

```python
from django.db.models import Count, Avg, Sum
from asgiref.sync import sync_to_async

@sync_to_async
def get_banner_statistics(zone):
    # get banner statistics with aggregation (not yet async)
    return Banner.objects.filter(zone=zone).aggregate(
        total_views=Sum('views'),
        total_clicks=Sum('clicks'),
        avg_views=Avg('views'),
        banner_count=Count('id')
    )

@router.get("/stats/{zone}")
async def banner_stats(zone: str):
    stats = await get_banner_statistics(zone)
    return stats
```

**Example 2: Select/Prefetch Related**

```python
@sync_to_async
def get_banners_with_relations(zone):
    # get banners with optimized queries
    return list(
        Banner.objects.filter(zone=zone)
        .select_related('site', 'language')
        .prefetch_related('tags')
    )

@router.get("/banners/{zone}")
async def list_banners_with_relations(zone: str):
    banners = await get_banners_with_relations(zone)
    return banners
```

**Example 3: Transactions**

```python
from django.db import transaction

@sync_to_async
@transaction.atomic
def create_banner_with_relations(data):
    # create banner with related objects in transaction
    banner = Banner.objects.create(
        zone=data['zone'],
        title=data['title'],
        active=True
    )

    # create related objects
    for tag_name in data.get('tags', []):
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        banner.tags.add(tag)

    return banner

@router.post("/banners")
async def create_banner(data: BannerCreateSchema):
    banner = await create_banner_with_relations(data.dict())
    return banner
```

### async_to_sync

Use `async_to_sync` to call asynchronous functions from synchronous code.

#### When to Use

- Calling async helpers from sync views
- Running async code in Django management commands
- Testing async functions in synchronous test cases
- Integrating async code in sync legacy systems
- Using async functions in Django signals

#### Basic Usage

```python
from asgiref.sync import async_to_sync

# call async function from sync context
def sync_view(request):
    banners = async_to_sync(BannerHelper.get_banners_async)("home")
    return render(request, 'banners.html', {'banners': banners})
```

#### Management Commands

```python
from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = 'Process banners asynchronously'

    def handle(self, *args, **options):
        # call async function from sync management command
        result = async_to_sync(self.process_banners_async)()
        self.stdout.write(f"Processed {result} banners")

    async def process_banners_async(self):
        banners = await Banner.objects.filter(active=True).aall()
        count = 0
        async for banner in Banner.objects.filter(active=True):
            # process each banner
            await self.update_banner_stats(banner)
            count += 1
        return count

    async def update_banner_stats(self, banner):
        await Banner.objects.filter(id=banner.id).aupdate(
            last_processed=timezone.now()
        )
```

#### Django Signals

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Banner)
def banner_saved(sender, instance, created, **kwargs):
    if created:
        # call async function from signal
        async_to_sync(notify_new_banner)(instance)

async def notify_new_banner(banner):
    # send async notification
    async with httpx.AsyncClient() as client:
        await client.post(
            'https://api.example.com/notify',
            json={'banner_id': banner.id}
        )
```

#### Testing

```python
from django.test import TestCase
from asgiref.sync import async_to_sync

class BannerTestCase(TestCase):

    def test_async_helper_from_sync_test(self):
        # setup
        Banner.objects.create(zone="home", active=True)

        # call async function in sync test
        banners = async_to_sync(BannerHelper.get_banners_async)("home")

        # assert
        self.assertEqual(len(banners), 1)
```

### Important Considerations

#### Performance Impact

- Both converters add overhead - avoid excessive conversions
- Prefer native async or sync approaches when possible
- Use `sync_to_async` sparingly in hot paths

#### Thread Safety

```python
# for database operations, use thread_sensitive=True
@sync_to_async(thread_sensitive=True)
def database_operation():
    # database queries here
    pass

# for cpu-bound tasks, use thread_sensitive=False (default)
@sync_to_async(thread_sensitive=False)
def cpu_intensive_task():
    # computation here
    pass
```

#### Nested Calls

Avoid deeply nested async/sync conversions:

```python
# ❌ bad - nested conversions
async def bad_example():
    result = await sync_to_async(
        lambda: async_to_sync(another_async_function)()
    )()

# ✔ good - direct async chain
async def good_example():
    result = await another_async_function()
```

### Decision Matrix

Use this matrix to decide which approach to use:

| Scenario | Solution | Example |
|----------|----------|---------|
| Async route needs ORM feature without async support | `sync_to_async` | Complex aggregations, prefetch_related |
| Async route needs sync third-party library | `sync_to_async` | Legacy libraries, file operations |
| Sync view needs async helper | `async_to_sync` | Calling async API clients |
| Management command needs async code | `async_to_sync` | Batch processing with async ORM |
| Signal needs to call async function | `async_to_sync` | Sending async notifications |
| Testing async code in sync tests | `async_to_sync` | Unit tests |

## 4. Helper Functions

### Naming Convention

- Async helpers must have `_async` suffix
- Sync helpers continue without suffix

### Organization Pattern

```python
# helpers/banner_helper.py

class BannerHelper:

    # synchronous (existing/legacy)
    @staticmethod
    def get_banner_by_token(token):
        return Banner.objects.get(token=token)

    # asynchronous (new)
    @staticmethod
    async def get_banner_by_token_async(token):
        return await Banner.objects.aget(token=token)
```

### Complete Example

```python
class BannerHelper:

    @staticmethod
    async def get_banners_async(zone, language=None, site_id=None):
        # retrieve banners asynchronously based on zone, language, and site
        qs = Banner.objects.filter(zone=zone, active=True)

        if language:
            qs = qs.filter(language=language)

        if site_id:
            qs = qs.filter(site_id=site_id)

        return [b async for b in qs]

    @staticmethod
    async def increment_banner_views_async(token):
        # increment banner view count asynchronously
        await Banner.objects.filter(token=token).aupdate(
            views=F('views') + 1
        )

    @staticmethod
    async def get_active_banners_count_async(zone):
        # count active banners in a zone asynchronously
        return await Banner.objects.filter(
            zone=zone,
            active=True
        ).acount()
```

## 5. Best Practices

### Keep Business Logic in Helpers

Avoid heavy logic inside route functions:

```python
# ✔ correct - logic in helper
@router.get("/banners")
async def list_banners(zone: str):
    return await BannerHelper.get_banners_async(zone=zone)

# ❌ incorrect - logic in route
@router.get("/banners")
async def list_banners(zone: str):
    qs = Banner.objects.filter(zone=zone, active=True)
    banners = [b async for b in qs]
    # ... more processing
    return banners
```

### Error Handling

```python
from fastapi import HTTPException, status

@router.get("/banner/{token}")
async def get_banner(token: str):
    try:
        banner = await BannerHelper.get_banner_by_token_async(token)
        return banner
    except Banner.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner not found"
        )
```

### Async with External APIs

```python
import httpx

class ExternalAPIHelper:

    @staticmethod
    async def fetch_data_async(url):
        # fetch data from external API asynchronously
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

## 6. Running Async Server

### Development

```bash
make run-async
```

Or directly:

```bash
uvicorn pyaa.asgi:application --reload --host 0.0.0.0 --port 8000
```

### Production

Use Gunicorn with Uvicorn workers:

```bash
gunicorn pyaa.asgi:application \
  --bind 0.0.0.0:8000 \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4
```

See [Docker documentation](docker.md) for async deployment with Docker.

## 7. Testing Async Code

### Test Example

```python
from django.test import TransactionTestCase
from asgiref.sync import async_to_sync

class BannerAsyncTestCase(TransactionTestCase):

    def test_get_banners_async(self):
        # setup
        Banner.objects.create(zone="home", active=True)

        # execute async function in sync test
        banners = async_to_sync(BannerHelper.get_banners_async)("home")

        # assert
        self.assertEqual(len(banners), 1)
```

### Async Test (Django 4.2+)

```python
from django.test import TransactionTestCase

class BannerAsyncTestCase(TransactionTestCase):

    async def test_get_banners_async(self):
        # setup
        await Banner.objects.acreate(zone="home", active=True)

        # execute
        banners = await BannerHelper.get_banners_async("home")

        # assert
        self.assertEqual(len(banners), 1)
```

## 8. Common Patterns

### Pagination with Async

```python
from apps.api.banner.schemas import PaginatedResponse

@router.get("/banners", response_model=PaginatedResponse)
async def list_banners_paginated(limit: int = 10, offset: int = 0):
    total = await Banner.objects.filter(active=True).acount()
    banners = await Banner.objects.filter(active=True)[offset:offset + limit].aall()

    return {
        "count": total,
        "items": banners,
    }
```

### Multiple Async Operations

```python
import asyncio

async def get_dashboard_data(user_id):
    # run multiple queries concurrently
    banners, logs, stats = await asyncio.gather(
        BannerHelper.get_user_banners_async(user_id),
        SystemLogHelper.get_recent_logs_async(user_id),
        StatsHelper.get_user_stats_async(user_id),
    )

    return {
        "banners": banners,
        "logs": logs,
        "stats": stats,
    }
```

### Async with Transactions

```python
from django.db import transaction
from asgiref.sync import sync_to_async

@sync_to_async
@transaction.atomic
def create_banner_with_related_data(data):
    banner = Banner.objects.create(**data)
    # create related objects
    return banner

@router.post("/banners")
async def create_banner(data: BannerCreateSchema):
    banner = await create_banner_with_related_data(data.dict())
    return banner
```

## 9. Pre-Flight Checklist

Before creating an async route, verify:

1. Route uses `async def`
2. No synchronous ORM calls inside the route (unless wrapped with `sync_to_async`)
3. Helpers use `_async` suffix for async methods
4. ORM uses async methods: `aget`, `aall`, `aexists`, `aupdate`, `adelete`, `acount`
5. If using ORM features without async support (aggregations, select_related, prefetch_related), wrap with `sync_to_async`
6. Third-party sync libraries are wrapped with `sync_to_async` if called from async code
7. Concurrency benefit is clear and measurable
8. Error handling is implemented
9. Business logic is in helpers, not routes
10. Performance benchmarks justify the async approach

### Common Checklist Scenarios

**Scenario 1: Simple async route with native async ORM**

```python
# ✔ all checks pass
@router.get("/banners")
async def list_banners(zone: str):
    # uses async orm - no sync_to_async needed
    return await BannerHelper.get_banners_async(zone=zone)
```

**Scenario 2: Async route needing select_related**

```python
# ✔ correct - uses sync_to_async decorator
from asgiref.sync import sync_to_async

@sync_to_async
def get_banners_with_relations(zone):
    return list(
        Banner.objects.filter(zone=zone)
        .select_related('site', 'language')
    )

@router.get("/banners/{zone}")
async def list_banners(zone: str):
    return await get_banners_with_relations(zone)
```

**Scenario 2.1: Async route with inline sync_to_async**

```python
# ✔ correct - uses sync_to_async inline
from asgiref.sync import sync_to_async

@router.get("/banners/{zone}")
async def list_banners(zone: str):
    # inline usage - wraps the sync function call
    banners = await sync_to_async(
        lambda: list(
            Banner.objects.filter(zone=zone)
            .select_related('site', 'language')
            .prefetch_related('tags')
        )
    )()
    return banners
```

**Scenario 3: Async route with aggregations**

```python
# ✔ correct - wraps aggregation with sync_to_async
from django.db.models import Count, Sum
from asgiref.sync import sync_to_async

@sync_to_async
def get_banner_stats(zone):
    return Banner.objects.filter(zone=zone).aggregate(
        total_views=Sum('views'),
        total_clicks=Sum('clicks'),
        count=Count('id')
    )

@router.get("/stats/{zone}")
async def banner_stats(zone: str):
    return await get_banner_stats(zone)
```

## 10. Performance Considerations

### Benchmark Before and After

Always measure performance improvements:

```python
# before (sync): 500ms average response time
# after (async): 150ms average response time
# improvement: 70% reduction
```

### Monitor Event Loop

- Avoid blocking operations in async functions
- Use async libraries for I/O (httpx, aiofiles, etc.)
- Keep CPU-intensive tasks in background workers

### Database Connection Pooling

Configure appropriate database connection settings in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

## 11. Quick Reference

### Async ORM Methods

| Sync Method | Async Equivalent |
|------------|------------------|
| `.get()` | `.aget()` |
| `.all()` | `.aall()` |
| `.filter()...` | `.filter()...` (still chainable) |
| `.exists()` | `.aexists()` |
| `.count()` | `.acount()` |
| `.create()` | `.acreate()` |
| `.update()` | `.aupdate()` |
| `.delete()` | `.adelete()` |
| `.first()` | `.afirst()` |
| `.last()` | `.alast()` |
| `for x in qs:` | `async for x in qs:` |

### ORM Features Requiring sync_to_async

These features don't have async support yet and need `sync_to_async`:

- `select_related()` / `prefetch_related()`
- `aggregate()` / `annotate()` with complex expressions
- `values()` / `values_list()`
- `bulk_create()` / `bulk_update()`
- Custom managers with complex logic
- Raw SQL queries
- Transaction management (`transaction.atomic`)

### Example Template

Use this template as a starting point for async routes:

```python
from fastapi import APIRouter
from asgiref.sync import sync_to_async
from apps.myapp.models import MyModel
from apps.api.myapp.schemas import MySchema

router = APIRouter()

# helper functions
class MyHelper:

    @staticmethod
    async def get_items_async(filters):
        # simple async query
        qs = MyModel.objects.filter(**filters)
        return [item async for item in qs]

    @staticmethod
    @sync_to_async
    def get_items_with_relations(filters):
        # complex query requiring sync_to_async
        return list(
            MyModel.objects.filter(**filters)
            .select_related('related_model')
            .prefetch_related('many_to_many')
        )

# routes
@router.get("/items", response_model=list[MySchema])
async def list_items(status: str = None):
    # list items with optional status filter
    filters = {}
    if status:
        filters['status'] = status

    # use simple async query
    items = await MyHelper.get_items_async(filters)
    return items

@router.get("/items-detailed", response_model=list[MySchema])
async def list_items_detailed():
    # list items with related data
    # use sync_to_async for complex query
    items = await MyHelper.get_items_with_relations({})
    return items
```

## Resources

- [Django Async Documentation](https://docs.djangoproject.com/en/stable/topics/async/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [asgiref Documentation](https://github.com/django/asgiref)
