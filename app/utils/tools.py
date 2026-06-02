from tenacity import wait_fixed, stop_after_attempt, AsyncRetrying
from typing import Optional
import asyncio
import aiohttp

from app.utils.params import WAIT_RETRIES, MAX_RETRIES
from app.utils.definitions import SERVICE_NAME
from app.db.common import configure_logger

logger = configure_logger(service_name=SERVICE_NAME)


async def async_get_request(url: str, params: dict = None,
                            headers: Optional[dict] = None,
                            time_out: int = 7) -> Optional[dict]:
    async for attempt in AsyncRetrying(stop=stop_after_attempt(MAX_RETRIES),
                                       wait=wait_fixed(WAIT_RETRIES)):
        with attempt:
            try:
                async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=time_out), headers=headers) as session:
                    async with session.get(url=url, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                pass  # this helps to handle netter the TimeoutError exception (have a line after the ClientSession)
            except asyncio.TimeoutError:
                await logger.awarning(f"TimeoutError: {url}")
                return None
            except Exception as er:
                await logger.ainfo(f"GET Request ERROR: ", er)
                raise er


async def async_post_request(url: str, data: Optional[str] = None,
                             headers: Optional[dict] = None,
                             time_out: int = 7) -> Optional[dict]:
    async for attempt in AsyncRetrying(stop=stop_after_attempt(MAX_RETRIES),
                                       wait=wait_fixed(WAIT_RETRIES)):
        with attempt:
            try:
                async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=time_out), headers=headers) as session:
                    async with session.post(url=url, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
                pass  # this helps to handle netter the TimeoutError exception (have a line after the ClientSession)
            except asyncio.TimeoutError:
                await logger.awarning(f"TimeoutError: {url}")
                return None
            except Exception as er:
                await logger.ainfo(f"Post Request ERROR: ", er)
                raise er
