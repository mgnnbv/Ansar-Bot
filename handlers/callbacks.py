from typing import Literal
from aiogram.filters.callback_data import CallbackData



class CategoryCallback(CallbackData, prefix="category"):
    category_id: int


class SubcategoryCallback(CallbackData, prefix="subcat"):
    subcategory_id: int


class ProductCallback(CallbackData, prefix="product"):
    product_id: int


class ProductDetailCallback(CallbackData, prefix='product_details'):
    product_detail_id: int


class BackCallback(CallbackData, prefix="back"):
    to: Literal["categories", "subcategories", "products", "product_details"]
    parent_id: int | None = None
