from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, ContentType, InputMediaPhoto
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from datetime import datetime
from sqlalchemy.orm import selectinload


from databases.crud import get_categories, get_subcategories, show_product_list_by_name
from databases.engine import AsyncSessionLocal
from databases.models import Category, Product, ProductImage, Subcategory
from fsm import AddProductStates, EditProductStates
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.admin_keyboards import get_admin_keyboard, get_cancel_edit_keyboard, get_cancel_keyboard, get_edit_product_keyboard, get_image_management_keyboard

admin_router = Router()


@admin_router.message(CommandStart())
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


@admin_router.callback_query(F.data == "admin_add_product")
async def admin_add_product_handler(callback: CallbackQuery, state: FSMContext):
    """Обработка добавления товара через кнопку"""
    await state.clear()
    await callback.message.edit_text(
        "📦 <b>Добавление нового товара</b>\n\n"
        "Введите <b>название товара</b> или нажмите кнопку для отмены:",
        reply_markup=get_cancel_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AddProductStates.waiting_for_name)
    await callback.answer()

@admin_router.message(AddProductStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка названия товара"""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer(
            "❌ Название слишком короткое (минимум 2 символа). Введите еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(name=name)
    
    async with AsyncSessionLocal() as session:
        categories = await get_categories(session)
        
        builder = InlineKeyboardBuilder()
        for category in categories:
            builder.button(
                text=category.name, 
                callback_data=f"cat_{category.id}"
            )
        
        builder.button(
            text="❌ Отменить",
            callback_data="cancel_operation"
        )
        
        builder.adjust(2)

        await message.answer(
            f"✅ <b>Название:</b> {name}\n\n"
            "Выберите <b>категорию</b>:",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AddProductStates.waiting_for_category)

@admin_router.callback_query(F.data.startswith("cat_"), AddProductStates.waiting_for_category)
async def process_category(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category_id_str = callback.data.replace("cat_", "")
    try:
        category_id = int(category_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID категории")
        return
    
    async with AsyncSessionLocal() as session:
        subcategories = await get_subcategories(session, category_id)
        await state.update_data(category_id=category_id)
        
        builder = InlineKeyboardBuilder()
        
        if subcategories:
            for subcategory in subcategories:
                builder.button(
                    text=subcategory.name,
                    callback_data=f"sub_{subcategory.id}"
                )
            builder.button(
                text="⏭️ Пропустить подкатегорию",
                callback_data="skip_subcategory"
            )
        else:
            builder.button(
                text="⏭️ Нет подкатегорий",
                callback_data="skip_subcategory"
            )
        
        builder.button(
            text="❌ Отменить",
            callback_data="cancel_operation"
        )
        
        builder.adjust(2)
        
        result = await session.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        category_name = category.name if category else f"Категория #{category_id}"
        
        data = await state.get_data()
        product_name = data.get('name', 'Не указано')
        
        await callback.message.edit_text(
            f"✅ <b>Название:</b> {product_name}\n"
            f"✅ <b>Категория:</b> {category_name}\n\n"
            "Выберите <b>подкатегорию</b> или пропустите:",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AddProductStates.waiting_for_subcategory)
    await callback.answer()

@admin_router.callback_query(F.data.startswith("sub_"), AddProductStates.waiting_for_subcategory)
async def process_subcategory(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора подкатегории"""
    subcategory_id_str = callback.data.replace("sub_", "")
    try:
        subcategory_id = int(subcategory_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID подкатегории")
        return
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Subcategory).where(Subcategory.id == subcategory_id))
        subcategory = result.scalar_one_or_none()
        subcategory_name = subcategory.name if subcategory else f"Подкатегория #{subcategory_id}"
        
        await state.update_data(subcategory_id=subcategory_id)
        
        data = await state.get_data()
        name = data.get('name', 'Не указано')
        
        category_name = "Не указано"
        if 'category_id' in data:
            result = await session.execute(select(Category).where(Category.id == data['category_id']))
            category = result.scalar_one_or_none()
            if category:
                category_name = category.name
        
        await callback.message.edit_text(
            f"✅ <b>Название:</b> {name}\n"
            f"✅ <b>Категория:</b> {category_name}\n"
            f"✅ <b>Подкатегория:</b> {subcategory_name}\n\n"
            "Напишите <b>краткое описание</b> товара (минимум 10 символов):",
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AddProductStates.waiting_for_short_description)
    await callback.answer()

