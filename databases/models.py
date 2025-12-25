from sqlalchemy import Float, ForeignKey, String, Text
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
