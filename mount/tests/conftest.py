from collections.abc import AsyncIterator

import pytest
from app.adapters.database import dsn
from app.adapters.database import ServiceDatabase
from app.common import settings
from app.common.context import Context


class TestContext(Context):
    def __init__(self, db: ServiceDatabase) -> None:
        self._db = db

    @property
    def db(self) -> ServiceDatabase:
        return self._db


@pytest.fixture(scope="function")
async def db() -> AsyncIterator[ServiceDatabase]:
    async with ServiceDatabase(
        write_dsn=dsn(
            scheme=settings.WRITE_DB_SCHEME,
            user=settings.WRITE_DB_USER,
            password=settings.WRITE_DB_PASS,
            host=settings.WRITE_DB_HOST,
            port=settings.WRITE_DB_PORT,
            database=settings.WRITE_DB_NAME,
        ),
        read_dsn=dsn(
            scheme=settings.WRITE_DB_SCHEME,
            user=settings.READ_DB_USER,
            password=settings.READ_DB_PASS,
            host=settings.READ_DB_HOST,
            port=settings.READ_DB_PORT,
            database=settings.READ_DB_NAME,
        ),
        min_pool_size=settings.MIN_DB_POOL_SIZE,
        max_pool_size=settings.MAX_DB_POOL_SIZE,
        ssl=settings.DB_USE_SSL,
    ) as db:
        yield db

        # TODO: is there a more automatic solution?
        await db.execute("TRUNCATE servers")


@pytest.fixture
async def ctx(db: ServiceDatabase) -> TestContext:
    return TestContext(db=db)
