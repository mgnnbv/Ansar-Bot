import asyncio

from engine import engine
from models import Category, Subcategory, Base, Product, ProductImage, Order, OrderStatus

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
        await engine.dispose()

asyncio.run(init_models())
