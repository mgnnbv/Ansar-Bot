from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload
from aiogram.exceptions import TelegramBadRequest



from databases.crud import get_categories, get_subcategories, return_to_admin_panel, safe_edit_message, safe_send_media, show_product_list_by_name
from databases.engine import AsyncSessionLocal
from databases.models import Category, Product, ProductImage, Subcategory
from fsm import AddProductStates, EditProductStates
from aiogram.utils.keyboard import InlineKeyboardBuilder


from keyboards.admin_keyboards import back_to_edit_keyboard, get_admin_keyboard, get_cancel_edit_keyboard, get_cancel_keyboard, get_edit_product_keyboard, get_image_management_keyboard, photos_start_keyboard


admin_router = Router()


# ========== СТАРТ КОМАННДЫ И ХЕНДЛЕРЫ ==========
@admin_router.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        '👑 Здравствуйте, менеджер!\n'
        'Нажмите на кнопку, чтобы увидеть ваши команды:',
        reply_markup=get_admin_keyboard()
    )


@admin_router.message(Command('main_menu'))
async def start_cmd(message: Message):
    await message.answer(
        '👑 Здравствуйте, менеджер!\n'
        'Нажмите на кнопку, чтобы увидеть ваши команды:',
        reply_markup=get_admin_keyboard()
    )



@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    """Панель администратора"""
    await message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Выберите команду:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "👑 <b>Панель администратора</b>\n\nВыберите команду:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()


# ========== ДОБАВЛЕНИЕ ТОВАРА ==========

@admin_router.callback_query(F.data == "admin_add_product")
async def admin_add_product_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    text = (
        "📦 <b>Добавление нового товара</b>\n\n"
        "Введите <b>название товара</b> или нажмите кнопку для отмены:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_cancel_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=get_cancel_keyboard(),
            parse_mode=ParseMode.HTML
        )

    await state.set_state(AddProductStates.waiting_for_name)
    await callback.answer()

