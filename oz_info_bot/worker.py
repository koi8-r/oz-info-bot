import asyncio

import aiohttp

from oz_info_bot.models import Response, Result


async def worker(q: asyncio.Queue[Result]) -> None:
    async with aiohttp.ClientSession(
        base_url='https://some.org', raise_for_status=True,
    ) as sess:
        while True:
            async with sess.get('/foo') as resp:
                r: Response = Response.parse_obj(await resp.json())
                for rr in (_ for _ in r.result if 'IVANOV' in _.name.upper()):
                    if rr.free_participants or rr.free_tickets:
                        q.put_nowait(rr)
            await asyncio.sleep(10)
