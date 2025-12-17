from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.utils.keyboard import InlineKeyboardBuilder

from databases.crud import get_categories
from handlers.callbacks import BackCallback, ProductCallback, ProductDetailCallback, SubcategoryCallback, CategoryCallback


async def categories_keyboard(
    session: AsyncSession,
    row_amount: int = 2
) -> InlineKeyboardMarkup | None:

    categories = await get_categories(session)

    if not categories:
        return None

    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.button(
            text=category.name,
            callback_data=CategoryCallback(
                category_id=category.id
            ).pack()
        )

    builder.adjust(row_amount)
    return builder.as_markup()



async def subcategories_keyboard(subcategories):
    builder = InlineKeyboardBuilder()

    for sub in subcategories:
        builder.button(
            text=sub.name,
            callback_data=SubcategoryCallback(
                subcategory_id=sub.id
            ).pack()
        )


    builder.button(
    text="⬅️ Назад",
    callback_data=BackCallback(
        to="categories"
    ).pack()
    )


    builder.adjust(1)
    return builder.as_markup()


async def products_keyboard(products):
    builder = InlineKeyboardBuilder()
    
    for product in products:
        builder.button(
            text=product.name,
            callback_data=ProductCallback(product_id=product.id).pack()
        )

    builder.adjust(1)
    return builder.as_markup()


async def product_detail_keyboard(products):
    builder = InlineKeyboardBuilder()
    
    for product in products:
        builder.button(
            text=product.name,
            callback_data=ProductDetailCallback(product_detail_id=product.id).pack()
        )

    builder.adjust(1)
    return builder.as_markup()


async def command_keyboard(category_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text="💬 Задать вопрос", callback_data="ask_question")
    builder.button(text="📞 Заказать консультацию", callback_data="request_consultation")
    builder.button(text="🛒 Оформить заказ", callback_data="place_order")

    builder.button(
    text="⬅️ Назад",
    callback_data=BackCallback(
        to="subcategories",
        parent_id=category_id
    ).pack()
    )

    builder.adjust(2, 2)
    return builder.as_markup()