@admin_router.message(AddProductStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if not message.text:
        return

    name = message.text.strip()

    if len(name) < 2:
        await message.answer(
            "❌ Название слишком короткое (минимум 2 символа).",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(name=name)

    async with AsyncSessionLocal() as session:
        categories = await get_categories(session)

    if not categories:
        await message.answer(
            "❌ Категории не найдены. Сначала создайте категорию.",
            reply_markup=get_admin_keyboard()
        )
        await state.clear()
        return

    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=f"cat_{category.id}"
        )

    builder.button(text="❌ Отменить", callback_data="cancel_operation")
    builder.adjust(2)

    await message.answer(
        f"✅ <b>Название:</b> {name}\n\nВыберите <b>категорию</b>:",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(AddProductStates.waiting_for_category)

@admin_router.callback_query(
    AddProductStates.waiting_for_category,
    F.data.startswith("cat_")
)
async def process_category(callback: CallbackQuery, state: FSMContext):
    try:
        category_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("Ошибка категории")
        return

    async with AsyncSessionLocal() as session:
        category = await session.get(Category, category_id)
        subcategories = await get_subcategories(session, category_id)

    if not category:
        await callback.answer("Категория не найдена")
        return

    await state.update_data(
        category_id=category.id,
        category_name=category.name
    )

    builder = InlineKeyboardBuilder()

    if subcategories:
        for sub in subcategories:
            builder.button(text=sub.name, callback_data=f"sub_{sub.id}")
        builder.button(text="⏭ Пропустить", callback_data="skip_subcategory")
    else:
        builder.button(text="⏭ Подкатегорий нет", callback_data="skip_subcategory")

    builder.button(text="❌ Отменить", callback_data="cancel_operation")
    builder.adjust(2)

    data = await state.get_data()

    await callback.message.edit_text(
        f"✅ <b>Название:</b> {data['name']}\n"
        f"✅ <b>Категория:</b> {category.name}\n\n"
        "Выберите <b>подкатегорию</b>:",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(AddProductStates.waiting_for_subcategory)
    await callback.answer()

@admin_router.callback_query(
    AddProductStates.waiting_for_subcategory,
    F.data.startswith("sub_")
)
async def process_subcategory(callback: CallbackQuery, state: FSMContext):
    sub_id = int(callback.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        sub = await session.get(Subcategory, sub_id)

    if not sub:
        await callback.answer("Подкатегория не найдена")
        return

    await state.update_data(
        subcategory_id=sub.id,
        subcategory_name=sub.name
    )

    await go_to_description(callback, state, sub.name)


async def go_to_description(callback: CallbackQuery, state: FSMContext, subcategory_name: str):
    data = await state.get_data()

    await callback.message.edit_text(
        f"✅ <b>Название:</b> {data['name']}\n"
        f"✅ <b>Категория:</b> {data['category_name']}\n"
        f"✅ <b>Подкатегория:</b> {subcategory_name}\n\n"
        "Введите <b>краткое описание</b> (мин. 10 символов):",
        parse_mode=ParseMode.HTML
    )

    await state.set_state(AddProductStates.waiting_for_short_description)
    await callback.answer()

@admin_router.callback_query(
    AddProductStates.waiting_for_subcategory,
    F.data == "skip_subcategory"
)
async def skip_subcategory(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subcategory_id=None, subcategory_name="Не выбрана")
    await go_to_description(callback, state, "Не выбрана")

@admin_router.callback_query(
    AddProductStates.waiting_for_subcategory,
    F.data == "skip_subcategory"
)
async def skip_subcategory(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subcategory_id=None, subcategory_name="Не выбрана")
    await go_to_description(callback, state, "Не выбрана")

@admin_router.message(AddProductStates.waiting_for_short_description)
async def process_short_description(message: Message, state: FSMContext):
    """Обработка краткого описания"""
    short_description = message.text.strip()
    
    if len(short_description) < 10:
        await message.answer(
            "❌ Описание слишком короткое (минимум 10 символов). Введите еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(short_description=short_description)
    
    await message.answer(
        "📝 Теперь введите <b>дополнительную информацию</b> о товаре:\n"
        "(материалы, размеры, особенности, характеристики и т.д.)\n"
        "Или напишите <b>'нет'</b>, если дополнительная информация не требуется.\n\n"
        "<i>Пример: Материал: дерево, Размеры: 200x180 см, Цвет: белый</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AddProductStates.waiting_for_additional_info)

@admin_router.message(AddProductStates.waiting_for_additional_info)
async def process_additional_info(message: Message, state: FSMContext):
    """Обработка дополнительной информации"""
    additional_info = message.text.strip()
    
    if additional_info.lower() == 'нет':
        additional_info = ''
    elif len(additional_info) < 5 and additional_info.lower() != 'нет':
        await message.answer(
            "❌ Слишком короткая информация. Введите подробнее или напишите 'нет':",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(additional_info=additional_info)
    
    await message.answer(
        "📸 Теперь отправьте <b>фотографии товара</b> (можно несколько):\n\n"
        "📌 <b>Инструкция:</b>\n"
        "1. Отправляйте фото по одному\n"
        "2. Первое фото будет главным\n"
        "3. Когда все фото загружены, нажмите кнопку <b>'Готово'</b>\n\n"
        "Или кнопку /cancel_operation для отмены.",
        reply_markup=photos_start_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AddProductStates.waiting_for_photos)

@admin_router.callback_query(
    F.data.in_({"photos_done", "skip_photos"}),
    AddProductStates.waiting_for_photos
)
async def photos_done_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    name = data.get("name")
    short_description = data.get("short_description")
    additional_info = data.get("additional_info") or "Не указана"

    text = (
        "📋 <b>Сводка товара</b>\n\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {short_description}\n"
        f"<b>Доп. информация:</b> {additional_info}\n"
        f"<b>Фото:</b> {len(photos)} шт.\n\n"
        "Подтвердить сохранение?"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Сохранить", callback_data="confirm_save")
    builder.button(text="❌ Отмена", callback_data="cancel_operation")
    builder.adjust(1)

    if photos:
        await callback.message.answer_photo(
            photo=photos[0]["file_id"],
            caption=text,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )

    await state.set_state(AddProductStates.waiting_for_final_confirm)

    await callback.answer()

@admin_router.callback_query(
    F.data == "confirm_save",
    AddProductStates.waiting_for_final_confirm
)
async def save_product(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    photos_data = data.get("photos", [])

    async with AsyncSessionLocal() as session:
        try:
            product = Product(
                name=data["name"],
                short_description=data.get("short_description"),
                additional_info=data.get("additional_info", ""),
                category_id=data.get("category_id"),
                subcategory_id=data.get("subcategory_id")
            )

            session.add(product)
            await session.flush()

            # сохраняем фото (если есть)
            for photo_info in photos_data:
                session.add(
                    ProductImage(
                        url=photo_info.get("file_id", ""),
                        product_id=product.id
                    )
                )

            await session.commit()

            success_message = (
                f"✅ <b>Товар успешно сохранен!</b>\n\n"
                f"<b>ID:</b> {product.id}\n"
                f"<b>Название:</b> {product.name}\n"
                f"<b>Фотографий:</b> {len(photos_data)}"
            )

            if photos_data:
                await callback.message.edit_caption(
                    caption=success_message,
                    reply_markup=None,
                    parse_mode="HTML"
                )
            else:
                await callback.message.edit_text(
                    text=success_message,
                    reply_markup=None,
                    parse_mode="HTML"
                )

            await callback.message.answer(
                "👑 <b>Панель администратора</b>\n\n"
                "Выберите команду:",
                reply_markup=get_admin_keyboard(),
                parse_mode="HTML"
            )

        except Exception as e:
            await session.rollback()

            error_text = f"❌ Ошибка при сохранении: {e}"

            if callback.message.caption:
                await callback.message.edit_caption(error_text)
            else:
                await callback.message.edit_text(error_text)

        finally:
            await state.clear()

    await callback.answer()



@admin_router.message(
    AddProductStates.waiting_for_photos,
    F.content_type != ContentType.PHOTO
)
async def photos_only(message: Message):
    await message.answer(
        "❌ Сейчас можно отправлять только фотографии.\n"
        "Когда закончите — нажмите «Готово»."
    )


@admin_router.callback_query(
    F.data == "photos_done",
    AddProductStates.waiting_for_photos
)
async def photos_done_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if not photos:
        await callback.answer("❌ Добавьте хотя бы одно фото", show_alert=True)
        return

    name = data.get("name")
    short_description = data.get("short_description")
    additional_info = data.get("additional_info") or "Не указана"

    text = (
        "📋 <b>Сводка товара</b>\n\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {short_description}\n"
        f"<b>Доп. информация:</b> {additional_info}\n"
        f"<b>Фото:</b> {len(photos)} шт.\n\n"
        "Подтвердить сохранение?"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Сохранить", callback_data="confirm_save")
    builder.button(text="❌ Отменить", callback_data="cancel_operation")
    builder.adjust(1)

    await callback.message.answer_photo(
        photo=photos[0]["file_id"],
        caption=text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(AddProductStates.waiting_for_final_confirm)
    await callback.answer()


@admin_router.callback_query(F.data == "confirm_save", AddProductStates.waiting_for_final_confirm)
async def save_product(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Сохранение товара в БД с проверкой фото"""
    data = await state.get_data()
    photos_data = data.get("photos", [])

    if not photos_data:
        await callback.message.edit_text(
            "❌ Вы не добавили ни одного фото.\n"
            "Отправьте хотя бы одно фото или /cancel для отмены.",
            reply_markup=get_cancel_keyboard()
        )
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        try:
            product = Product(
                name=data['name'],
                short_description=data.get('short_description'),
                additional_info=data.get('additional_info', ''),
                category_id=data.get('category_id'),
                subcategory_id=data.get('subcategory_id')
            )
            session.add(product)
            await session.flush()

            for photo_info in photos_data:
                file_id = photo_info.get("file_id", "")
                product_image = ProductImage(
                    url=file_id,
                    product_id=product.id
                )
                session.add(product_image)

            await session.commit()

            category_name = "Не указано"
            if product.category_id:
                cat_result = await session.execute(
                    select(Category).where(Category.id == product.category_id)
                )
                category = cat_result.scalar_one_or_none()
                if category:
                    category_name = category.name

            subcategory_name = "Не указано"
            if product.subcategory_id:
                subcat_result = await session.execute(
                    select(Subcategory).where(Subcategory.id == product.subcategory_id)
                )
                subcategory = subcat_result.scalar_one_or_none()
                if subcategory:
                    subcategory_name = subcategory.name

            success_message = (
                f"✅ <b>Товар успешно сохранен!</b>\n\n"
                f"<b>ID:</b> {product.id}\n"
                f"<b>Название:</b> {product.name}\n"
                f"<b>Категория:</b> {category_name}\n"
                f"<b>Подкатегория:</b> {subcategory_name}\n"
                f"<b>Описание:</b> {product.short_description[:50]}...\n"
                f"<b>Фотографий:</b> {len(photos_data)}"
            )

            first_photo = photos_data[0]
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=first_photo.get("file_id"),
                caption=success_message,
                reply_markup=None,
                parse_mode=ParseMode.HTML
            )
            await callback.message.answer(
                "👑 <b>Панель администратора</b>\n\n"
                "Выберите команду:",
                reply_markup=get_admin_keyboard(),
                parse_mode=ParseMode.HTML
            )

        except Exception as e:
            await session.rollback()
            await callback.message.answer(
                f"❌ Ошибка при сохранении товара: {str(e)}"
            )
        finally:
            await state.clear()

    await callback.answer()


# ========== ИЗМЕНЕНИЕ ТОВАРА ==========

@admin_router.callback_query(F.data == "admin_edit_product")
async def admin_edit_product_handler(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования товара - поиск по названию"""
    await state.clear()
    
    await callback.message.edit_text(
        "🔍 <b>Поиск товара для редактирования</b>\n\n"
        "📝 <b>Введите название товара (полностью или частично):</b>\n\n"
        "<i>Примеры:</i>\n"
        "• <code>диван</code> - найдет все товары со словом 'диван'\n"
        "• <code>стол обеденный</code> - найдет товары с этими словами\n"
        "• <code>кресло</code> - найдет 'кресло', 'кресла', 'креслом' и т.д.",
        reply_markup=get_cancel_edit_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(EditProductStates.waiting_for_product_name)
    await callback.answer()

@admin_router.message(EditProductStates.waiting_for_product_name)
async def process_product_search_by_name(message: Message, state: FSMContext):
    """Поиск товара по названию"""
    search_name = message.text.strip()
    
    if not search_name or len(search_name) < 2:
        await message.answer(
            "❌ <b>Название слишком короткое!</b>\n"
            "Введите минимум 2 символа:",
            reply_markup=get_cancel_edit_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.category),
                selectinload(Product.subcategory)
            )
            .where(Product.name.ilike(f"%{search_name}%"))
            .order_by(Product.name)
            .limit(15)  
        )
        
        products = result.scalars().all()
        
        if not products:
            all_result = await session.execute(
                select(Product)
                .options(selectinload(Product.category))
                .order_by(Product.name)
                .limit(10)
            )
            all_products = all_result.scalars().all()
            
            if all_products:
                all_products_text = "\n".join([
                    f"• <b>{p.name}</b> (ID: {p.id})" 
                    for p in all_products
                ])
                
                await message.answer(
                    f"❌ <b>Товары не найдены по запросу:</b> <code>{search_name}</code>\n\n"
                    f"📋 <b>Все товары в базе:</b>\n{all_products_text}\n\n"
                    "Введите другое название или часть названия:",
                    reply_markup=get_cancel_edit_keyboard(),
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.answer(
                    "❌ <b>В базе данных нет товаров.</b>\n\n"
                    "Сначала добавьте товары через меню <b>'➕ Добавить товар'</b>",
                    reply_markup=get_cancel_edit_keyboard(),
                    parse_mode=ParseMode.HTML
                )
            return
        
        if len(products) == 1:
            product = products[0]
            await show_product_for_edit(message, state, product)
        else:
            await show_product_list_by_name(message, state, products, search_name)  
            

async def show_product_list(message: Message, state: FSMContext, products):
    """Показ списка найденных товаров"""
    builder = InlineKeyboardBuilder()
    
    for product in products:
        builder.button(
            text=f"{product.id}: {product.name[:30]}",
            callback_data=f"select_product_{product.id}"
        )
    
    builder.button(text="❌ Отменить", callback_data="cancel_edit")
    builder.adjust(1)
    
    products_text = "\n".join([f"{p.id}: {p.name}" for p in products])
    
    await message.answer(
        f"🔍 <b>Найдено товаров:</b> {len(products)}\n\n"
        f"{products_text}\n\n"
        "Выберите товар для редактирования:",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(EditProductStates.waiting_for_product_choice)

async def show_product_for_edit(message: Message, state: FSMContext, product):
    """Показ товара для редактирования (упрощенная версия)"""
    async with AsyncSessionLocal() as session:
        product = await session.get(
            Product, 
            product.id,
            options=[
                selectinload(Product.images),
                selectinload(Product.category),
                selectinload(Product.subcategory)
            ]
        )
        
        await state.update_data(product_id=product.id)
        
        category_name = product.category.name if product.category else "❌ Не указана"
        subcategory_name = product.subcategory.name if product.subcategory else "❌ Не указана"
        
        short_desc = product.short_description
        if short_desc and len(short_desc) > 80:
            short_desc = short_desc[:77] + "..."
        
        add_info = product.additional_info
        if add_info and len(add_info) > 50:
            add_info = add_info[:47] + "..."
        
        product_info = (
            f"🛒 <b>Товар для редактирования</b>\n\n"
            f"📝 <b>Название:</b>\n{product.name}\n\n"
            f"📋 <b>Краткое описание:</b>\n{short_desc or '❌ Не указано'}\n\n"
            f"ℹ️ <b>Доп. информация:</b>\n{add_info or '❌ Не указана'}\n\n"
            f"📁 <b>Категория:</b> {category_name}\n"
            f"📂 <b>Подкатегория:</b> {subcategory_name}\n"
            f"📷 <b>Изображений:</b> {len(product.images)}"
        )
        
        builder = InlineKeyboardBuilder()
        
        builder.button(text="✏️ Название", callback_data="edit_name")
        builder.button(text="📝 Описание", callback_data="edit_short_desc")
        builder.button(text="ℹ️ Доп. инфо", callback_data="edit_add_info")
        builder.button(text="📁 Категория", callback_data="edit_category")
        builder.button(text="🖼️ Изображения", callback_data="edit_images")
        builder.button(text="✅ Сохранить", callback_data="finish_edit")
        builder.button(text="❌ Отменить", callback_data="cancel_edit")
        
        builder.adjust(2, 2, 2, 1, 1)
        
        if product.images:
            first_image = product.images[0]
            try:
                await message.answer_photo(
                    photo=first_image.url,
                    caption=product_info,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
            except:
                await message.answer(
                    product_info + f"\n\n⚠️ <i>Не удалось загрузить изображение</i>",
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
        else:
            await message.answer(
                product_info + f"\n\n⚠️ <i>Нет изображений</i>",
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        
        await state.set_state(EditProductStates.waiting_for_edit_choice)

@admin_router.callback_query(F.data.startswith("select_product_"), EditProductStates.waiting_for_product_choice)
async def select_product_handler(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора товара из списка"""
    product_id_str = callback.data.replace("select_product_", "")
    
    try:
        product_id = int(product_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID товара")
        return
    
    async with AsyncSessionLocal() as session:
        product = await session.get(
            Product, 
            product_id,
            options=[selectinload(Product.images)]
        )
        
        if not product:
            await callback.message.edit_text(
                "❌ Товар не найден. Попробуйте снова:",
                reply_markup=get_cancel_edit_keyboard()
            )
            return
        
        await show_product_for_edit(callback.message, state, product)
    
    await callback.answer()


# ========== ВЫБОР ПОЛЯ ДЛЯ РЕДАКТИРОВАНИЯ ==========

@admin_router.callback_query(F.data.startswith("edit_"), EditProductStates.waiting_for_edit_choice)
async def edit_field_choice(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора поля для редактирования"""

    action = callback.data
    data = await state.get_data()
    product_id = data.get('product_id')

    if not product_id:
        await callback.answer("❌ Ошибка: товар не найден в сессии", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)

        if not product:
            text = "❌ Товар не найден в базе данных"
            # Если можно редактировать текст — edit_text, иначе создаём новое сообщение
            if callback.message.text is not None or callback.message.caption is not None:
                await callback.message.edit_text(text, reply_markup=get_cancel_edit_keyboard())
            else:
                await callback.message.answer(text, reply_markup=get_cancel_edit_keyboard())
            return

        # --------------------- Редактирование названия ---------------------
        if action == "edit_name":
            await state.set_state(EditProductStates.waiting_for_name_edit)
            await safe_edit_message(
                callback.message,
                f"✏️ <b>Редактирование названия</b>\n\n"
                f"Текущее название:\n<b>{product.name}</b>\n\n"
                "Введите новое название:",
                get_cancel_edit_keyboard()
            )

        # --------------------- Редактирование короткого описания ---------------------
        elif action == "edit_short_desc":
            await state.set_state(EditProductStates.waiting_for_short_desc_edit)
            await safe_edit_message(
                callback.message,
                f"📝 <b>Редактирование описания</b>\n\n"
                f"{product.short_description or '❌ Не указано'}\n\n"
                "Введите новое описание:"
            )

        # --------------------- Редактирование дополнительной информации ---------------------
        elif action == "edit_add_info":
            await state.set_state(EditProductStates.waiting_for_additional_info_edit)
            await safe_edit_message(
                callback.message,
                f"ℹ️ <b>Редактирование доп. информации</b>\n\n"
                f"{product.additional_info or '❌ Не указана'}\n\n"
                "Введите новую информацию:",
                get_cancel_edit_keyboard()
            )

        # --------------------- Редактирование категории ---------------------
        elif action == "edit_category":
            categories = await get_categories(session)

            builder = InlineKeyboardBuilder()
            for category in categories:
                builder.button(
                    text=category.name,
                    callback_data=f"edit_cat_{category.id}"
                )
            builder.button(text="↩️ Назад", callback_data="back_to_edit")
            builder.adjust(2)

            await callback.message.answer(
                "📁 <b>Выбор категории</b>\n\nВыберите новую категорию:",
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

            await state.set_state(EditProductStates.waiting_for_category_edit)
            await callback.answer()
            return


        # --------------------- Управление изображениями ---------------------
        elif action == "edit_images":
            keyboard = get_image_management_keyboard()
            text = "🖼️ <b>Управление изображениями</b>\n\nВыберите действие:"

            await safe_edit_message(callback.message, text, keyboard)


            await state.set_state(EditProductStates.waiting_for_image_choice)
            await callback.answer()
            return


        # --------------------- Просмотр товара ---------------------
        elif action == "view_product":
            await show_product_for_edit(callback.message, state, product)
            await callback.answer()
            return

    await callback.answer()


# ========== РЕДАКТИРОВАНИЕ ТЕКСТОВЫХ ПОЛЕЙ ==========

@admin_router.message(EditProductStates.waiting_for_name_edit)
async def process_name_edit(message: Message, state: FSMContext):
    """Обработка нового названия"""
    new_name = message.text.strip()
    
    if len(new_name) < 2:
        await message.answer(
            "❌ Название слишком короткое (минимум 2 символа). Введите еще раз:",
            reply_markup=get_cancel_edit_keyboard()
        )
        return
    
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if product:
            product.name = new_name
            await session.commit()
            
            await message.answer(
                f"✅ Название обновлено: <b>{new_name}</b>",
                parse_mode=ParseMode.HTML
            )
            
        await show_product_for_edit(message, state, product)
        await state.set_state(EditProductStates.waiting_for_edit_choice)

@admin_router.message(EditProductStates.waiting_for_short_desc_edit)
async def process_short_desc_edit(message: Message, state: FSMContext):
    """Обработка нового описания"""
    new_desc = message.text.strip()
    
    if len(new_desc) < 10:
        await message.answer(
            "❌ Описание слишком короткое (минимум 10 символов). Введите еще раз:",
            reply_markup=get_cancel_edit_keyboard()
        )
        return
    
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if product:
            product.short_description = new_desc
            await session.commit()
            
            await message.answer(
                f"✅ Описание обновлено!",
                parse_mode=ParseMode.HTML
            )
            
        await show_product_for_edit(message, state, product)
        await state.set_state(EditProductStates.waiting_for_edit_choice)

@admin_router.message(EditProductStates.waiting_for_additional_info_edit)
async def process_additional_info_edit(message: Message, state: FSMContext):
    """Обработка новой дополнительной информации"""
    new_info = message.text.strip()
    
    if new_info.lower() == 'нет':
        new_info = ''
    elif len(new_info) < 5 and new_info.lower() != 'нет':
        await message.answer(
            "❌ Слишком короткая информация. Введите подробнее или напишите 'нет':",
            reply_markup=get_cancel_edit_keyboard()
        )
        return
    
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if product:
            product.additional_info = new_info
            await session.commit()
            
            await message.answer(
                f"✅ Дополнительная информация обновлена!",
                parse_mode=ParseMode.HTML
            )
            
        await show_product_for_edit(message, state, product)
        await state.set_state(EditProductStates.waiting_for_edit_choice)


# ========== РЕДАКТИРОВАНИЕ КАТЕГОРИЙ ==========
@admin_router.callback_query(F.data.startswith("edit_cat_"), EditProductStates.waiting_for_category_edit)
async def process_category_edit(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора новой категории"""
    category_id_str = callback.data.replace("edit_cat_", "")
    
    try:
        category_id = int(category_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID категории")
        return
    
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        subcategories = await get_subcategories(session, category_id)
        
        builder = InlineKeyboardBuilder()
        
        if subcategories:
            for subcategory in subcategories:
                builder.button(
                    text=subcategory.name,
                    callback_data=f"edit_sub_{subcategory.id}"
                )
            builder.button(text="⏭️ Без подкатегории", callback_data="edit_skip_sub")
        else:
            builder.button(text="⏭️ Нет подкатегорий", callback_data="edit_skip_sub")
        
        builder.button(text="↩️ Назад", callback_data="back_to_edit")
        builder.adjust(2)
        
        category = await session.get(Category, category_id)
        
        await callback.message.edit_text(
            f"📁 <b>Категория:</b> {category.name}\n\n"
            "Выберите подкатегорию:",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        
        await state.update_data(temp_category_id=category_id)
        await state.set_state(EditProductStates.waiting_for_subcategory_edit)
    
    await callback.answer()

@admin_router.callback_query(F.data.startswith("edit_sub_"), EditProductStates.waiting_for_subcategory_edit)
async def process_subcategory_edit(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора подкатегории"""
    subcategory_id_str = callback.data.replace("edit_sub_", "")
    
    try:
        subcategory_id = int(subcategory_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID подкатегории")
        return
    
    data = await state.get_data()
    product_id = data.get('product_id')
    category_id = data.get('temp_category_id')
    
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if product:
            product.category_id = category_id
            product.subcategory_id = subcategory_id
            await session.commit()
            
            subcategory = await session.get(Subcategory, subcategory_id)
            category = await session.get(Category, category_id)
            
            await callback.message.edit_text(
                f"✅ Категория обновлена:\n"
                f"<b>Категория:</b> {category.name}\n"
                f"<b>Подкатегория:</b> {subcategory.name}",
                parse_mode=ParseMode.HTML
            )
            
        await show_product_for_edit(callback.message, state, product)
        await state.set_state(EditProductStates.waiting_for_edit_choice)
    
    await callback.answer()

@admin_router.callback_query(F.data == "edit_skip_sub", EditProductStates.waiting_for_subcategory_edit)
async def skip_subcategory_edit(callback: CallbackQuery, state: FSMContext):
    """Пропуск подкатегории"""
    data = await state.get_data()
    product_id = data.get('product_id')
    category_id = data.get('temp_category_id')
    
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if product:
            product.category_id = category_id
            product.subcategory_id = None  
            await session.commit()
            
            category = await session.get(Category, category_id)
            
            await callback.message.edit_text(
                f"✅ Категория обновлена:\n"
                f"<b>Категория:</b> {category.name}\n"
                f"<b>Подкатегория:</b> Не указана",
                parse_mode=ParseMode.HTML
            )
            
        await show_product_for_edit(callback.message, state, product)
        await state.set_state(EditProductStates.waiting_for_edit_choice)
    
    await callback.answer()


# ========== СТАТИСТИКА ТОВАРОВ ==========

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        categories_count = await session.scalar(
            select(func.count(Category.id))
        )
        subcategories_count = await session.scalar(
            select(func.count(Subcategory.id))
        )
        products_count = await session.scalar(
            select(func.count(Product.id))
        )

    text = (
        "📊 <b>Статистика магазина</b>\n\n"
        f"📁 Категорий: <b>{categories_count}</b>\n"
        f"🗂️ Подкатегорий: <b>{subcategories_count}</b>\n"
        f"📦 Товаров: <b>{products_count}</b>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Назад в меню", callback_data="back_to_admin_menu")
    builder.adjust(1)

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await callback.answer()


# ========== УДАЛЕНИЕ ТОВАРА ==========

@admin_router.callback_query(F.data == "admin_delete_product")
async def show_product_list_for_delete(callback: CallbackQuery, state: FSMContext):
    """Показ списка товаров для удаления"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

    if not products:
        await callback.message.answer("❌ Товаров для удаления нет")
        return

    builder = InlineKeyboardBuilder()

    for product in products:
        builder.button(
            text=f"id({product.id}): {product.name[:30]}",
            callback_data=f"delete_product_{product.id}"
        )

    builder.button(text="❌ Отменить", callback_data="cancel_operation")
    builder.adjust(1)

    products_text = "\n".join([f"{p.id}: {p.name}" for p in products])

    await callback.message.answer(
        f"🔍 <b>Найдено товаров:</b> {len(products)}\n\n"
        f"{products_text}\n\n"
        "Выберите и напишите товар для удаления:",
        parse_mode=ParseMode.HTML
    )

@admin_router.message(F.text)
async def delete_product_by_name(message: Message, state: FSMContext):
    text = message.text.strip()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product).where(Product.name.ilike(f"%{text}%"))
        )
        products = result.scalars().all()

    if not products:
        await message.answer("❌ Товар не найден. Попробуйте ещё раз или /cancel.")
        return

    product = products[0]  
    await state.update_data(product_id=product.id)
    await state.set_state("waiting_for_delete_confirmation")  

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить", callback_data="delete_product_confirmed")
    builder.button(text="❌ Отмена", callback_data="cancel_operation")
    builder.adjust(1)

    print("FSM state перед кнопкой:", await state.get_state())  

    await message.answer(
        f"⚠️ Вы уверены, что хотите удалить товар <b>{product.name}</b>?\n"
        "Это действие нельзя отменить.",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

@admin_router.callback_query(F.data == "delete_product_confirmed")
async def delete_product_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")

    if not product_id:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        await session.execute(delete(ProductImage).where(ProductImage.product_id == product_id))
        await session.execute(delete(Product).where(Product.id == product_id))
        await session.commit()

    await callback.message.answer("🗑️ Товар успешно удалён")
    await callback.message.answer(
        "👑 Панель администратора",
        reply_markup=get_admin_keyboard(),
        parse_mode=ParseMode.HTML
    )

    await state.clear()
    await callback.answer()


# ========== УПРАВЛЕНИЕ ИЗОБРАЖЕНИЯМИ ==========

@admin_router.callback_query(
    F.data == "add_image",
    EditProductStates.waiting_for_image_choice
)
async def add_image_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ <b>Добавление изображения</b>\n\n"
        "Отправьте фото (как фото или файл) либо URL:",
        reply_markup=get_cancel_edit_keyboard(),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(EditProductStates.waiting_for_image_upload)
    await callback.answer()


@admin_router.message(
    EditProductStates.waiting_for_image_upload,
    F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT})
)
async def process_image_photo(message: Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        if not message.document.mime_type.startswith("image/"):
            await message.answer("❌ Файл должен быть изображением")
            return
        file_id = message.document.file_id

    data = await state.get_data()
    product_id = data.get("product_id")

    async with AsyncSessionLocal() as session:
        session.add(ProductImage(url=file_id, product_id=product_id))
        await session.commit()

    await message.answer(
        "✅ Изображение добавлено",
        reply_markup=get_image_management_keyboard()
    )

    await state.set_state(EditProductStates.waiting_for_image_choice)

@admin_router.message(
    EditProductStates.waiting_for_image_upload,
    F.content_type == ContentType.TEXT
)
async def process_image_url(message: Message, state: FSMContext):
    url = message.text.strip()

    if not url.startswith(("http://", "https://")):
        await message.answer(
            "❌ URL должен начинаться с http:// или https://",
            reply_markup=get_cancel_edit_keyboard()
        )
        return

    data = await state.get_data()
    product_id = data.get("product_id")

    async with AsyncSessionLocal() as session:
        session.add(ProductImage(url=url, product_id=product_id))
        await session.commit()

    await message.answer(
        "✅ Изображение добавлено по URL",
        reply_markup=get_image_management_keyboard()
    )

    await state.set_state(EditProductStates.waiting_for_image_choice)

@admin_router.callback_query(
    F.data == "delete_image",
    EditProductStates.waiting_for_image_choice
)
async def delete_image_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.id)
        )
        images = result.scalars().all()

    if not images:
        await callback.message.edit_text(
            "❌ У товара нет изображений для удаления",
            reply_markup=get_image_management_keyboard()
        )
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()

    for img in images:
        builder.button(
            text=f"🗑️ ID {img.id}",
            callback_data=f"delete_img_{img.id}"
        )

    builder.button(text="↩️ Назад", callback_data="back_to_images")
    builder.adjust(1)

    await callback.message.edit_text(
        "🗑️ <b>Удаление изображения</b>\n\n"
        f"Всего изображений: {len(images)}\n"
        "Выберите изображение:",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(EditProductStates.waiting_for_image_delete)
    await callback.answer()

@admin_router.callback_query(
    F.data.startswith("delete_img_"),
    EditProductStates.waiting_for_image_delete
)
async def process_image_delete(callback: CallbackQuery, state: FSMContext):
    image_id_str = callback.data.removeprefix("delete_img_")

    if not image_id_str.isdigit():
        await callback.answer("❌ Неверный ID")
        return

    image_id = int(image_id_str)

    data = await state.get_data()
    product_id = data.get("product_id")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            delete(ProductImage).where(
                ProductImage.id == image_id,
                ProductImage.product_id == product_id
            )
        )
        await session.commit()

    if result.rowcount == 0:
        await callback.answer("❌ Изображение не найдено")
        return

    await callback.message.edit_text(
        f"✅ Изображение #{image_id} удалено",
        reply_markup=get_image_management_keyboard()
    )

    await state.set_state(EditProductStates.waiting_for_image_choice)
    await callback.answer()

@admin_router.callback_query(
    F.data == "view_images",
    EditProductStates.waiting_for_image_choice
)
async def view_images_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.id)
        )
        images = result.scalars().all()

    if not images:
        await callback.answer("❌ У товара нет изображений", show_alert=True)
        return

    for i, image in enumerate(images, start=1):
        await safe_send_media(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
            media=image.url,
            caption=f"📷 {i} из {len(images)}\nID: {image.id}",
            reply_markup=None   # ✅ ВАЖНО
        )

    await callback.message.answer(
        "⬅️ Вернуться к редактированию товара",
        reply_markup=back_to_edit_keyboard()
    )

    await callback.answer()

# ========== НАВИГАЦИОННЫЕ КНОПКИ ==========

@admin_router.callback_query(F.data == "back_to_edit")
async def back_to_edit_handler(callback: CallbackQuery, state: FSMContext):
    """Возврат к меню редактирования"""
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if product:
            await show_product_for_edit(callback.message, state, product)
            await state.set_state(EditProductStates.waiting_for_edit_choice)
    
    await callback.answer()

@admin_router.callback_query(F.data == "back_to_images")
async def back_to_images_handler(callback: CallbackQuery, state: FSMContext):
    """Возврат к меню управления изображениями"""
    await callback.message.edit_text(
        "🖼️ <b>Управление изображениями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_image_management_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(EditProductStates.waiting_for_image_choice)
    await callback.answer()

@admin_router.callback_query(F.data == "finish_edit")
async def finish_edit_handler(callback: CallbackQuery, state: FSMContext):
    """Завершение редактирования"""
    await state.clear()

    text = "✅ <b>Редактирование завершено!</b>\n\nТовар успешно обновлен."
    
    try:
        if callback.message.text:
            await callback.message.edit_text(text, parse_mode=ParseMode.HTML)
        elif callback.message.caption and (callback.message.photo or callback.message.video or callback.message.document):
            await callback.message.edit_caption(text, parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(text, parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, parse_mode=ParseMode.HTML)

    await callback.message.answer(
        "👑 <b>Панель администратора</b>\n\nВыберите команду:",
        reply_markup=get_admin_keyboard(),
        parse_mode=ParseMode.HTML
    )

    await callback.answer()



@admin_router.callback_query(F.data == "cancel_edit")
async def cancel_edit_handler(callback: CallbackQuery, state: FSMContext):
    """Отмена редактирования"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ <b>Редактирование отменено</b>",
        parse_mode=ParseMode.HTML
    )
    
    await callback.message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Выберите команду:",
        reply_markup=get_admin_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@admin_router.callback_query(F.data == "cancel_operation")
async def cancel_operation_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        "❌ <b>Операция отменена</b>",
        parse_mode=ParseMode.HTML
    )

    await return_to_admin_panel(callback.message)
    await callback.answer()


@admin_router.callback_query(F.data == "cancel")
async def cancel_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Отмена любой операции через кнопку"""
    await state.clear()

    if callback.message.text or callback.message.caption:
        await callback.message.edit_text(
            "❌ <b>Операция отменена</b>",
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.message.answer(
            "❌ <b>Операция отменена</b>",
            parse_mode=ParseMode.HTML
        )

    await callback.message.answer(
        "👑 <b>Панель администратора</b>\n\nВыберите команду:",
        reply_markup=get_admin_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()



@admin_router.callback_query(
    F.data == "back_to_edit",
    EditProductStates.waiting_for_image_choice
)
async def back_to_edit_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "✏️ Редактирование изображений товара:",
        reply_markup=get_image_management_keyboard()
    )
    await callback.answer()

