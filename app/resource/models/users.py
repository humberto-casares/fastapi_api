from pydantic import BaseModel


class UserResponse(BaseModel):
    user_id: int
    user_name: str


class UsersListResponse(BaseModel):
    status_code: int
    message: str
    data: list[UserResponse]

