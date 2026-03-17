import asyncio
import aiohttp
import time

BASE_URL = "http://localhost:8003"
API_KEY = "gok1-secret#*&%-key"
HEADERS = {"X-API-Key": API_KEY}

PAYLOAD = {
    "source_language": "eng_Latn",
    "target_language": "hin_Deva",
    "text": "The weather in Mumbai is warm and humid during the monsoon season.",
}


async def _post(session, payload):
    start = time.monotonic()
    async with session.post(f"{BASE_URL}/translate", json=payload, headers=HEADERS) as r:
        body = await r.json()
        return r.status, body, time.monotonic() - start


async def _run_concurrent(n):
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[_post(session, PAYLOAD) for _ in range(n)])
    return results


def test_concurrent_requests():
    """All N concurrent requests must succeed and the server must stay responsive."""
    n = 5
    results = asyncio.run(_run_concurrent(n))

    for i, (status, body, elapsed) in enumerate(results):
        assert status == 200, f"Request {i} failed with status {status}: {body}"
        assert "translated_text" in body, f"Request {i} missing translated_text"

    print(f"\n{n} concurrent requests all succeeded")
    for i, (_, _, elapsed) in enumerate(results):
        print(f"  request {i+1}: {elapsed:.2f}s")
