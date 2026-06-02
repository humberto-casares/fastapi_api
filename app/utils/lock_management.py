import asyncio
from collections import Counter
from datetime import timedelta

from app.db.common import configure_logger
from app.db.db import AsyncConnection, retry_db
from app.utils.definitions import SERVICE_NAME
from app.utils.params import DB_RETRIES, DB_WAIT_FACTOR
from app.utils.definitions import mx_now

logger = configure_logger(service_name=f'{SERVICE_NAME}-service')


class LockManagement(object):
    LOCK = "INSERT INTO lock_management(name, expire_at) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING"
    DELETE = "DELETE FROM lock_management WHERE name = $1"

    def __init__(self, name: str, db: AsyncConnection,
                 counter: Counter = None, wait: float = 1, expire: int = 300):
        self._name = name
        self._wait = wait
        self._expire = expire
        self._counter = counter
        self._db = db

    @retry_db(times=DB_RETRIES, wait_factor=DB_WAIT_FACTOR)
    async def _execute_job(self) -> bool:
        try:
            async with self._db.cursor() as cursor:
                if 1 == await cursor.execute(self.LOCK,
                                             (self.name,
                                              mx_now().replace(tzinfo=None) + timedelta(seconds=self._expire))):
                    return True
        except Exception as er:
            await logger.awarning("locking task: {0} error {1}".format(self.name, str(er)))
        return False

    async def lock(self) -> bool:
        while await self._execute_job() is False:
            await asyncio.sleep(self._wait)
        return True

    async def can_lock(self) -> bool:
        return await self._execute_job()

    @retry_db(times=DB_RETRIES, wait_factor=DB_WAIT_FACTOR)
    async def unlock(self) -> None:
        async with self._db.cursor() as cursor:
            await cursor.execute(sql=self.DELETE, params=[self.name])

    @property
    def name(self) -> str:
        return self._name

    @property
    def wait(self) -> float:
        return self._wait

    @property
    def expire(self) -> int:
        return self._expire
