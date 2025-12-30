from datetime import datetime
import enum
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from sqlalchemy.orm import Mapped, mapped_column, relationship

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    subcategories: Mapped[list["Subcategory"]] = relationship(
        "Subcategory",
        back_populates="category"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category"
    )



class Subcategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    category: Mapped["Category"] = relationship(
        back_populates="subcategories"
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="subcategory",
        cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # Название
    short_description: Mapped[str] = mapped_column(Text, nullable=True)  # Краткое описание
    additional_info: Mapped[str] = mapped_column(Text, nullable=True)  # Доп. информация (опционально)

    subcategory_id: Mapped[int] = mapped_column(
        ForeignKey("subcategories.id"), 
        nullable=True
    )
    subcategory: Mapped["Subcategory"] = relationship(
        back_populates="products"
    )

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category: Mapped["Category"] = relationship(back_populates="products")

    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.id"
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    product: Mapped["Product"] = relationship(back_populates="images")


class OrderStatus(enum.Enum):
    NEW = "new"  # Новый заказ
    IN_PROGRESS = "in_progress"  # В работе
    COMPLETED = "completed"  # Завершенный заказ
    CANCELLED = "cancelled"  # Отмененный

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Информация о товаре (копируем из Product)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_description: Mapped[str] = mapped_column(Text, nullable=True)
    product_info: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Информация о клиенте
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Даты и статус
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.NEW)
    notes: Mapped[str] = mapped_column(Text, nullable=True)  # Примечания менеджера
    
    # Фото товара (можем сохранить file_id или ссылки)
    product_images: Mapped[str] = mapped_column(Text, nullable=True)