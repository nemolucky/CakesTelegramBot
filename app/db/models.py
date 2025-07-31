import os

from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker

from dotenv import load_dotenv

load_dotenv()
engine = create_async_engine(url=os.getenv('URL'), echo=True)
async_session = async_sessionmaker(engine)


class Base(DeclarativeBase, AsyncAttrs):
    repr_cols_num = 6
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    username = Column(String(100))
    name = Column(String(255))
    phone = Column(String(255))


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(1024))
    price = Column(String(30))
    category = Column(ForeignKey('categories.id'))


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    url = Column(String(1024))
    item = Column(ForeignKey('items.id'))


class Bin(Base):
    __tablename__ = 'bins'

    id = Column(Integer, primary_key=True)
    user = Column(ForeignKey('users.id'))
    item = Column(ForeignKey('items.id'))


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
