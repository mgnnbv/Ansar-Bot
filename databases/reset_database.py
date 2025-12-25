import asyncio
from sqlalchemy import select
from engine import AsyncSessionLocal
from models import Category, Product, ProductImage, Subcategory

async def get_products_data():
    async with AsyncSessionLocal() as session:
        print("🔍 ТОВАР 1: КУХНЯ 'МИЛАН' ПРЯМАЯ")
        print("-" * 40)
        
        # Находим товар
        product1 = await session.scalar(
            select(Product).where(Product.name.ilike("%милан%"))
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
            photos1 = await session.scalars(
                select(ProductImage).where(ProductImage.product_id == product1.id)
            )
            print(f"Фото: {len(list(photos1))}")
            for photo in photos1:
                print(f"  URL: {photo.url[:50]}...")
        
        print("\n🔍 ТОВАР 2: КИТАЙСКИЙ СТУЛ")
        print("-" * 40)
        
        product2 = await session.scalar(
            select(Product).where(Product.name.ilike("%китайск%стул%"))
        )
        
        if product2:
            print(f"ID: {product2.id}")
            print(f"Название: {product2.name}")
            print(f"Категория ID: {product2.category_id}")
            print(f"Подкатегория ID: {product2.subcategory_id}")
            print(f"Описание: {product2.short_description}")
            # print(f'image: {product2.images}')
            
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
            photos2 = await session.scalars(
                select(ProductImage).where(ProductImage.product_id == product2.id)
            )
            print(f"Фото: {len(list(photos2))}")
            for photo in photos2:
                print(f"  URL: {photo.url[:50]}...")

async def main():
    await get_products_data()

if __name__ == "__main__":
    asyncio.run(main())