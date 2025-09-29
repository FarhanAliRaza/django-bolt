import asyncio
import time
import httpx

async def test_streaming():
    """Test current streaming performance"""
    async with httpx.AsyncClient() as client:
        start = time.time()
        tasks = []
        for _ in range(100):
            tasks.append(client.get("http://localhost:8000/stream"))
        responses = await asyncio.gather(*tasks)
        end = time.time()
        
        total_bytes = sum(len(r.content) for r in responses)
        rps = 100 / (end - start)
        print(f"Streaming: {rps:.1f} RPS, {total_bytes} bytes in {end-start:.3f}s")

async def test_collected():
    """Test if we just returned all data at once"""
    async with httpx.AsyncClient() as client:
        start = time.time()
        tasks = []
        for _ in range(100):
            # Test with the root endpoint which returns immediately
            tasks.append(client.get("http://localhost:8000/"))
        responses = await asyncio.gather(*tasks)
        end = time.time()
        
        total_bytes = sum(len(r.content) for r in responses)
        rps = 100 / (end - start)
        print(f"Non-streaming: {rps:.1f} RPS, {total_bytes} bytes in {end-start:.3f}s")

if __name__ == "__main__":
    asyncio.run(test_streaming())
    asyncio.run(test_collected())