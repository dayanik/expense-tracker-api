from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import DATABASE_URL
from app import models, utils, schemas, exceptions


# echo=true -- sql logs
engine = create_async_engine(DATABASE_URL, echo=False)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

CATEGORIES = [
    {"category_id": 1, "title": "Продукты"},
    {"category_id": 2, "title": "Транспорт"},
    {"category_id": 3, "title": "Жильё"},
    {"category_id": 4, "title": "Развлечения"},
    {"category_id": 5, "title": "Электроника"},
    {"category_id": 6, "title": "Вещи"},
    {"category_id": 7, "title": "Здоровье"},
    {"category_id": 8, "title": "Кредиты"},
    {"category_id": 9, "title": "Другое"}
]


async def seed_categories(session: AsyncSession) -> None:
    result = await session.execute(
        select(func.count(models.Category.category_id))
    )
    count = result.scalar()

    if count > 0:
        return

    session.add_all(
        models.Category(**cat) for cat in CATEGORIES
    )
    await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    async with async_session_maker() as session:
          await seed_categories(session)
    yield


# декоратор создания сессии
def connection(method):
	async def wrapper(*args, **kwargs):
		async with async_session_maker() as session:
			try:
				return await method(*args, session=session, **kwargs)
			except Exception as e:
				await session.rollback()
				raise e
			finally:
				await session.close()
	return wrapper


@connection
async def create_user(
        data: schemas.UserRegisterRequest, session: AsyncSession
    ) -> models.User | None:
    user = models.User(**data.model_dump())
    user.password = utils.get_password_hash(user.password)
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise exceptions.HTTPEmailNotUniqueException()


@connection
async def get_user(email: str, session: AsyncSession) -> models.User:
    query = select(models.User).where(models.User.email == email)
    user_row = await session.execute(query)
    return user_row.scalar_one_or_none()


@connection
async def create_expense(
        data: schemas.ExpenseRequest, 
        user_id: int,
        session: AsyncSession
    ) -> models.Expense:

    category_query = (
        select(models.Category)
        .where(models.Category.category_id == data.category_id)
    )
    category_result = await session.execute(category_query)
    category = category_result.scalar_one_or_none()
    if category is None:
        raise exceptions.HTTPException(400, "Category_id is not found")

    expense = models.Expense(
        title = data.title,
        description = data.description,
        amount = data.amount,
        category=category
    )
    expense.user_id = user_id 
    session.add(expense)
    await session.commit()
    await session.refresh(expense, ["category"])
    return expense


@connection
async def get_expenses(
        user_id: int,
        page: int,
        limit: int,
        category_id: int | None, 
        date_from: datetime, 
        date_to: datetime,
        session: AsyncSession
    ) -> list[models.Expense]:
    filters = [
        models.Expense.user_id == user_id,
        models.Expense.updated_at >= date_from,
        models.Expense.updated_at <= date_to
    ]
    if category_id:
        filters.append(models.Expense.category_id == category_id)
    query = (
        select(models.Expense)
        .options(joinedload(models.Expense.category))
        .where(*filters)
        .order_by(models.Expense.updated_at)
        .limit(limit)
        .offset((page - 1) * limit)
    )
    result = await session.execute(query)
    expenses = result.scalars().all()
    return expenses


@connection
async def get_expenses_count(
        user_id: int,
        category_id: int | None, 
        date_from: datetime, 
        date_to: datetime,
        session: AsyncSession
    ):
    filters = [
        models.Expense.user_id == user_id,
        models.Expense.updated_at >= date_from,
        models.Expense.updated_at <= date_to
    ]
    if category_id:
        filters.append(models.Expense.category_id == category_id)

    count_query = (
        select(func.count())
        .select_from(models.Expense)
        .where(*filters)
    )
    total_expenses = await session.scalar(count_query)
    return total_expenses


@connection
async def get_expense(
        expense_id: int, 
        session: AsyncSession
    ) -> models.Expense | None:
    query = (
        select(models.Expense)
        .options(joinedload(models.Expense.category))
        .where(models.Expense.expense_id == expense_id)
        )
    result = await session.execute(query)
    return result.scalar_one_or_none()


@connection
async def update_expense(
        expense_id: int, 
        data: schemas.ExpenseRequest,
        session: AsyncSession
    ) -> models.Expense:
    
    query = (
        select(models.Expense)
        .where(models.Expense.expense_id == expense_id)
    )
    result = await session.execute(query)
    expense = result.scalar_one_or_none()

    if not expense:
        raise exceptions.HTTPExpenseNotExistsException()
    
    expense.title = data.title
    expense.description = data.description
    expense.category_id = data.category_id
    expense.amount = data.amount
    await session.commit()
    
    return expense


@connection
async def delete_expense(
        expense_id: int,
        session: AsyncSession
    ):
    query = (
        select(models.Task)
        .where(models.Expense.expense_id == expense_id)
    )
    result = await session.execute(query)
    expense = result.scalar_one_or_none()
    if not expense:
        raise exceptions.HTTPExpenseNotExistsException()
    await session.delete(expense)
    await session.commit()