@admin_router.callback_query(F.data == "skip_subcategory", AddProductStates.waiting_for_subcategory)
async def skip_subcategory(callback: CallbackQuery, state: FSMContext):
    """Пропуск подкатегории"""
    await state.update_data(subcategory_id=None)
    
    data = await state.get_data()
    name = data.get('name', 'Не указано')
    
    async with AsyncSessionLocal() as session:
        category_name = "Не указано"
        if 'category_id' in data:
            result = await session.execute(select(Category).where(Category.id == data['category_id']))
            category = result.scalar_one_or_none()
            if category:
                category_name = category.name
    
    await callback.message.edit_text(
        f"✅ <b>Название:</b> {name}\n"
        f"✅ <b>Категория:</b> {category_name}\n"
        f"✅ <b>Подкатегория:</b> Не выбрана\n\n"
        "Напишите <b>краткое описание</b> товара (минимум 10 символов):",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AddProductStates.waiting_for_short_description)
    await callback.answer()

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
        "3. Минимум 1 фото, максимум 10\n"
        "4. Когда все фото загружены, нажмите кнопку <b>'Готово'</b>\n\n"
        "Или /cancel для отмены.",
        reply_markup=get_cancel_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AddProductStates.waiting_for_photos)

@admin_router.message(AddProductStates.waiting_for_photos, F.content_type == ContentType.PHOTO)
async def process_photo(message: Message, state: FSMContext, bot: Bot):
    """Обработка загрузки фото"""
    photo = message.photo[-1]
    file_id = photo.file_id
    
    file = await bot.get_file(file_id)
    
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) >= 10:
        await message.answer(
            "❌ Максимум 10 фото.\n"
            "Нажмите кнопку <b>'Готово'</b> для продолжения.",
            reply_markup=get_cancel_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return
    
    photo_data = {
        "file_id": file_id,
        "file_path": file.file_path,
        "file_unique_id": photo.file_unique_id,
        "width": photo.width,
        "height": photo.height,
        "date": message.date.isoformat()
    }
    
    photos.append(photo_data)
    await state.update_data(photos=photos)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Готово", callback_data="photos_done")
    builder.button(text="❌ Отменить", callback_data="cancel_operation")
    builder.adjust(1)
    
    await message.answer(
        f"✅ Фото #{len(photos)} добавлено\n"
        f"📷 Всего фото: {len(photos)} из 10\n\n"
        "Отправьте еще фото или нажмите <b>'Готово'</b> для продолжения.",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

@admin_router.callback_query(F.data == "photos_done", AddProductStates.waiting_for_photos)
async def photos_done_handler(callback: CallbackQuery, state: FSMContext):
    """Завершение загрузки фото через кнопку"""
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await callback.message.edit_text(
            "❌ Вы не отправили ни одной фотографии.\n"
            "Отправьте хотя бы одно фото или /cancel для отмены.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    name = data.get('name', 'Не указано')
    short_description = data.get('short_description', 'Не указано')
    additional_info = data.get('additional_info', 'Не указано')
    
    summary_text = (
        "📋 <b>Сводка по товару:</b>\n\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Краткое описание:</b> {short_description}\n"
        f"<b>Доп. информация:</b> {additional_info if additional_info else 'Не указана'}\n"
        f"<b>Количество фото:</b> {len(photos)} шт.\n\n"
        "<i>Подтвердите сохранение товара:</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Сохранить товар", callback_data="confirm_save")
    builder.button(text="❌ Отменить", callback_data="cancel_operation")
    builder.adjust(1)
    
    if photos:
        first_photo = photos[0]
        await callback.message.delete()  
        
        await callback.message.answer_photo(
            photo=first_photo.get("file_id"),
            caption=summary_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    
    await state.set_state(AddProductStates.waiting_for_final_confirm)
    await callback.answer()

@admin_router.callback_query(F.data == "confirm_save", AddProductStates.waiting_for_final_confirm)
async def save_product(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Сохранение товара в БД"""
    data = await state.get_data()
    
    async with AsyncSessionLocal() as session:
        try:
            # Создаем товар
            product = Product(
                name=data['name'],
                short_description=data.get('short_description'),
                additional_info=data.get('additional_info', ''),
                category_id=data.get('category_id'),
                subcategory_id=data.get('subcategory_id')
            )
            
            session.add(product)
            await session.flush()
            
            # Сохраняем фото
            photos_data = data.get("photos", [])
            
            for index, photo_info in enumerate(photos_data):
                file_id = photo_info.get("file_id", "")
                file_path = photo_info.get("file_path", "")
                
                # Используем поле url вместо telegram_file_id
                # file_id - это уникальный идентификатор файла в Telegram
                # Можно использовать его как URL или сохранить отдельно
                product_image = ProductImage(
                    url=file_id,  # Сохраняем file_id в поле url
                    product_id=product.id
                    # Убрали лишние поля: telegram_file_id, telegram_file_path, cdn_url, is_main, order_index
                )
                session.add(product_image)
            
            await session.commit()
            
            # Получаем названия категории и подкатегории
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
            
            await callback.message.edit_caption(
                caption=success_message,
                reply_markup=None,
                parse_mode="HTML"
            )
            
            # Возвращаем в админ-панель
            await callback.message.answer(
                "👑 <b>Панель администратора</b>\n\n"
                "Выберите команду:",
                reply_markup=get_admin_keyboard(),
                parse_mode="HTML"
            )
            
        except Exception as e:
            await session.rollback()
            await callback.message.edit_caption(
                caption=f"❌ Ошибка при сохранении: {str(e)}",
                reply_markup=None
            )
        finally:
            await state.clear()
    
    await callback.answer()

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
        # Ищем товары по частичному совпадению названия
        result = await session.execute(
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.category),
                selectinload(Product.subcategory)
            )
            .where(Product.name.ilike(f"%{search_name}%"))
            .order_by(Product.name)
            .limit(15)  # Ограничиваем для удобства
        )
        
        products = result.scalars().all()
        
        if not products:
            # Показываем список всех товаров, если поиск не дал результатов
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
            # Если нашли один товар - сразу переходим к редактированию
            product = products[0]
            await show_product_for_edit(message, state, product)
        else:
            # Если несколько товаров - показываем список для выбора
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
        # Загружаем связи
        product = await session.get(
            Product, 
            product.id,
            options=[
                selectinload(Product.images),
                selectinload(Product.category),
                selectinload(Product.subcategory)
            ]
        )
        
        # Сохраняем ID товара в состоянии
        await state.update_data(product_id=product.id)
        
        # Формируем информацию о товаре
        category_name = product.category.name if product.category else "❌ Не указана"
        subcategory_name = product.subcategory.name if product.subcategory else "❌ Не указана"
        
        # Обрезаем длинные тексты для отображения
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
        
        # Клавиатура для выбора действия
        builder = InlineKeyboardBuilder()
        
        builder.button(text="✏️ Название", callback_data="edit_name")
        builder.button(text="📝 Описание", callback_data="edit_short_desc")
        builder.button(text="ℹ️ Доп. инфо", callback_data="edit_add_info")
        builder.button(text="📁 Категория", callback_data="edit_category")
        builder.button(text="🖼️ Изображения", callback_data="edit_images")
        builder.button(text="✅ Сохранить", callback_data="finish_edit")
        builder.button(text="❌ Отменить", callback_data="cancel_edit")
        
        builder.adjust(2, 2, 2, 1, 1)
        
        # Если есть фото - показываем первое
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
                # Если не удалось показать фото
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
        await callback.answer("❌ Ошибка: товар не найден в сессии")
        return
    
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        
        if not product:
            await callback.message.edit_text(
                "❌ Товар не найден в базе данных",
                reply_markup=get_cancel_edit_keyboard()
            )
            return
        
        if action == "edit_name":
            await callback.message.edit_text(
                f"✏️ <b>Редактирование названия</b>\n\n"
                f"Текущее название: <b>{product.name}</b>\n\n"
                "Введите новое название:",
                reply_markup=get_cancel_edit_keyboard(),
                parse_mode=ParseMode.HTML
            )
            await state.set_state(EditProductStates.waiting_for_name_edit)
            
        elif action == "edit_short_desc":
            current_desc = product.short_description or "Не указано"
            await callback.message.edit_text(
                f"📝 <b>Редактирование описания</b>\n\n"
                f"Текущее описание: {current_desc}\n\n"
                "Введите новое краткое описание:",
                reply_markup=get_cancel_edit_keyboard(),
                parse_mode=ParseMode.HTML
            )
            await state.set_state(EditProductStates.waiting_for_short_desc_edit)
            
        elif action == "edit_add_info":
            current_info = product.additional_info or "Не указана"
            await callback.message.edit_text(
                f"ℹ️ <b>Редактирование дополнительной информации</b>\n\n"
                f"Текущая информация: {current_info}\n\n"
                "Введите новую дополнительную информацию:\n"
                "(или напишите 'нет', чтобы очистить)",
                reply_markup=get_cancel_edit_keyboard(),
                parse_mode=ParseMode.HTML
            )
            await state.set_state(EditProductStates.waiting_for_additional_info_edit)
            
        elif action == "edit_category":
            # Показываем список категорий
            categories = await get_categories(session)
            
            builder = InlineKeyboardBuilder()
            for category in categories:
                builder.button(
                    text=category.name,
                    callback_data=f"edit_cat_{category.id}"
                )
            builder.button(text="↩️ Назад", callback_data="back_to_edit")
            builder.adjust(2)
            
            await callback.message.edit_text(
                "📁 <b>Выбор категории</b>\n\n"
                "Выберите новую категорию:",
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
            await state.set_state(EditProductStates.waiting_for_category_edit)
            
        elif action == "edit_images":
            await callback.message.edit_text(
                "🖼️ <b>Управление изображениями</b>\n\n"
                "Выберите действие:",
                reply_markup=get_image_management_keyboard(),
                parse_mode=ParseMode.HTML
            )
            await state.set_state(EditProductStates.waiting_for_image_choice)
            
        elif action == "view_product":
            await show_product_for_edit(callback.message, state, product)
    
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
            
        # Показываем меню редактирования снова
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
        # Получаем подкатегории для выбранной категории
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
        
        # Сохраняем временные данные
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
            product.subcategory_id = None  # Очищаем подкатегорию
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

# ========== УПРАВЛЕНИЕ ИЗОБРАЖЕНИЯМИ ==========
@admin_router.callback_query(F.data == "add_image", EditProductStates.waiting_for_image_choice)
async def add_image_handler(callback: CallbackQuery, state: FSMContext):
    """Добавление нового изображения"""
    await callback.message.edit_text(
        "➕ <b>Добавление изображения</b>\n\n"
        "Отправьте фото товара (как файл или фото) или введите URL изображения:",
        reply_markup=get_cancel_edit_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(EditProductStates.waiting_for_image_url)

@admin_router.message(EditProductStates.waiting_for_image_url, F.content_type == ContentType.PHOTO)
async def process_image_photo(message: Message, state: FSMContext, bot: Bot):
    """Обработка фото для добавления"""
    photo = message.photo[-1]
    file_id = photo.file_id
    
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        # Создаем запись в product_images
        product_image = ProductImage(
            url=file_id,
            product_id=product_id
        )
        session.add(product_image)
        await session.commit()
        
        await message.answer(
            "✅ Изображение добавлено!",
            reply_markup=get_image_management_keyboard()
        )
        
        await state.set_state(EditProductStates.waiting_for_image_choice)

@admin_router.message(EditProductStates.waiting_for_image_url, F.content_type == ContentType.TEXT)
async def process_image_url(message: Message, state: FSMContext):
    """Обработка URL изображения"""
    url = message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        await message.answer(
            "❌ Неверный URL. Должен начинаться с http:// или https://\n"
            "Попробуйте еще раз:",
            reply_markup=get_cancel_edit_keyboard()
        )
        return
    
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        product_image = ProductImage(
            url=url,
            product_id=product_id
        )
        session.add(product_image)
        await session.commit()
        
        await message.answer(
            "✅ Изображение добавлено по URL!",
            reply_markup=get_image_management_keyboard()
        )
        
        await state.set_state(EditProductStates.waiting_for_image_choice)

@admin_router.callback_query(F.data == "delete_image", EditProductStates.waiting_for_image_choice)
async def delete_image_handler(callback: CallbackQuery, state: FSMContext):
    """Удаление изображения"""
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ProductImage).where(ProductImage.product_id == product_id)
        )
        images = result.scalars().all()
        
        if not images:
            await callback.message.edit_text(
                "❌ У товара нет изображений для удаления",
                reply_markup=get_image_management_keyboard()
            )
            return
        
        builder = InlineKeyboardBuilder()
        
        for img in images:
            builder.button(
                text=f"🗑️ Изображение {img.id}",
                callback_data=f"delete_img_{img.id}"
            )
        
        builder.button(text="↩️ Назад", callback_data="back_to_images")
        builder.adjust(1)
        
        await callback.message.edit_text(
            f"🗑️ <b>Удаление изображения</b>\n\n"
            f"Всего изображений: {len(images)}\n"
            "Выберите изображение для удаления:",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        
        await state.set_state(EditProductStates.waiting_for_image_to_delete)

@admin_router.callback_query(F.data.startswith("delete_img_"), EditProductStates.waiting_for_image_to_delete)
async def process_image_delete(callback: CallbackQuery, state: FSMContext):
    """Обработка удаления изображения"""
    image_id_str = callback.data.replace("delete_img_", "")
    
    try:
        image_id = int(image_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID изображения")
        return
    
    async with AsyncSessionLocal() as session:
        # Удаляем изображение
        await session.execute(
            delete(ProductImage).where(ProductImage.id == image_id)
        )
        await session.commit()
        
        await callback.message.edit_text(
            f"✅ Изображение #{image_id} удалено!",
            reply_markup=get_image_management_keyboard()
        )
        
        await state.set_state(EditProductStates.waiting_for_image_choice)
    
    await callback.answer()

@admin_router.callback_query(F.data == "view_images", EditProductStates.waiting_for_image_choice)
async def view_images_handler(callback: CallbackQuery, state: FSMContext):
    """Просмотр всех изображений товара"""
    data = await state.get_data()
    product_id = data.get('product_id')
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ProductImage).where(ProductImage.product_id == product_id)
        )
        images = result.scalars().all()
        
        if not images:
            await callback.message.edit_text(
                "📷 У товара нет изображений",
                reply_markup=get_image_management_keyboard()
            )
            return
        
        if len(images) == 1:
            # Если одно изображение
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=images[0].url,
                    caption=f"📷 Изображение 1 из {len(images)}\nID: {images[0].id}"
                ),
                reply_markup=get_image_management_keyboard()
            )
        else:
            # Если несколько изображений - создаем медиагруппу
            media = []
            for i, img in enumerate(images, 1):
                media.append(InputMediaPhoto(
                    media=img.url,
                    caption=f"📷 Изображение {i} из {len(images)}\nID: {img.id}" if i == 1 else ""
                ))
            
            await callback.message.delete()
            await callback.message.answer_media_group(media)
            
            await callback.message.answer(
                f"📷 Всего изображений: {len(images)}",
                reply_markup=get_image_management_keyboard()
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
    
    await callback.message.edit_text(
        "✅ <b>Редактирование завершено!</b>\n\n"
        "Товар успешно обновлен.",
        parse_mode=ParseMode.HTML
    )
    
    # Возвращаем в админ-панель
    await callback.message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Выберите команду:",
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
    """Отмена операции"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Операция отменена.\n\n"
        "Возвращаю в админ-панель..."
    )
    await callback.message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Выберите команду:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Команда отмены"""
    await state.clear()
    await message.answer(
        "❌ Операция отменена.\n\n"
        "Возвращаю в админ-панель...",
        reply_markup=get_admin_keyboard()
    )
