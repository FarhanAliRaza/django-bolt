from typing import Optional, List
import msgspec
import asyncio
from django_bolt import BoltAPI, JSON

api = BoltAPI()


class Item(msgspec.Struct):
    name: str
    price: float
    is_offer: Optional[bool] = None


@api.get("/")
async def read_root():
    return {"Hello": "World"}


@api.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@api.put("/items/{item_id}", response_model=dict)
async def update_item(item_id: int, item: Item) -> dict:
    return {"item_name": item.name, "item_id": item_id}


@api.get("/items100", response_model=list[Item])
async def items100() -> list[Item]:
    return [
        Item(name=f"item{i}", price=float(i), is_offer=(i % 2 == 0))
        for i in range(100)
    ]


# ==== Benchmarks: JSON parsing/validation & slow async op ====
class BenchPayload(msgspec.Struct):
    title: str
    count: int
    items: List[Item]


@api.post("/bench/parse")
async def bench_parse(payload: BenchPayload):
    # msgspec validates and decodes in one pass; just return minimal data
    return {"ok": True, "n": len(payload.items), "count": payload.count}


@api.get("/bench/slow")
async def bench_slow(ms: Optional[int] = 100):
    # Simulate slow I/O (network) with asyncio.sleep
    delay = max(0, (ms or 0)) / 1000.0
    await asyncio.sleep(delay)
    return {"ok": True, "ms": ms}
