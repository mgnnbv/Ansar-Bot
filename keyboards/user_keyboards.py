from typing import Optional
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from databases.crud import get_categories
from handlers.callbacks import (
    BackCallback, ProductCallback, ProductDetailCallback, 
    SubcategoryCallback, CategoryCallback, AskCallback)

MANAGER_USERNAME = "mgnnbv"


async def categories_keyboard(
    session: AsyncSession,
    row_amount: int = 2
) -> InlineKeyboardMarkup:
    """Клавиатура с категориями товаров"""
    categories = await get_categories(session)

    builder = InlineKeyboardBuilder()

    if not categories:
        builder.button(
            text="Нет доступных категорий",
            callback_data="no_categories")
    else:
        for category in categories:
            builder.button(
                text=category.name,
                callback_data=CategoryCallback(category_id=category.id).pack())

    builder.adjust(row_amount)
    return builder.as_markup()


async def subcategories_keyboard(
    subcategories, 
    category_id: int,  # ← Этот параметр уже есть!
    row_amount: int = 1) -> InlineKeyboardMarkup:
    """Клавиатура с подкатегориями"""
    builder = InlineKeyboardBuilder()

    if not subcategories:
        builder.button(
            text="💬 Задать вопрос", 
            callback_data="ask_question")
        builder.button(
            text="📞 Консультация", 
            callback_data="request_consultation")
    else:
        for subcategory in subcategories:
            builder.button(
                text=subcategory.name,
                callback_data=SubcategoryCallback(
                    subcategory_id=subcategory.id
                ).pack())

    builder.button(
        text="⬅️ Назад",
        callback_data=BackCallback(to="categories").pack())

    builder.adjust(row_amount, 2, 1)
    return builder.as_markup()


async def products_keyboard(
    products, 
    subcategory_id: int,
    category_id: Optional[int] = None,  # ← Сделайте опциональным
    row_amount: int = 1) -> InlineKeyboardMarkup:
    """Клавиатура со списком продуктов"""
    builder = InlineKeyboardBuilder()

    if not products:
        builder.button(
            text="Нет товаров в этой подкатегории",
            callback_data="no_products")
    else:
        for product in products:
            product_text = f"📦 {product.name}"
                
            builder.button(
                text=product_text,
                callback_data=ProductCallback(product_id=product.id).pack())

    
    builder.button(
        text="⬅️ Назад",
        callback_data=BackCallback(
            to="subcategories",
            parent_id=category_id  
        ).pack())

    builder.adjust(row_amount, 1)
    return builder.as_markup()


async def command_keyboard(
    category_id: int = None,
    subcategory_id: int = None,
    product_id: int =None) -> InlineKeyboardMarkup:
    """Универсальная клавиатура с командами"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="💬 Задать вопрос", 
        callback_data=AskCallback().pack())
    builder.button(
        text="📞 Консультация", 
        callback_data="request_consultation")
    builder.button(
        text="🛒 Оформить заказ", 
        callback_data="place_order")
    
    if subcategory_id:
        builder.button(
            text="⬅️ Назад к товарам",
            callback_data=BackCallback(
                to="products",
                parent_id=subcategory_id  
            ).pack())
    elif category_id:
        builder.button(
            text="⬅️ Назад в подкатегории",
            callback_data=BackCallback(
                to="subcategories",
                parent_id=category_id  
            ).pack())
    else:
        builder.button(
            text="⬅️ Назад в каталог",
            callback_data=BackCallback(to="categories").pack())
    
    builder.adjust(2, 1, 1) 
    return builder.as_markup()

async def consultation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с ссылкой на чат менеджера."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                    text="💬 Перейти в чат с менеджером",
                    url=f"https://t.me/{MANAGER_USERNAME}")]])


# def cart_keyboard() -> InlineKeyboardMarkup:
#     """Клавиатура для корзины"""
#     builder = InlineKeyboardBuilder()
    
#     builder.button(text="🛒 Оформить заказ", callback_data="checkout")
#     builder.button(text="🗑️ Очистить корзину", callback_data="clear_cart")
#     builder.button(text="📦 Продолжить покупки", callback_data="continue_shopping")
#     builder.button(text="🏠 Главное меню", callback_data="main_menu")
    
#     builder.adjust(2, 1, 1)
#     return builder.as_markup()


# async def main_menu_keyboard() -> InlineKeyboardMarkup:
#     """Главное меню бота"""
#     builder = InlineKeyboardBuilder()
    
#     builder.button(text="📂 Каталог", callback_data="catalog")
#     builder.button(text="🛒 Корзина", callback_data="cart")
#     builder.button(text="📋 Мои заказы", callback_data="my_orders")
#     builder.button(text="👤 Профиль", callback_data="profile")
#     builder.button(text="📞 Контакты", callback_data="contacts")
#     builder.button(text="ℹ️ О компании", callback_data="about")
    
#     builder.adjust(2, 2, 2)
#     return builder.as_markup()


def back_to_catalog_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура для возврата в каталог"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📂 Вернуться в каталог",
        callback_data="back_to_catalog")
    
    return builder.as_markup()


