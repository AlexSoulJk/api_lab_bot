import os

from dotenv import load_dotenv

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date

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

    text = Column(String(100))
    file_url = Column(String(100))
    image_url = Column(String(100))

    date_start = Column(Date, nullable=False)
    date_deadline = Column(Date, nullable=True)
    date_finish = Column(Date, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    #TODO: JSON TYPE FOR CATEGORY OR ANOTHER TABLE?
    category = Column(String(100))
