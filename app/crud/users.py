from fastapi import HTTPException

from app.db.db import AsyncConnection, retry_db
from app.db.utils import db_insert, db_update
from app.resource.models.users import User, UserCreate, UserUpdate
from app.utils.params import MAX_RETRIES, WAIT_RETRIES


USER_RETURNING = "user_id, user_name, email, full_name, is_active, profile, created_at, updated_at"


def _orjson_dumps(val):
    import orjson

    return orjson.dumps(val).decode("utf-8")


async def _prepare_connection(connection) -> None:
    import orjson

    await connection.set_type_codec(
        "jsonb",
        encoder=_orjson_dumps,
        decoder=orjson.loads,
        schema="pg_catalog",
    )


@retry_db(times=MAX_RETRIES, wait_factor=WAIT_RETRIES)
async def list_users(conn: AsyncConnection, limit: int = 100, offset: int = 0) -> list[User]:
    try:
        async with conn.pool.acquire() as connection:
            await _prepare_connection(connection)
            rows = await connection.fetch(
                f"""
                SELECT {USER_RETURNING}
                FROM users
                WHERE is_active = TRUE
                ORDER BY user_id ASC
                LIMIT $1 OFFSET $2
                """,
                limit,
                offset,
            )
            return [User.model_validate(dict(r)) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener users: {str(e)}")


@retry_db(times=MAX_RETRIES, wait_factor=WAIT_RETRIES)
async def get_user(conn: AsyncConnection, user_id: int) -> User:
    try:
        async with conn.pool.acquire() as connection:
            await _prepare_connection(connection)
            row = await connection.fetchrow(
                f"""
                SELECT {USER_RETURNING}
                FROM users
                WHERE user_id = $1 AND is_active = TRUE
                """,
                user_id,
            )
            if row is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return User.model_validate(dict(row))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener user: {str(e)}")


@retry_db(times=MAX_RETRIES, wait_factor=WAIT_RETRIES)
async def create_user(conn: AsyncConnection, payload: UserCreate) -> User:
    try:
        values = payload.model_dump()
        async with conn.pool.acquire() as connection:
            await _prepare_connection(connection)
            row = await db_insert(
                "users",
                values={
                    "user_name": values["user_name"],
                    "email": values["email"],
                    "full_name": values["full_name"],
                    "is_active": values["is_active"],
                    "profile": values["profile"],
                },
                returning=USER_RETURNING,
                conn=connection,
            )
            return User.model_validate(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear user: {str(e)}")


@retry_db(times=MAX_RETRIES, wait_factor=WAIT_RETRIES)
async def update_user(conn: AsyncConnection, user_id: int, payload: UserUpdate) -> User:
    try:
        values = payload.model_dump(exclude_unset=True)
        if not values:
            return await get_user(conn, user_id)

        async with conn.pool.acquire() as connection:
            await _prepare_connection(connection)
            row = await db_update(
                "users",
                values=values,
                where={"user_id": user_id, "is_active": True},
                returning=USER_RETURNING,
                conn=connection,
            )
            if row is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return User.model_validate(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar user: {str(e)}")


@retry_db(times=MAX_RETRIES, wait_factor=WAIT_RETRIES)
async def delete_user(conn: AsyncConnection, user_id: int) -> None:
    try:
        async with conn.pool.acquire() as connection:
            await _prepare_connection(connection)
            row = await db_update(
                "users",
                values={"is_active": False},
                where={"user_id": user_id, "is_active": True},
                returning="user_id",
                conn=connection,
            )
            if row is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar user: {str(e)}")
