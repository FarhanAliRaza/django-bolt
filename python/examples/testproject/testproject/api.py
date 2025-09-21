from typing import Optional, List, Annotated
import msgspec
import asyncio
from django_bolt import BoltAPI, JSON
from django_bolt.param_functions import Header, Cookie
from django_bolt.responses import PlainText, HTML, Redirect
from django_bolt.exceptions import HTTPException

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


# ==== Benchmark endpoints for Header/Cookie/Exception/HTML/Redirect ====
@api.get("/header")
async def get_header(x: Annotated[str, Header(alias="x-test")]):
    return PlainText(x)


@api.get("/cookie")
async def get_cookie(val: Annotated[str, Cookie(alias="session")]):
    return PlainText(val)


@api.get("/exc")
async def raise_exc():
    raise HTTPException(status_code=404, detail="Not found")


@api.get("/html")
async def get_html():
    return HTML("<h1>Hello</h1>")


@api.get("/redirect")
async def get_redirect():
    return Redirect("/", status_code=302)
