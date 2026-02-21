import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.main import app as fastapi_app
from app.db.session import get_db
from app.db.base import Base
import app.models

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/chatdb_test"

@pytest.fixture(scope="session")
async def setup_db():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

@pytest.fixture
async def client(setup_db):
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fastapi_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test"
    ) as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
    await engine.dispose()

@pytest.fixture
async def auth_headers(client):
    await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "testpass123"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@test.com",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}