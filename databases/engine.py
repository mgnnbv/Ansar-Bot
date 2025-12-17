from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from environs import Env

from sqlalchemy import text

env = Env()
env.read_env()


DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{env.str('DB_USER')}:"
    f"{env.str('DB_PASS')}@"
    f"{env.str('DB_HOST')}:"
    f"{env.int('DB_PORT')}/"
    f"{env.str('DB_NAME')}"
)

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def test():
    '''Этот тест для проверки соединения с PostgreSQL'''
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())

# asyncio.run(test())

