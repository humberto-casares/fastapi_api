from contextlib import asynccontextmanager
import functools
import asyncio
import time

import asyncpg
import orjson

from . import sqlop
from .common import configure_logger


class RetryException(Exception):
    pass


def retry_db(fn=None, *, times=5, wait_factor=1.2):
    def _decorate(function):
        @functools.wraps(function)
        async def wrapped_function(*args, **kwargs):
            log = configure_logger(__file__)
            attempts = 0
            start_time = time.time()

            while attempts < times:
                try:
                    return await function(*args, **kwargs)
                except (
                        asyncpg.InterfaceError, asyncpg.PostgresError, asyncpg.DataError,
                        asyncpg.InternalServerError, asyncpg.CannotConnectNowError, asyncpg.ConnectionDoesNotExistError,
                        asyncpg.ConnectionFailureError, asyncpg.ConnectionRejectionError,
                        asyncpg.ClientCannotConnectError, ConnectionRefusedError
                ) as error:
                    attempts += 1
                    wait_time = min(20, attempts if attempts < 2 else wait_factor ** attempts)
                    await log.awarning(
                        f"DB operation failed due to [{str(error)}], attempt {attempts}"
                        f" of {times}, retry in {wait_time}s"
                    )
                    await asyncio.sleep(wait_time)
                except Exception as err:  # for other kind of exceptions
                    raise err

            raise RetryException(
                f"Failed to execute database query after {attempts} "
                f"attempts over the last {time.time() - start_time} seconds"
            )

        return wrapped_function

    if fn is not None:
        return _decorate(fn)
    return _decorate


def orjson_dumps(val):
    return orjson.dumps(val).decode('utf-8')


class AsyncConnection(object):
    def __init__(self, uri=None, log=None, min=1, max=5):
        self.log = log or configure_logger(__file__)
        self.min = min
        self.max = max
        self.uri = uri

    async def new_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.uri,
                min_size=self.min,
                max_size=self.max
            )
        except Exception as err:
            await self.log.aerror(f"creating AsyncConnection pool {err}")
            self.pool = None
            await asyncio.sleep(0.1)

    async def close_pool(self):
        if hasattr(self, 'pool') and self.pool is not None:
            await self.pool.close()

    @asynccontextmanager
    async def cursor(self):
        while not hasattr(self, 'pool') or (hasattr(self, 'pool') and self.pool is None):
            await self.new_pool()

        exc_value = exc_type = exc_tb = None
        cursor = CustomCursor(pool=self.pool)
        try:
            yield cursor
        except Exception as err:
            raise err


class UnavailableException(Exception):
    pass


