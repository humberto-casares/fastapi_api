from fastapi import APIRouter, Request
from app.crud.users import fetch_all_users
from app.resource.models.users import UsersListResponse


router = APIRouter(prefix="/users")

@router.get("", response_model=UsersListResponse)
async def get_users(request: Request):
    db_conn = request.app.state.db
    users = await fetch_all_users(db_conn)
    return {
        "status_code": 200,
        "message": f"Se encontraron {len(users)} usuarios",
        "data": users,
    }

