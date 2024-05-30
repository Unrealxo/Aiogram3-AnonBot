from sqlalchemy import String, BigInteger, Column
from sqlalchemy.ext.asyncio import (async_sessionmaker,
                                    create_async_engine,
                                    AsyncAttrs)
from sqlalchemy.orm import DeclarativeBase


"""
Подключение к базе данных и создание новых столбцов
"""

ip='IP'
PGUSER='USER'
PGPASSWORD='PASSWORD'
DATABASE='DATABASE'

POSTGRES_URI = f'postgresql+asyncpg://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}'

engine = create_async_engine(POSTGRES_URI, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
	pass


class User(Base):
	__tablename__ = "users"

	user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
	nickname = Column(String(25), nullable=True)
	gender = Column(String(10), nullable=True)
	age = Column(String(5), nullable=True)
	user_interests = Column(String(100), nullable=True)
	spoiler = Column(BigInteger, nullable=True)
	# 1 - премиума нет. 2 - премиум есть.
	is_premium = Column(BigInteger, nullable=True)
	# дата действия премиума
	premium_date = Column(String(25), nullable=True)
	date_nickname = Column(String(20), nullable=True)
	blocked = Column(BigInteger, nullable=True)
	date_blocked = Column(String(20), nullable=True)


class UserCaptcha(Base):
	__tablename__ = "captcha"

	user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
	status1 = Column(BigInteger)
	status2 = Column(BigInteger)
	status3 = Column(BigInteger)
	status4 = Column(BigInteger)
	emodji = Column(String(50), nullable=True)


class UserAlerts(Base):
	__tablename__ = "alerts"

	user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
	ad = Column(BigInteger, nullable=True)
	nasilie = Column(BigInteger, nullable=True)
	sell = Column(BigInteger, nullable=True)
	porn = Column(BigInteger, nullable=True)
	popros = Column(BigInteger, nullable=True)
	osk = Column(BigInteger, nullable=True)
	poshl = Column(BigInteger, nullable=True)


class UserCaptchaConfirm(Base):
	__tablename__ = "captchaConfirm"

	user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)


class Search_Connection(Base):
	__tablename__ = 'search'

	user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
	search_status = Column(BigInteger, nullable=True)
	interests = Column(BigInteger, nullable=True)
	gender = Column(BigInteger, nullable=True)
	pol_search = Column(String(3), nullable=True)


class Connection(Base):
	__tablename__ = 'connection'

	user_id = Column(BigInteger, primary_key=True)
	connect_user_id = Column(BigInteger)
	view_all = Column(BigInteger, nullable=True)


class Photo_user(Base):
	__tablename__ = 'photo_refaction'

	photo = Column(String(150), nullable=True, primary_key=True)
	user_id = Column(BigInteger)
	photo_hash = Column(String(50), nullable=True)
	caption = Column(String(500), nullable=True)
	date_time = Column(String(20), nullable=True)


class Video_user(Base):
	__tablename__ = 'video_refaction'

	video = Column(String(150), nullable=True, primary_key=True)
	user_id = Column(BigInteger)
	video_hash = Column(String(50), nullable=True)
	caption = Column(String(500), nullable=True)
	date_time = Column(String(20), nullable=True)


# Создает все колонки в БД если не созданы.
async def database_main():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)