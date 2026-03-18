import asyncio
import aiohttp
import time
import random

BASE_URL = "http://localhost:8003"
API_KEY = "gok1-secret#*&%-key"
HEADERS = {"X-API-Key": API_KEY}

# Texts of varying lengths (300–1500 chars)
TEXTS = [
    "The monsoon season in India brings heavy rainfall across the country. Farmers eagerly await the rains.",
    "Ancient Indian mathematicians discovered the concept of zero and made foundational contributions to algebra and astronomy. The spice trade brought merchants from Arabia, China, and Europe to Indian shores for centuries.",
    "The history of ancient India spans thousands of years and encompasses a rich tapestry of cultures, religions, and civilizations. From the Indus Valley Civilization to the Maurya and Gupta empires, India has been home to some of the worlds oldest and most sophisticated societies. The subcontinent gave birth to major world religions including Hinduism, Buddhism, Jainism, and Sikhism.",
    "Modern India is the worlds largest democracy and one of the fastest growing economies. Its diverse population speaks hundreds of languages and follows dozens of religious traditions. Indian cinema, cuisine, and culture have spread across the globe and influenced millions of people worldwide. The country continues to grow rapidly in technology, infrastructure, and international influence.",
    "The Mughal Empire unified much of the subcontinent under a single administration and produced architectural masterpieces like the Taj Mahal. Colonial rule by the British fundamentally transformed Indian society, economy, and governance. The independence movement led by Mahatma Gandhi used nonviolent resistance to achieve freedom in 1947. After independence, India adopted a democratic constitution and began the long process of nation building. The early decades saw significant industrialization and the establishment of key public institutions.",
]

async def translate(session, text, idx):
    start = time.monotonic()
    payload = {
        "source_language": "eng_Latn",
        "target_language": "hin_Deva",
        "text": text,
    }
    async with session.post(f"{BASE_URL}/translate", json=payload, headers=HEADERS) as r:
        body = await r.json()
        elapsed = time.monotonic() - start
        ok = r.status == 200 and "translated_text" in body
        return idx, ok, elapsed, len(text), r.status

async def run():
    # Build 40 requests cycling through the texts
    requests = [(i, TEXTS[i % len(TEXTS)]) for i in range(40)]

    print(f"Sending {len(requests)} concurrent requests...\n")
    wall_start = time.monotonic()

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[translate(session, text, idx) for idx, text in requests])

    wall_total = time.monotonic() - wall_start

    # Sort by index for clean output
    results.sort(key=lambda x: x[0])

    passed = sum(1 for _, ok, *_ in results if ok)
    failed = len(results) - passed
    times = [elapsed for _, _, elapsed, *_ in results]

    print(f"{'#':>3}  {'chars':>6}  {'time':>7}  status")
    print("-" * 35)
    for idx, ok, elapsed, chars, status in results:
        flag = "✓" if ok else "✗"
        print(f"{idx+1:>3}  {chars:>6}  {elapsed:>6.2f}s  {flag} {status}")

    print(f"\n{'─'*35}")
    print(f"Total wall time : {wall_total:.2f}s")
    print(f"Passed          : {passed}/{len(results)}")
    print(f"Failed          : {failed}")
    print(f"Avg per request : {sum(times)/len(times):.2f}s")
    print(f"Min / Max       : {min(times):.2f}s / {max(times):.2f}s")

if __name__ == "__main__":
    asyncio.run(run())
