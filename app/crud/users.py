from typing import List

from fastapi import HTTPException

from app.db.db import AsyncConnection, retry_db
from app.utils.params import MAX_RETRIES, WAIT_RETRIES
from app.resource.models.users import UserResponse


@retry_db(times=MAX_RETRIES, wait_factor=WAIT_RETRIES)
async def fetch_all_users(conn: AsyncConnection) -> List[UserResponse]:
    try:
        async with conn.cursor() as cur:
            rows = await cur.query(
                """
                SELECT user_id, user_name
                FROM users
                ORDER BY user_id ASC
                """
            )
            return [UserResponse.model_validate(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener users: {str(e)}")                
