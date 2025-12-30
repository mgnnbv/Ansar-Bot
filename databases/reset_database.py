import asyncio
from sqlalchemy import select
from engine import AsyncSessionLocal
from models import Category, Product, ProductImage, Subcategory

async def get_products_data():
    async with AsyncSessionLocal() as session:
        # 🔹 ТОВАР 1: Кровать 'Элегант' 🇷🇺
        print("🔍 ТОВАР 1: Кровать 'Элегант' 🇷🇺")
        print("-" * 40)
        product1 = await session.scalar(
            select(Product).where(Product.name.ilike("%элегант%"))
        )
        if product1:
            print(f"ID: {product1.id}")
            print(f"Название: {product1.name}")
            print(f"Категория ID: {product1.category_id}")
            print(f"Подкатегория ID: {product1.subcategory_id}")
            print(f"Описание: {product1.short_description}")

            category1 = await session.scalar(
                select(Category).where(Category.id == product1.category_id)
            )
            print(f"Категория: {category1.name if category1 else 'Нет'}")

            if product1.subcategory_id:
                subcat1 = await session.scalar(
                    select(Subcategory).where(Subcategory.id == product1.subcategory_id)
                )
                print(f"Подкатегория: {subcat1.name if subcat1 else 'Нет'}")

            # Фото
            photo_urls1 = [
                    'https://avatars.mds.yandex.net/get-mpic/4120495/img_id6446554681234858130.jpeg/orig'
            ]
            print(f"Фото: {len(photo_urls1)}")
            for url in photo_urls1:
                print(f"  URL: {url}")

        # 🔹 ТОВАР 2: Кровать 'Султан' 🇹🇷
        print("\n🔍 ТОВАР 2: Кровать 'Султан' 🇹🇷")
        print("-" * 40)
        product2 = await session.scalar(
            select(Product).where(Product.name.ilike("%султан%"))
        )
        if product2:
            print(f"ID: {product2.id}")
            print(f"Название: {product2.name}")
            print(f"Категория ID: {product2.category_id}")
            print(f"Подкатегория ID: {product2.subcategory_id}")
            print(f"Описание: {product2.short_description}")

            category2 = await session.scalar(
                select(Category).where(Category.id == product2.category_id)
            )
            print(f"Категория: {category2.name if category2 else 'Нет'}")

            if product2.subcategory_id:
                subcat2 = await session.scalar(
                    select(Subcategory).where(Subcategory.id == product2.subcategory_id)
                )
                print(f"Подкатегория: {subcat2.name if subcat2 else 'Нет'}")

            # Фото
            photo_urls2 = [
                    'https://aligulerfurniture.com/cdn/shop/files/sultan-cream-bed-ali-guler-furniture-3.jpg?v=1736181477'
            ]
            print(f"Фото: {len(photo_urls2)}")
            for url in photo_urls2:
                print(f"  URL: {url}")

        # 🔹 ТОВАР 3: Кухня 'Милан' прямая
        print("\n🔍 ТОВАР 3: Кухня 'Милан' прямая")
        print("-" * 40)
        product3 = await session.scalar(
            select(Product).where(Product.name.ilike("%милан%"))
        )
        if product3:
            print(f"ID: {product3.id}")
            print(f"Название: {product3.name}")
            print(f"Категория ID: {product3.category_id}")
            print(f"Подкатегория ID: {product3.subcategory_id}")
            print(f"Описание: {product3.short_description}")

            category3 = await session.scalar(
                select(Category).where(Category.id == product3.category_id)
            )
            print(f"Категория: {category3.name if category3 else 'Нет'}")

            if product3.subcategory_id:
                subcat3 = await session.scalar(
                    select(Subcategory).where(Subcategory.id == product3.subcategory_id)
                )
                print(f"Подкатегория: {subcat3.name if subcat3 else 'Нет'}")

            # Фото
            photo_urls3 = [
                    'https://aligulerfurniture.com/cdn/shop/files/sultan-dining-table-ali-guler-furniture-1.jpg?v=1716705735'
            ]
            print(f"Фото: {len(photo_urls3)}")
            for url in photo_urls3:
                print(f"  URL: {url}")

async def main():
    await get_products_data()

if __name__ == "__main__":
    asyncio.run(main())
