import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# from engine import AsyncSessionLocal


from .models import Category, Subcategory, Product


async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(select(Category).order_by(Category.id))
    return result.scalars().all()


async def get_subcategories(
    session: AsyncSession,
    category_id: int
) -> list[Subcategory]:
    result = await session.execute(
        select(Subcategory).where(Subcategory.category_id == category_id)
    )
    return result.scalars().all()


async def get_subcategory(
    session: AsyncSession,
    subcategory_id: int
) -> Subcategory | None:
    result = await session.execute(
        select(Subcategory).where(Subcategory.id == subcategory_id)
    )
    return result.scalars().first()



async def get_products(session: AsyncSession, subcategory_id: int) -> list[Product]:
    result = await session.execute(
        select(Product)
        .where(Product.subcategory_id == subcategory_id)
        .options(selectinload(Product.images))  
    )
    return result.scalars().all()



# PRODUCTS = [
#     {
#         "name": "🇷🇺 Роскошная Российская Спальная Мебель – Коллекция Комфорт",
#         "short_description": "Высококачественная спальная мебель российского производства. Элегантный дизайн и максимальный   комфорт для сна.",
#         "country": "Россия",
#         "size": "160x200, 180x200",
#         "price": 15000.0,
#         "category_id": 1,
#         "subcategory_id": 1
#     },
#     {
#         "name": "🇷🇺 Российская Спальная Мебель премиум-класса – Серия «Элегант»",
#         "short_description": "Прочные и стильные кровати и спальни для современного дома. Надёжность и уют в каждой детали.",
#         "country": "Россия",
#         "size": "180x200, 200x200",
#         "price": 18000.0,
#         "category_id": 1,
#         "subcategory_id": 1
#     },

#     {
#         "name": "🇹🇷 Элегантная Турецкая Спальная Мебель – Коллекция «Люкс»",
#         "short_description": "Стильная турецкая мебель премиум-класса с современным дизайном и долговечными материалами.",
#         "country": "Турция",
#         "size": "160x200, 180x200",
#         "price": 16000.0,
#         "category_id": 1,
#         "subcategory_id": 2
#     },
#     {
#         "name": "🇹🇷 Турецкая Мебель премиум-класса – Серия «Royal»",
#         "short_description": "Элегантные кровати и спальни из Турции. Идеальное сочетание стиля, качества и комфорта.",
#         "country": "Турция",
#         "size": "180x200, 200x200",
#         "price": 20000.0,
#         "category_id": 1,
#         "subcategory_id": 2
#     },
#     {
#         "name": "🇹🇷 Современная Турецкая Спальная Мебель – Коллекция «Modern»",
#         "short_description": "Мебель с уникальным дизайном, удобными кроватями и мягкими элементами для максимального комфорта.",
#         "country": "Турция",
#         "size": "160x200, 200x200",
#         "price": 17000.0,
#         "category_id": 1,
#         "subcategory_id": 2
#     },

#     {
#         "name": "Кровать Мечты для Современной Спальни – Модель «Comfort Plus»",
#         "short_description": "Современная кровать с удобным основанием и стильным дизайном. Отличный выбор для любой спальни.",
#         "country": "Россия/Турция",
#         "size": "160x200, 180x200",
#         "price": 15000.0,
#         "category_id": 1,
#         "subcategory_id": 3
#     },
#     {
#         "name": "Кровать Элегантная и Надёжная – Модель «DreamLine»",
#         "short_description": "Прочная и красивая кровать, создающая уют и комфорт для сна. Подходит для любых интерьеров.",
#         "country": "Россия/Турция",
#         "size": "180x200, 200x200",
#         "price": 18000.0,
#         "category_id": 1,
#         "subcategory_id": 3
#     },
# ]

# async def seed_products():
#     async with AsyncSessionLocal() as session:
#         exists = await session.execute(select(Product))
#         if exists.scalars().first():
#             print("📦 Продукты уже существуют")
#             return

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

#         await session.commit()
#         print("✅ Продукты добавлены")

# if __name__ == "__main__":
#     asyncio.run(seed_products())








