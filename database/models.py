import datetime
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, JSON, TIME, DateTime, Interval, TIMESTAMP, Boolean
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    date_start = Column(Date, nullable=False, default=datetime.datetime.utcnow)
    user_id = Column(String(100), unique=True)


class Remind(Base):
    __tablename__ = 'remind'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    text = Column(String(100))

    date_start = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)

    ones_month = Column(Integer, nullable=True)
    ones_years = Column(Integer, nullable=True)

    date_last_notificate = Column(DateTime, nullable=True)
    date_deadline = Column(DateTime, nullable=False)

    date_finish = Column(Date, nullable=True)
    date_is_delete = Column(DateTime, nullable=True)

    interval = Column(Interval, nullable=True)
    is_at_time = Column(Boolean, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))

class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    remind_id = Column(Integer, ForeignKey("remind.id"))
    file_name = Column(String(100))
    file_url = Column(String(100))


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    remind_id = Column(Integer, ForeignKey("remind.id"))
    category_name = Column(String(100))