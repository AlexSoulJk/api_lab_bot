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