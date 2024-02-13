from typing import Generic, Type, TypeVar

from sqlalchemy import func, text
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Column, SQLModel, select
from sqlmodel.sql.expression import Select

from icon_stats.db import get_session

T = TypeVar("T", bound="BaseSQLModel")


class BaseSQLModel(SQLModel):
    @classmethod
    async def get(
        cls: Type[T],
        condition: BinaryExpression | list[BinaryExpression] | None = None,
        *args,
        **kwargs,
    ) -> T | None:
        async with get_session(db_name="stats") as session:
            query = select(cls)
            if condition is not None:
                if isinstance(condition, BinaryExpression):
                    condition = [condition]
                for c in condition:
                    query = query.where(c)
            result = await session.execute(query.filter(*args).filter_by(**kwargs))
            return result.scalars().first()

    @classmethod
    async def get_all(
        cls: Type[T],
        condition: BinaryExpression | list[BinaryExpression] | None = None,
        *args,
        **kwargs,
    ) -> list[T] | None:
        async with get_session(db_name="stats") as session:
            query = select(cls)
            if condition is not None:
                if isinstance(condition, BinaryExpression):
                    condition = [condition]
                for c in condition:
                    query = query.where(c)
            result = await session.execute(query.filter(*args).filter_by(**kwargs))
            return result.scalars().all()

    @classmethod
    async def count(
        cls: Type[T],
        condition: BinaryExpression | list[BinaryExpression] | None = None,
        *args,
    ) -> list[T] | None:
        async with get_session(db_name="stats") as session:
            query = func.count(getattr(cls, next(iter(cls.model_fields.keys()))))
            if condition is not None:
                if isinstance(condition, BinaryExpression):
                    condition = [condition]
                for c in condition:
                    query = query.where(c)
            result = await session.execute(query.filter(*args))
            return result.one()[0]

    @classmethod
    async def sum(
        cls: Type[T],
        value: InstrumentedAttribute,
        *args,
        group_by: InstrumentedAttribute = None,
    ) -> list[T] | None:
        async with get_session(db_name="stats") as session:
            query = select(func.sum(value).label("foo")).select_from(cls)
            if group_by is not None:
                query = query.group_by(text(group_by))
            result = await session.execute(query.filter(*args))
            return result.scalars().all()[0]

    async def upsert(self):
        async with get_session(db_name="stats") as session:
            session.add(self)
            await session.commit()

    @classmethod
    def select(cls, *args) -> Select:
        if args:
            return select(*args)
        return select(cls)
