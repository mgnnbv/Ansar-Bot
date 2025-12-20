from asyncio.log import logger
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove, KeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
# from aiogram.utils.keyboard import    


from handlers.callbacks import (
    AskCallback, CategoryCallback, SubcategoryCallback, 
    ProductCallback, ProductDetailCallback, 
    BackCallback
)
from databases.engine import AsyncSessionLocal
from keyboards.user_keyboards import (
    categories_keyboard, consultation_keyboard, products_keyboard, 
    subcategories_keyboard, command_keyboard, 
)
from databases.crud import (
    get_subcategories, get_products, 
    get_subcategory, get_category, get_product
)

from fsm import (QuestionStates, OrderStates
)

router = Router()

MANAGER_CHAT_ID = 5129105635

@router.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        markup = await categories_keyboard(session)

    await message.answer(
        "🛋️ <b>Добро пожаловать в магазин мебели!</b>\n\n"
        "Выберите интересующую вас категорию:",
        parse_mode="HTML",
        reply_markup=markup
    )


@router.callback_query(CategoryCallback.filter())
async def category_selected(
    callback: CallbackQuery,
    callback_data: CategoryCallback,
    state: FSMContext
):
    """Обработчик выбора категории"""
    category_id = callback_data.category_id
    
    async with AsyncSessionLocal() as session:
        category = await get_category(session, category_id)
        if not category:
            await callback.answer("❌ Категория не найдена", show_alert=True)
            return
        
        subcategories = await get_subcategories(session, category_id)
        
        await state.update_data(
            selected_category_id=category_id,
            selected_category_name=category.name
        )
        
        if not subcategories:
            markup = await command_keyboard(category_id=category_id)
            
            await callback.message.edit_text(
                f"📂 <b>{category.name}</b>\n\n"
                "В этой категории пока нет подкатегорий.\n"
                "Выберите действие:",
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            markup = await subcategories_keyboard(
                subcategories, 
                category_id=category_id
            )
            
            await callback.message.edit_text(
                f"📁 <b>Категория:</b> {category.name}\n\n"
                "Выберите подкатегорию:",
                parse_mode="HTML",
                reply_markup=markup
            )
    
    await callback.answer()


@router.callback_query(SubcategoryCallback.filter())
async def subcategory_selected(
    callback: CallbackQuery, 
    callback_data: SubcategoryCallback,
    state: FSMContext
):
    """Обработчик выбора подкатегории"""
    subcategory_id = callback_data.subcategory_id
    
    async with AsyncSessionLocal() as session:
        subcategory = await get_subcategory(session, subcategory_id)
        if not subcategory:
            await callback.answer("❌ Подкатегория не найдена", show_alert=True)
            return
        
        category = await get_category(session, subcategory.category_id)
        products = await get_products(session, subcategory_id)
        
        await state.update_data(
            selected_subcategory_id=subcategory_id,
            selected_subcategory_name=subcategory.name,
            selected_category_id=subcategory.category_id,
            selected_category_name=category.name if category else "Неизвестно"
            )
        
        if not products:
            markup = await command_keyboard(
                category_id=subcategory.category_id,
                subcategory_id=subcategory_id
            )
            
            await callback.message.edit_text(
                f"📦 <b>Подкатегория:</b> {subcategory.name}\n\n"
                "В этой подкатегории пока нет товаров.\n"
                "Выберите действие:",
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            markup = await products_keyboard(
                products=products,
                subcategory_id=subcategory_id,
                category_id=subcategory.category_id)
            
            category_name = category.name if category else "Неизвестно"
            await callback.message.edit_text(
                f"📦 <b>Категория:</b> {category_name}\n"
                f"📁 <b>Подкатегория:</b> {subcategory.name}\n\n"
                f"<b>Доступные товары:</b>",
                parse_mode="HTML",
                reply_markup=markup
            )
    
    await callback.answer()


@router.callback_query(ProductCallback.filter())
async def product_selected(
    callback: CallbackQuery, 
    callback_data: ProductCallback, 
    state: FSMContext):
    product_id = callback_data.product_id

    
    async with AsyncSessionLocal() as session:
        product = await get_product(session, product_id)
    
    if not product:
        await callback.message.answer("Товар не найден")
        return
    
    if product.images and len(product.images) > 0:
        first_image = product.images[0]
        await callback.message.answer(f"URL фото: {first_image.url}\n{product.name}\n\n{product.short_description}",
                                      reply_markup=await command_keyboard())
        
        await callback.message.answer_photo(
            photo=first_image.url,
            caption=f"Тест: {product.name}"
        )
    else:
        await callback.message.answer("Нет фото для этого товара")
    
    await callback.answer()


@router.callback_query(AskCallback.filter())
async def ask_question(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(QuestionStates.waiting)

    await callback.message.answer(
        "✍️ Напишите ваш вопрос одним сообщением:"
    )
    await callback.answer()

@router.message(QuestionStates.waiting)
async def process_question(
    message: Message,
    state: FSMContext
):
    await message.answer(
        "✅ Ваш вопрос получен!\n\n"
        f"📋 Вопрос: {message.text}\n\n"
        "Мы передали его менеджеру. Ответ придёт в ближайшее время.\n"
        "Также вы можете связаться с нами напрямую: @mgnnbv"
    )

    await state.clear()


@router.callback_query(F.data == "request_consultation")
async def request_consultation(callback: CallbackQuery):
    await callback.message.answer(
        "📞 Консультация\n\n"
        "Нажмите кнопку ниже, чтобы перейти в чат с менеджером 👇",
        reply_markup=consultation_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "place_order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.name)
    await callback.message.answer("🛒 Оформление заказа\n\nЧто вы хотите заказать?")
    await callback.answer()

@router.message(OrderStates.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.short_description)
    await message.answer("✏️ Кратко опишите товар или услугу:")

@router.message(OrderStates.short_description)
async def order_short_description(message: Message, state: FSMContext):
    await state.update_data(short_description=message.text)
    await state.set_state(OrderStates.additional_info)
    await message.answer("ℹ️ Дополнительная информация (необязательно):")


@router.message(OrderStates.additional_info)
async def order_additional_info(message: Message, state: FSMContext):
    await state.update_data(additional_info=message.text)
    await state.set_state(OrderStates.images)
    await message.answer("📸 Прикрепите фото товара(максимум 10) или напишите 'Пропустить':")

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

@router.message(OrderStates.images)
async def order_images(message: Message, state: FSMContext):
    data = await state.get_data()
    images = data.get('images', [])
    
    if message.photo:
        images.append(message.photo[-1].file_id)
        await state.update_data(images=images)
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Готово")]],
            resize_keyboard=True
        )
        
        await message.answer(
            f"✅ Фото {len(images)} добавлено.\n"
            f"Отправьте еще фото или нажмите 'Готово'.",
            reply_markup=keyboard
        )
        return
    
    elif message.text and message.text.lower() in ["готово", "пропустить"]:
        remove_keyboard = ReplyKeyboardRemove()
        
        text_to_manager = (
            f"📦 Новый заказ:\n"
            f"├ Название: {data['name']}\n"
            f"├ Описание: {data['short_description']}\n"
            f"├ Дополнительно: {data['additional_info']}\n"
            f"└ Фото: {len(images)} шт."
        )
        
        await message.bot.send_message(MANAGER_CHAT_ID, text_to_manager)
        
        if images:
            for i in range(0, len(images), 10):
                media_group = images[i:i+10]
                media = [InputMediaPhoto(media=fid) for fid in media_group]
                await message.bot.send_media_group(MANAGER_CHAT_ID, media)
        
        await message.answer(
            "✅ Заказ оформлен! Менеджер свяжется с вами.",
            reply_markup=remove_keyboard
        )
        
        await state.clear()
        return
    
    await message.answer("Пожалуйста, отправьте фото или нажмите 'Готово'.")


@router.callback_query(BackCallback.filter())
async def back_handler(
    callback: CallbackQuery,
    callback_data: BackCallback,
):
    if not callback.message:
        await callback.answer("Сообщение не найдено", show_alert=True)
        return

    try:
        async with AsyncSessionLocal() as session:
            if callback_data.to == "categories":
                markup = await categories_keyboard(session)
                text = "🛋️ <b>Выберите категорию:</b>"

            elif callback_data.to == "subcategories":
                category = await get_category(session, callback_data.parent_id)
                subcategories = await get_subcategories(session, callback_data.parent_id)

                markup = await subcategories_keyboard(
                    subcategories,
                    category_id=callback_data.parent_id
                )

                text = (
                    f"📂 <b>Категория:</b> "
                    f"{category.name if category else 'Неизвестно'}\n\n"
                    "Выберите подкатегорию:"
                )

            elif callback_data.to == "products":
                subcategory = await get_subcategory(session, callback_data.parent_id)
                products = await get_products(session, callback_data.parent_id)
                category = await get_category(session, subcategory.category_id)

                markup = await products_keyboard(
                    products,
                    subcategory_id=callback_data.parent_id
                )

                text = (
                    f"📦 <b>Категория:</b> {category.name if category else 'Неизвестно'}\n"
                    f"<b>Подкатегория:</b> {subcategory.name}\n\n"
                    "Выберите товар:"
                )

            elif callback_data.to == "product_detail":
                product = await get_product(session, callback_data.parent_id)
                products = await get_products(session, product.subcategory_id)

                markup = await products_keyboard(
                    products,
                    subcategory_id=product.subcategory_id,
                    category_id=product.subcategory.category_id
                )

                text = (
                    f"📦 <b>Подкатегория:</b> "
                    f"{product.subcategory.name if product.subcategory else 'Неизвестно'}\n\n"
                    "Выберите товар:"
                )
            else:
                await callback.answer("Неизвестное действие", show_alert=True)
                return

        await callback.message.edit_text(
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.exception("Ошибка в back_handler")
        await callback.answer("Произошла ошибка при навигации", show_alert=True)
        return

    else:
        await callback.answer()




@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата в каталог"""
    await send_welcome(callback.message, state)
    await callback.answer()


# @router.callback_query(F.data == "catalog")
# async def catalog_handler(callback: CallbackQuery, state: FSMContext):
#     """Обработчик кнопки 'Каталог'"""
#     await send_welcome(callback.message, state)
#     await callback.answer()


# @router.callback_query(F.data == "main_menu")
# async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
    
#     markup = await main_menu_keyboard()
    
#     await callback.message.edit_text(
#         "🏠 <b>Главное меню</b>\n\n"
#         "Выберите действие:",
#         parse_mode="HTML",
#         reply_markup=markup
#     )
#     await callback.answer()


# @router.message(F.text)
# async def handle_user_question(message: Message, state: FSMContext):
#     """Обработчик текстовых сообщений (вопросов о товаре)"""
#     data = await state.get_data()
    
#     if 'asking_about_product' in data:
#         product_id = data['asking_about_product']
#         product_name = data.get('asking_about_product_name', 'товар')
        
#         question_text = message.text
        
#         await message.answer(
#             f"✅ <b>Ваш вопрос получен!</b>\n\n"
#             f"<b>Товар:</b> {product_name}\n"
#             f"<b>Ваш вопрос:</b> {question_text}\n\n"
#             f"Менеджер свяжется с вами в ближайшее время.",
#             parse_mode="HTML"
#         )
        
#         await state.update_data(
#             asking_about_product=None,
#             asking_about_product_name=None
#         )
        
#         markup = await back_to_catalog_keyboard()
#         await message.answer(
#             "Хотите продолжить покупки?",
#             reply_markup=markup
#         )
#     else:
#         await send_welcome(message, state)