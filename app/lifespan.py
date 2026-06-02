from yoyo import get_backend, read_migrations
from contextlib import asynccontextmanager
from urllib.parse import quote
from pathlib import Path
from fastapi import FastAPI
import asyncio
import anyio

from app.db.common import db_connection_uri, configure_logger
from app.utils.params import DB_POOL_MIN, DB_POOL_MAX
from app.utils.definitions import SERVICE_NAME
from app.db.db import AsyncConnection
from app.core.config import settings

# Get environment variables
db_host = settings.DB_HOST
db_name = settings.DB_NAME
db_password = settings.DB_PASSWORD
db_port = settings.DB_PORT
db_user = settings.DB_USER

# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
logger = configure_logger(service_name=f'{SERVICE_NAME}-service')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")

    try:
        logger.info(f"Migration started")
        backend = get_backend('postgres://{0}:{1}@{2}:{3}/{4}'.format(quote(db_user),
                                                                      quote(db_password),
                                                                      db_host,
                                                                      db_port,
                                                                      db_name))
        migrations_dir = Path(__file__).resolve().parent / "resource" / "migration"
        backend.apply_migrations(backend.to_apply(read_migrations(str(migrations_dir))))
        backend.connection.close()
        logger.info(f"Migration completed")
    except Exception as e:
        logger.exception(f"Migration Exception: {e}")

    limit = anyio.to_thread.current_default_thread_limiter()
    limit.total_tokens = 30000

    # User Register Async Queue
    app.state.task_queue = asyncio.Queue()

    # Database Async Connection
    app.state.db = AsyncConnection(uri=db_connection_uri(), log=logger, min=DB_POOL_MIN, max=DB_POOL_MAX)
    await app.state.db.new_pool()  # Ensure the connection pool is initialized

    yield

    # Shutdown
    if hasattr(app.state, "db") and app.state.db is not None:
        await app.state.db.close_pool()

    logger.info("lifespan sleep")
    await asyncio.sleep(1)
    logger.info("lifespan stopped")
