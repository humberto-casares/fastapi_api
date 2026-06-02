from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    user_id: int
    user_name: str
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool
    profile: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "user_name": "tutor_01",
                "email": "user@example.com",
                "full_name": "Tutor Name",
                "is_active": True,
                "profile": {"phone": "+527471549863"},
                "created_at": "2026-06-01T00:00:00Z",
                "updated_at": "2026-06-01T00:00:00Z",
            }
        }


class UserCreate(BaseModel):
    user_name: str
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool = True
    profile: dict[str, Any] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "user_name": "tutor_01",
                "email": "user@example.com",
                "full_name": "Tutor Name",
                "is_active": True,
                "profile": {"phone": "+527471549863"},
            }
        }


class UserUpdate(BaseModel):
    user_name: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None
    profile: dict[str, Any] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "new_email@example.com",
                "full_name": "Updated Tutor Name",
                "is_active": True,
                "profile": {"phone": "+527471549863", "city": "CDMX"},
            }
        }


class UsersListResponse(BaseModel):
    status_code: int
    message: str
    data: list[User]

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "message": "Se encontraron 1 usuarios",
                "data": [
                    {
                        "user_id": 1,
                        "user_name": "tutor_01",
                        "email": "user@example.com",
                        "full_name": "Tutor Name",
                        "is_active": True,
                        "profile": {"phone": "+527471549863"},
                        "created_at": "2026-06-01T00:00:00Z",
                        "updated_at": "2026-06-01T00:00:00Z",
                    }
                ],
            }
        }


class UserGetResponse(BaseModel):
    status_code: int
    message: str
    data: User

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "message": "Usuario encontrado",
                "data": {
                    "user_id": 1,
                    "user_name": "tutor_01",
                    "email": "user@example.com",
                    "full_name": "Tutor Name",
                    "is_active": True,
                    "profile": {"phone": "+527471549863"},
                    "created_at": "2026-06-01T00:00:00Z",
                    "updated_at": "2026-06-01T00:00:00Z",
                },
            }
        }


class UserCreateResponse(BaseModel):
    status_code: int
    message: str
    data: User

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 201,
                "message": "Usuario creado",
                "data": {
                    "user_id": 1,
                    "user_name": "tutor_01",
                    "email": "user@example.com",
                    "full_name": "Tutor Name",
                    "is_active": True,
                    "profile": {"phone": "+527471549863"},
                    "created_at": "2026-06-01T00:00:00Z",
                    "updated_at": "2026-06-01T00:00:00Z",
                },
            }
        }


class UserUpdateResponse(BaseModel):
    status_code: int
    message: str
    data: User

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "message": "Usuario actualizado",
                "data": {
                    "user_id": 1,
                    "user_name": "tutor_01",
                    "email": "new_email@example.com",
                    "full_name": "Updated Tutor Name",
                    "is_active": True,
                    "profile": {"phone": "+527471549863", "city": "CDMX"},
                    "created_at": "2026-06-01T00:00:00Z",
                    "updated_at": "2026-06-01T00:00:00Z",
                },
            }
        }


class UserDeleteResponse(BaseModel):
    status_code: int
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "message": "Usuario eliminado",
            }
        }

