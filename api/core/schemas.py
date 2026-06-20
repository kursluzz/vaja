from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    telegram_user_id: int


class UserResponse(BaseModel):
    id: int
    telegram_user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
