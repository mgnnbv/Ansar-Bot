from aiogram.fsm.state import State, StatesGroup

from aiogram.fsm.state import StatesGroup, State

class QuestionStates(StatesGroup):
    waiting = State()

from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    name = State()
    category = State()
    subcategory = State()
    short_description = State()
    additional_info = State()
    images = State()


class AddProductStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_subcategory = State()
    waiting_for_photos = State()
    waiting_for_short_description = State()
    waiting_for_additional_info = State()  
    waiting_for_final_confirm = State()


class EditProductStates(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_product_choice = State()
    waiting_for_edit_choice = State()
    waiting_for_name_edit = State()
    waiting_for_short_desc_edit = State()
    waiting_for_additional_info_edit = State()
    waiting_for_category_edit = State()
    waiting_for_subcategory_edit = State()
    waiting_for_image_choice = State()
    waiting_for_image_upload = State()
    waiting_for_image_delete = State()
    waiting_for_final_save = State()


