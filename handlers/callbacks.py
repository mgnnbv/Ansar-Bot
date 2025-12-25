from typing import Literal, Optional
from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="category"):
    category_id: int


class SubcategoryCallback(CallbackData, prefix="subcat"):
    subcategory_id: int


class ProductCallback(CallbackData, prefix="product"):
    product_id: int


class ProductDetailCallback(CallbackData, prefix='product_detail'):
    product_detail_id: int
    action: Literal["view", "add_to_cart", "ask_question"] = "view"


class AskCallback(CallbackData, prefix="ask"):
    pass


class BackCallback(CallbackData, prefix="back"):
    to: Literal["categories", "subcategories", "products", "product_detail"]
    parent_id: Optional[int] = None


