from typing import Any

import aiohttp

from app.core.exeptions import exceptions_http


class AsyncHttpClient:
    def __init__(self):
        self.session = None

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ):
        try:
            async with self.session.get(
                url, headers=headers, params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            exceptions_http.handle_aiohttp_error(e)
        except aiohttp.ClientConnectionError as e:
            raise exceptions_http.ExternalServiceError(
                f"Error connecting to the external service: {e}"
            )
        except aiohttp.ServerDisconnectedError as e:
            raise exceptions_http.ExternalServiceError(
                f"External service disconnected unexpectedly: {e}"
            )
        except aiohttp.ClientError as e:
            raise exceptions_http.ExternalServiceError(
                f"Error interacting with the external service: {e}"
            )

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
