from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    subcategories: Mapped[list["Subcategory"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
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


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_description: Mapped[str] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    size: Mapped[str] = mapped_column(String, nullable=True)  
    price: Mapped[float] = mapped_column(Float, nullable=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id"), nullable=True)

    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)  
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    product: Mapped["Product"] = relationship(back_populates="images")