from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
from databases.crud import get_categories
from handlers.callbacks import (
    BackCallback, ProductCallback, SubcategoryCallback,
    CategoryCallback, AskCallback)

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
    category_id: int,  
    row_amount: int = 1) -> InlineKeyboardMarkup:
    """Клавиатура с подкатегориями"""
    builder = InlineKeyboardBuilder()

    if not subcategories:
        builder.button(
        text="💬 Задать вопрос", 
        callback_data=AskCallback().pack()
            )
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
    subcategory_id: int | None = None,
    category_id: int | None = None,
    row_amount: int = 1
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if products:  
        for product in products:
            builder.button(
                text=f"📦 {product.name}",
                callback_data=ProductCallback(product_id=product.id).pack()
            )
    else:  
        builder.button(
            text="Товаров пока нет",
            callback_data="no_products"
        )
    
    if subcategory_id and category_id:
        builder.button(
            text="⬅️ Назад",
            callback_data=BackCallback(
                to="subcategories",
                parent_id=category_id  
            ).pack()
        )
    elif category_id:
        builder.button(
            text="⬅️ Назад",
            callback_data=BackCallback(
                to="categories"
            ).pack()
        )
    else:
        builder.button(
            text="⬅️ Назад",
            callback_data=BackCallback(to="categories").pack()
        )
    
    builder.adjust(row_amount, 1)  
    return builder.as_markup()


async def command_keyboard(
    category_id: int = None,
    subcategory_id: int = None,
    product_id: int = None,
    empty: bool = False
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    # ---------- КНОПКА НАЗАД ----------
    if empty and category_id:
        builder.button(
            text="⬅️ Назад к подкатегориям",
            callback_data=BackCallback(
                to="subcategories",
                parent_id=category_id
            ).pack()
        )

    elif product_id and subcategory_id:
        builder.button(
            text="⬅️ Назад к товарам",
            callback_data=BackCallback(
                to="products",
                parent_id=subcategory_id
            ).pack()
        )

    elif subcategory_id and category_id:
        builder.button(
            text="⬅️ Назад к подкатегориям",
            callback_data=BackCallback(
                to="subcategories",
                parent_id=category_id
            ).pack()
        )

    else:
        builder.button(
            text="⬅️ Назад в каталог",
            callback_data=BackCallback(to="categories").pack()
        )

    builder.button(
        text="💬 Задать вопрос",
        callback_data=AskCallback().pack()
    )
    builder.button(
        text="📞 Консультация",
        callback_data="request_consultation"
    )
    builder.button(
        text="🛒 Оформить заказ",
        callback_data="place_order"
    )

    builder.adjust(1, 2, 1)
    return builder.as_markup()


async def consultation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с ссылкой на чат менеджера."""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="💬 Перейти в чат с менеджером",
        url=f"https://t.me/{MANAGER_USERNAME}"
    )
    
    builder.adjust(1)  
    
    return builder.as_markup()


def back_to_catalog_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура для возврата в каталог"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📂 Вернуться в каталог",
        callback_data="back_to_catalog")
    
    return builder.as_markup()