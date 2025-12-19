import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from engine import engine, AsyncSessionLocal
from models import Category, Subcategory, Base, Product, ProductImage


async def drop_all_tables():
    """Удалить все таблицы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ Все таблицы удалены")


async def create_all_tables():
    """Создать все таблицы по новым моделям"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Все таблицы созданы заново")


async def seed_test_data():
    """Заполнить БД тестовыми данными"""
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже данные
        categories_count = await session.execute(select(Category))
        if categories_count.scalars().first():
            print("📊 Данные уже существуют, пропускаем заполнение")
            return
        
        # 1. Создаем категории
        categories_data = [
            {"name": "Спальная мебель"},
            {"name": "Кухонная мебель"},
            {"name": "Мягкая мебель"},
            {"name": "📚 Столы и стулья"},
            {"name": "📺 Тумбы и комоды"},
            {"name": "🛏️ Матрасы"},
            {"name": "🚪 Шкафы"},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(name=cat_data["name"])
            session.add(category)
            categories.append(category)
        
        await session.flush()  # Получаем ID категорий
        
        # 2. Создаем подкатегории для каждой категории
        # Категория 1: Спальная мебель
        subcategories_data = [
            # Для категории 1: Спальная мебель
            {"name": "🇷🇺 Российская", "category_id": categories[0].id},
            {"name": "🇹🇷 Турецкая", "category_id": categories[0].id},
            {"name": "Кровати", "category_id": categories[0].id},
            
            # Для категории 2: Кухонная мебель
            {"name": "📐 Прямая", "category_id": categories[1].id},
            {"name": "🔽 Угловая", "category_id": categories[1].id},
            
            # Для категории 3: Мягкая мебель
            {"name": "🇷🇺 Российская → Прямая", "category_id": categories[2].id},
            {"name": "🇷🇺 Российская → Угловая", "category_id": categories[2].id},
            {"name": "🇹🇷 Турецкая", "category_id": categories[2].id},
            
            # Для категории 4: Столы и стулья
            {"name": "Столы", "category_id": categories[3].id},
            {"name": "Стулья", "category_id": categories[3].id},
            {"name": "Барные стулья", "category_id": categories[3].id},
            
            # Для категории 5: Тумбы и комоды
            {"name": "Тумбы под ТВ", "category_id": categories[4].id},
            {"name": "Комоды", "category_id": categories[4].id},
            {"name": "Прикроватные тумбы", "category_id": categories[4].id},
            
            # Для категории 6: Матрасы
            {"name": "Пружинные", "category_id": categories[5].id},
            {"name": "Беспружинные", "category_id": categories[5].id},
            {"name": "Ортопедические", "category_id": categories[5].id},
            {"name": "Детские", "category_id": categories[5].id},
            
            # Для категории 7: Шкафы
            {"name": "Шкафы-купе", "category_id": categories[6].id},
            {"name": "Распашные шкафы", "category_id": categories[6].id},
            {"name": "Гардеробные", "category_id": categories[6].id},
            {"name": "Книжные шкафы", "category_id": categories[6].id},
        ]
        
        subcategories = []
        for sub_data in subcategories_data:
            subcategory = Subcategory(
                name=sub_data["name"],
                category_id=sub_data["category_id"]
            )
            session.add(subcategory)
            subcategories.append(subcategory)
        
        await session.flush()  # Получаем ID подкатегорий
        
        # 3. Создаем тестовые товары для разных категорий
        products_data = [
            # Для категории 1: Спальная мебель (Российская)
            {
                "name": "Кровать 'Элегант'",
                "short_description": "Двуспальная кровать из массива сосны",
                "additional_info": "Страна: Россия | Размер: 200x180 см | Материал: массив сосны | Цвет: венге | Цена: 35 000 руб.",
                "subcategory_id": subcategories[0].id,  # Российская спальня
                "images": [
                    "https://placehold.co/600x400/e6e6fa/333333?text=Кровать+Элегант+1",
                    "https://placehold.co/600x400/e6e6fa/333333?text=Кровать+Элегант+2",
                ]
            },
            {
                "name": "Турецкая кровать 'Султан'",
                "short_description": "Роскошная кровать с мягким изголовьем",
                "additional_info": "Страна: Турция | Размер: 200x200 см | Материал: ткань, дерево | Цвет: бежевый | Цена: 42 000 руб.",
                "subcategory_id": subcategories[1].id,  # Турецкая спальня
                "images": [
                    "https://placehold.co/600x400/fffacd/333333?text=Кровать+Султан+1",
                ]
            },
            
            # Для категории 2: Кухонная мебель (Прямая)
            {
                "name": "Кухня 'Милан' прямая",
                "short_description": "Прямая кухня с фасадами из МДФ",
                "additional_info": "Размер: 240 см | Материал: МДФ, ДСП | Цвет: белый/дуб | Фурнитура: Blum | Цена: 85 000 руб.",
                "subcategory_id": subcategories[3].id,  # Прямая кухня
                "images": [
                    "https://placehold.co/600x400/ffebcd/333333?text=Кухня+Милан+1",
                    "https://placehold.co/600x400/ffebcd/333333?text=Кухня+Милан+2",
                ]
            },
            
            # Для категории 3: Мягкая мебель (Российская → Угловая)
            {
                "name": "Угловой диван 'Комфорт'",
                "short_description": "Угловой диван с механизмом еврокнижка",
                "additional_info": "Страна: Россия | Размер: 220x160 см | Материал: жаккард | Цвет: серый | Цена: 48 000 руб.",
                "subcategory_id": subcategories[6].id,  # Российская → Угловая
                "images": [
                    "https://placehold.co/600x400/d3d3d3/333333?text=Диван+Комфорт+1",
                    "https://placehold.co/600x400/d3d3d3/333333?text=Диван+Комфорт+2",
                    "https://placehold.co/600x400/d3d3d3/333333?text=Диван+Комфорт+3",
                ]
            },
            
            # Для категории 4: Столы и стулья (Столы)
            {
                "name": "Обеденный стол 'Флоренция'",
                "short_description": "Стеклянный стол на металлической основе",
                "additional_info": "Размер: 120x80 см | Материал: стекло, сталь | Цвет: прозрачный/хром | Цена: 24 000 руб.",
                "subcategory_id": subcategories[8].id,  # Столы
                "images": [
                    "https://placehold.co/600x400/f0f8ff/333333?text=Стол+Флоренция+1",
                ]
            },
            
            # Для категории 7: Шкафы (Шкафы-купе)
            {
                "name": "Шкаф-купе 'Модерн'",
                "short_description": "Вместительный шкаф с зеркальными дверями",
                "additional_info": "Размеры: 240x60x220 см | Материал: ЛДСП | Цвет: белый/зеркало | Фурнитура: система купе | Цена: 32 500 руб.",
                "subcategory_id": subcategories[19].id,  # Шкафы-купе
                "images": [
                    "https://placehold.co/600x400/f5f5f5/333333?text=Шкаф+Модерн+1",
                    "https://placehold.co/600x400/f5f5f5/333333?text=Шкаф+Модерн+2",
                ]
            },
        ]
        
        for prod_data in products_data:
            product = Product(
                name=prod_data["name"],
                short_description=prod_data["short_description"],
                additional_info=prod_data["additional_info"],
                subcategory_id=prod_data["subcategory_id"]
            )
            session.add(product)
            await session.flush()  # Получаем ID товара
            
            # Добавляем изображения
            for img_url in prod_data["images"]:
                image = ProductImage(url=img_url, product_id=product.id)
                session.add(image)
        
        await session.commit()
        print("✅ Тестовые данные добавлены")
        print(f"   Категорий: {len(categories)}")
        print(f"   Подкатегорий: {len(subcategories)}")
        print(f"   Товаров: {len(products_data)}")


async def init_database():
    """Инициализация базы данных"""
    print("🔄 Инициализация базы данных...")
    
    # Удаляем старые таблицы
    await drop_all_tables()
    
    # Создаем новые таблицы
    await create_all_tables()
    
    # Заполняем тестовыми данными
    await seed_test_data()
    
    print("✅ База данных готова к работе!")
    
    # Закрываем соединение
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())