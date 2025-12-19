import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Category, Subcategory, Product


async def get_categories(session: AsyncSession) -> list[Category]:
    """Получить все категории"""
    result = await session.execute(select(Category).order_by(Category.id))
    return result.scalars().all()


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    """Получить категорию по ID"""
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalars().first()


async def get_subcategories(
    session: AsyncSession,
    category_id: int
) -> list[Subcategory]:
    """Получить подкатегории по ID категории"""
    result = await session.execute(
        select(Subcategory).where(Subcategory.category_id == category_id)
    )
    return result.scalars().all()


async def get_subcategory(
    session: AsyncSession,
    subcategory_id: int
) -> Subcategory | None:
    """Получить подкатегорию по ID"""
    result = await session.execute(
        select(Subcategory).where(Subcategory.id == subcategory_id)
    )
    return result.scalars().first()


async def get_products(session: AsyncSession, subcategory_id: int) -> list[Product]:
    """Получить товары по ID подкатегории"""
    result = await session.execute(
        select(Product)
        .where(Product.subcategory_id == subcategory_id)
        .options(selectinload(Product.images))
    )
    return result.scalars().all()


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    """Получить товар по ID"""
    result = await session.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.images))
    )
    return result.scalars().first()


async def get_products_by_category(session: AsyncSession, category_id: int) -> list[Product]:
    """Получить все товары категории (через подкатегории)"""
    subcategories = await get_subcategories(session, category_id)
    
    all_products = []
    for subcategory in subcategories:
        products = await get_products(session, subcategory.id)
        all_products.extend(products)
    
    return all_products


async def search_products(session: AsyncSession, search_term: str) -> list[Product]:
    """Поиск товаров по названию"""
    result = await session.execute(
        select(Product)
        .where(Product.name.ilike(f"%{search_term}%"))
        .options(selectinload(Product.images))
        .limit(20)  # Ограничиваем количество результатов
    )
    return result.scalars().all()



# async def seed_products():
#     from .engine import AsyncSessionLocal
#     
#     async with AsyncSessionLocal() as session:
#         exists = await session.execute(select(Product))
#         if exists.scalars().first():
#             print("📦 Продукты уже существуют")
#             return
#
#         for prod in PRODUCTS:
#             product = Product(
#                 name=prod["name"],
#                 short_description=prod["short_description"],
#                 country=prod["country"],
#                 size=prod["size"],
#                 price=prod["price"],
#                 category_id=prod["category_id"],
#                 subcategory_id=prod["subcategory_id"]
#             )
#             session.add(product)
#
#         await session.commit()
#         print("✅ Продукты добавлены")
#
#
# if __name__ == "__main__":
#     asyncio.run(seed_products())