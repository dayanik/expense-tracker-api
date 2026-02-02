from datetime import datetime
from sqlalchemy import Integer, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates='user', cascade="all, delete-orphan")


class Expense(Base):
    __tablename__ = "expenses"

    expense_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    amount: Mapped[int]
    category_id = mapped_column(
        Integer, 
        ForeignKey("categories.category_id"),
        nullable=False
    )
    user_id = mapped_column(Integer, ForeignKey("users.user_id"))
    user: Mapped["User"] = relationship("User", back_populates="expenses")
    category: Mapped["Category"] = relationship(
        "Category", back_populates="expenses")


class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True
        )
    title: Mapped[str]
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates='category'
    )
