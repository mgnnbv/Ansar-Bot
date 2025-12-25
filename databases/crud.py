import asyncio
from typing import List
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from databases.engine import AsyncSessionLocal
from fsm import EditProductStates

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



async def search_products(session: AsyncSession, search_term: str) -> list[Product]:
    """Поиск товаров по названию"""
    result = await session.execute(
        select(Product)
        .where(Product.name.ilike(f"%{search_term}%"))
        .options(selectinload(Product.images))
        .limit(20)  
    )
    return result.scalars().all()


async def get_products_by_category_id(
    session: AsyncSession,
    category_id: int
) -> List[Product]:
    """Получить все активные товары категории"""
    from sqlalchemy import select
    
    stmt = select(Product).where(
        Product.category_id == category_id,
        Product.is_active == True
    ).order_by(Product.created_at.desc())
    
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_products_by_category(session: AsyncSession, category_id: int) -> list[Product]:
    """Получить товары по ID категории (без подкатегорий)"""
    result = await session.execute(
        select(Product)
        .where(
            (Product.category_id == category_id) &
            (Product.subcategory_id == None)  # ← Только товары БЕЗ подкатегорий
        )
        .options(selectinload(Product.images))
    )

    return result.scalars().all()



async def show_product_list_by_name(message: Message, state: FSMContext, products, search_query):
    """Показ списка найденных товаров"""
    builder = InlineKeyboardBuilder()
    
    for product in products:
        # Формируем текст кнопки
        category_name = product.category.name if product.category else "Без кат."
        images_count = len(product.images)
        
        button_text = f"🛒 {product.name}"
        if len(button_text) > 35:
            button_text = button_text[:32] + "..."
        
        builder.button(
            text=button_text,
            callback_data=f"select_product_{product.id}"
        )
        
        # Дополнительная информация под кнопкой
        builder.button(
            text=f"📁 {category_name} | 📷 {images_count}",
            callback_data=f"info_{product.id}"
        )
    
    # Навигационные кнопки
    builder.button(text="🔍 Новый поиск", callback_data="new_search_name")
    builder.button(text="📋 Показать все товары", callback_data="show_all_products")
    builder.button(text="❌ Отменить", callback_data="cancel_edit")
    
    builder.adjust(1, 2, 2, 1)  # Настраиваем расположение
    
    # Формируем текст сообщения
    found_text = f"🔍 <b>Найдено товаров:</b> {len(products)} по запросу '<code>{search_query}</code>'"
    
    await message.answer(
        found_text,
        reply_markup=builder.as_markup(),
        parse_mode=BaseModel.HTML
    )
    await state.set_state(EditProductStates.waiting_for_product_choice)
