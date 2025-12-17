from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from databases.models import Product
from handlers.callbacks import CategoryCallback, SubcategoryCallback, ProductDetailCallback, BackCallback
from databases.engine import AsyncSessionLocal
from keyboards.user_keyboards import categories_keyboard, products_keyboard, subcategories_keyboard, command_keyboard
from databases.crud import get_subcategories, get_products, get_subcategory



router = Router()


@router.message(CommandStart())
async def send_welcome(message: Message):
    async with AsyncSessionLocal() as session:
        markup = await categories_keyboard(session)

    await message.answer(
        "Здравствуйте, этот бот поможет вам выбрать мебель.\n\nВыберите категорию:",
        reply_markup=markup
    )


@router.callback_query(CategoryCallback.filter())
async def category_selected(
    callback: CallbackQuery,
    callback_data: CategoryCallback
):
    category_id = callback_data.category_id

    async with AsyncSessionLocal() as session:
        subcategories = await get_subcategories(session, category_id)

    if not subcategories:
        await callback.answer("В этой категории пока нет подкатегорий", show_alert=True)
        return

    markup = await subcategories_keyboard(subcategories)

    await callback.message.edit_text(
        "Выберите подкатегорию:",
        reply_markup=markup
    )
    await callback.answer()


@router.callback_query(SubcategoryCallback.filter())
async def subcategory_selected(callback: CallbackQuery, callback_data: SubcategoryCallback):
    subcategory_id = callback_data.subcategory_id


    async with AsyncSessionLocal() as session:
        subcategory = await get_subcategory(session, subcategory_id)
        products = await get_products(session, subcategory_id)

    if products:
        markup = await products_keyboard(products)
        await callback.message.edit_text(
            "Выберите товар:",
            reply_markup=markup
        )
    else:
        markup = await command_keyboard(category_id=subcategory.category_id)
        await callback.message.edit_text(
            "В этой подкатегории пока нет товаров",
            reply_markup=markup
        )

    await callback.answer()


@router.callback_query(ProductDetailCallback.filter())
async def product_selected(callback: CallbackQuery, callback_data: ProductDetailCallback):
    product_id = callback_data.product_detail_id

    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        print(product)

    if not callback.message:
        return

    text = (
        f"🛏️ <b>{product.name}</b>\n\n"
        f"{product.short_description}\n\n"
        f"🌍 Страна: {product.country}\n"
        f"📏 Размеры: {product.size}\n"
        f"💰 Цена: {product.price} ₽"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()



@router.callback_query(BackCallback.filter())
async def back_handler(
    callback: CallbackQuery,
    callback_data: BackCallback
):
    async with AsyncSessionLocal() as session:

        if callback_data.to == "categories":
            markup = await categories_keyboard(session)
            text = "Выберите категорию:"

        elif callback_data.to == "subcategories":
            subcategories = await get_subcategories(
                session, callback_data.parent_id
            )
            markup = await subcategories_keyboard(subcategories)
            text = "Выберите подкатегорию:"

        elif callback_data.to == "products":
            products = await get_products(
                session, callback_data.parent_id
            )
            markup = await command_keyboard(products)
            text = "Выберите товар:"

    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()



