from fastapi import APIRouter, Request

from app.crud.users import create_user, delete_user, get_user, list_users, update_user
from app.resource.models.users import (
    UserCreate,
    UserCreateResponse,
    UserDeleteResponse,
    UserGetResponse,
    UsersListResponse,
    UserUpdate,
    UserUpdateResponse,
)


router = APIRouter(prefix="/users")


@router.get("", response_model=UsersListResponse)
async def get_users(request: Request, limit: int = 100, offset: int = 0):
    db_conn = request.app.state.db
    users = await list_users(db_conn, limit=limit, offset=offset)
    return {
        "status_code": 200,
        "message": f"Se encontraron {len(users)} usuarios",
        "data": users,
    }


@router.get("/{user_id}", response_model=UserGetResponse)
async def get_user_by_id(request: Request, user_id: int):
    db_conn = request.app.state.db
    user = await get_user(db_conn, user_id=user_id)
    return {
        "status_code": 200,
        "message": "Usuario encontrado",
        "data": user,
    }


@router.post("", status_code=201, response_model=UserCreateResponse)
async def create_user_endpoint(request: Request, payload: UserCreate):
    db_conn = request.app.state.db
    user = await create_user(db_conn, payload=payload)
    return {
        "status_code": 201,
        "message": "Usuario creado",
        "data": user,
    }


@router.patch("/{user_id}", response_model=UserUpdateResponse)
async def update_user_endpoint(request: Request, user_id: int, payload: UserUpdate):
    db_conn = request.app.state.db
    user = await update_user(db_conn, user_id=user_id, payload=payload)
    return {
        "status_code": 200,
        "message": "Usuario actualizado",
        "data": user,
    }


@router.delete("/{user_id}", response_model=UserDeleteResponse)
async def delete_user_endpoint(request: Request, user_id: int):
    db_conn = request.app.state.db
    await delete_user(db_conn, user_id=user_id)
    return {
        "status_code": 200,
        "message": "Usuario eliminado",
    }

