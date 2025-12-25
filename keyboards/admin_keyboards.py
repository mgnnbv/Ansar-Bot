from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="➕ Добавить товар", callback_data="admin_add_product")
    builder.button(text="✏️ Редактировать товар", callback_data="admin_edit_product")  # Добавлено
    builder.button(text="🗑️ Удалить товар", callback_data="admin_delete_product")
    
    builder.adjust(2, 2)  # Размещаем по 2 кнопки в ряду
    return builder.as_markup()



def get_edit_product_keyboard():
    """Клавиатура для выбора поля редактирования"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Название", callback_data="edit_name")
    builder.button(text="📝 Краткое описание", callback_data="edit_short_desc")
    builder.button(text="ℹ️ Доп. информация", callback_data="edit_add_info")
    builder.button(text="📁 Категория", callback_data="edit_category")
    builder.button(text="🖼️ Изображения", callback_data="edit_images")
    builder.button(text="👁️ Просмотреть товар", callback_data="view_product")
    builder.button(text="✅ Завершить", callback_data="finish_edit")
    builder.button(text="❌ Отменить", callback_data="cancel_edit")
    
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()

def get_image_management_keyboard():
    """Клавиатура управления изображениями"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="➕ Добавить изображение", callback_data="add_image")
    builder.button(text="🗑️ Удалить изображение", callback_data="delete_image")
    builder.button(text="👁️ Просмотреть изображения", callback_data="view_images")
    builder.button(text="↩️ Назад к редактированию", callback_data="back_to_edit")
    
    builder.adjust(2)
    return builder.as_markup()

def get_cancel_edit_keyboard():
    """Клавиатура отмены редактирования"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить", callback_data="cancel_edit")
    return builder.as_markup()

def get_cancel_keyboard():
    """Клавиатура только с кнопкой отмены"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Отменить операцию",
        callback_data="cancel"  
    )
    return builder.as_markup()


