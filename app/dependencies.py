from typing import AsyncGenerator
from app.database import session_local
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_local() as session:
        yield session