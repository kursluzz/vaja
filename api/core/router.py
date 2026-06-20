from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.models import User
from api.core.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    result = await db.execute(
        select(User).where(User.telegram_user_id == body.telegram_user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    user = User(telegram_user_id=body.telegram_user_id)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.get("/{telegram_user_id}", response_model=UserResponse)
async def get_user(telegram_user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    result = await db.execute(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
