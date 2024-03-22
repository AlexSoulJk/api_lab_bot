import os

from dotenv import load_dotenv

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, JSON, TIME

load_dotenv()
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    date_start = Column(Date, nullable=False)
    user_id = Column(String(100))


class Remind(Base):
    __tablename__ = 'remind'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    text = Column(String(100))
    image_url = Column(String(100), nullable=True)

    date_start = Column(Date, nullable=False)
    date_deadline = Column(Date, nullable=True)
    date_finish = Column(Date, nullable=True)
    date_is_delete = Column(Date, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    #TODO: JSON TYPE FOR CATEGORY OR ANOTHER TABLE?
    type = Column(String(100))

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