def connection_decorator(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        c = args[0]
        if kwargs.get('conn', False):
            await kwargs['conn'].set_type_codec('jsonb', encoder=orjson_dumps,
                                                decoder=orjson.loads, schema='pg_catalog')
            return await func(*args, **kwargs)
        else:
            async with c.pool.acquire() as conn:
                await conn.set_type_codec('jsonb', encoder=orjson_dumps, decoder=orjson.loads, schema='pg_catalog')
                return await func(*args, conn=conn, **kwargs)

    return wrapper


class CustomCursor(object):
    def __init__(self, pool):
        self.pool = pool

    @connection_decorator
    async def execute(self, sql, params=None, conn=None):
        if params is not None:
            res = await conn.execute(sql, *params)
        else:
            res = await conn.execute(sql)
        if 'INSERT' in res or 'UPDATE' in res or 'DELETE' in res:
            return int(res.split(' ')[-1])
        return res

    @connection_decorator
    async def query(self, sql, params=None, conn=None):
        if params is not None:
            data = await conn.fetch(sql, *params)
        else:
            data = await conn.fetch(sql)
        return [dict(r) for r in data]

    @connection_decorator
    async def query_one(self, sql, params=None, conn=None):
        if params is not None:
            res = await conn.fetchrow(sql, *params)
        else:
            res = await conn.fetchrow(sql)
        if res is not None:
            return dict(res)
        return None

    @connection_decorator
    async def query_json(self, sql, params=None, conn=None):
        if "to_json" in sql:
            q = sql
        else:
            q = f"SELECT json_agg(to_json(d)) FROM ({sql}) AS d"

        if params is not None:
            rows = await conn.fetchrow(q, *params)
        else:
            rows = await conn.fetchrow(q)
        res = rows['json_agg']
        if res is None:
            return {}
        elif len(res) == 0 or res[0] is None:
            return {}
        try:
            return orjson.loads(res)[0]
        except:
            return res

    @connection_decorator
    async def query_dict(self, sql, key, params=None, force_unique_key=True, conn=None):
        _d = {}
        if params is not None:
            rows = await conn.fetch(sql, *params)
        else:
            rows = await conn.fetch(sql)

        for row in rows:
            if row[key] in _d and force_unique_key:
                raise Exception("query_dict error: found key value repeated")
            _d[row[key]] = dict(row)
        return _d

    @connection_decorator
    async def insert(self, table, values, returning=None, conn=None):
        _count = [f"${x}" for x, v in enumerate(values.keys(), 1)]
        sql = f"INSERT INTO {table} ({','.join(values.keys())}) VALUES ({','.join(_count)})"
        _values = sqlop.extract_values(values)
        if returning:
            res = await conn.fetchrow(f"{sql} RETURNING {returning}", *_values)
            if res is not None:
                return dict(res)
            else:
                return None
        else:
            inserted = await conn.fetch(f"{sql} RETURNING {list(values.keys())[0]}", *_values)
            return len(inserted)

    @connection_decorator
    async def update(self, table, values, where=None, returning=None, conn=None):
        _values = sqlop.extract_values(values)
        sql = f"UPDATE {table} SET {sqlop.update(values)}"
        if where:
            sql = f"{sql} {sqlop.where(where, start_at=len(values) + 1)}"
            [_values.append(v) for v in where.values()]
        if returning:
            res = await conn.fetchrow(f"{sql} RETURNING {returning}", *_values)
            if res is not None:
                return dict(res)
            else:
                return None
        else:
            updated = await conn.fetch(f"{sql} RETURNING {list(values.keys())[0]}", *_values)
            return len(updated)

    @connection_decorator
    async def upsert(self, table, values, constraint=None, returning=None, conn=None):
        constraint = constraint or f"{table}_pk"
        _count = [f"${x}" for x, v in enumerate(values.keys(), 1)]
        _vals = sqlop.extract_values(values)
        _kvps = [f"{v}=${idx + len(values)}" for idx, v in enumerate(values.keys(), 1)]

        sql = (
            f"INSERT INTO {table} ({','.join(values.keys())}) "
            f"VALUES ({','.join(_count)}) "
            f"ON CONFLICT ({constraint}) DO UPDATE SET {','.join(_kvps)}"
        )

        if returning:
            res = await conn.fetchrow(f"{sql} RETURNING {returning}", *(_vals + _vals))
            if res is not None:
                return dict(res)
            else:
                return None
        else:
            upserted = await conn.fetch(f"{sql} RETURNING {list(values.keys())[0]}", *(_vals + _vals))
            return len(upserted)

    @connection_decorator
    async def upsert_many(self, table, rows, constraint=None, returning=None, conn=None):
        if not rows:
            return 0  # No rows to upsert

        constraint = constraint or f"{table}_pk"
        keys = rows[0].keys()
        values_placeholder = [f"${x}" for x in range(1, len(keys) * len(rows) + 1)]
        split_points = [x for x in range(len(keys), len(values_placeholder) + 1, len(keys))]
        values_chunks = [values_placeholder[s - len(keys):s] for s in split_points]
        values_sql = ",".join([f"({','.join(chunk)})" for chunk in values_chunks])
        all_values = [value for row in rows for value in row.values()]

        _kvps = [f"{key}=excluded.{key}" for key in keys]

        sql = f'INSERT INTO {table} ({",".join(keys)}) VALUES {values_sql} ON CONFLICT ({constraint}) DO UPDATE SET {",".join(_kvps)}'

        if returning:
            result = await conn.fetch(f"{sql} RETURNING {returning}", *all_values)
            return [dict(row) for row in result] if result else []
        else:
            upserted = await conn.fetch(f"{sql} RETURNING {list(keys)[0]}", *all_values)
            return len(upserted)

    @connection_decorator
    async def delete(self, table, where={}, conn=None):
        sql = f"DELETE FROM {table} {sqlop.where(where)}"
        return await conn.execute(sql, *sqlop.extract_values(where))

    @connection_decorator
    async def store_bulk_data(self, data, table_name, columns, conn=None):
        """
        Stores bulk data into a specified table
        Args:
            data: The data to be stored in the table Tuples.
            table_name: The name of the table in which the data will be stored.
            columns: The columns in the table where the data will be stored.
            conn: The database connection to be used for storing the data.
        Returns:
            None
        """
        await conn.copy_records_to_table(table_name, records=data, columns=columns)
