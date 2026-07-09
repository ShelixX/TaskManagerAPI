import os
import sys
import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["COOKIE_SECURE"] = "false"

from app.database import Base
from app.dependencies import get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = async_sessionmaker(
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        bind=engine,
    )

    async def create_tables():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def drop_tables():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    asyncio.run(create_tables())
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(drop_tables())
