import logging
from dotenv import load_dotenv
import os
import subprocess

from dotenv import load_dotenv

from sqlalchemy import create_engine, select, update, delete, Engine, literal_column, join


from sqlalchemy.orm import sessionmaker

from database import models


class Database:
    def __init__(self, db_url):
        self.session_maker = None
        self.url = db_url
        self.engine = None

    def connect(self):
        def run_migrations():
            # Функция для запуска Alembic миграций
            try:
                subprocess.run(["alembic", "upgrade", "head"], check=True)
                logging.info("Migrations applied successfully")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to apply migrations: {e}")

        try:
            self.engine = create_engine(self.url)
            self.session_maker = sessionmaker(bind=self.engine)
            self.sql_query(query=select(1))
            logging.info("Database connected")
            run_migrations()  # Вызов метода для запуска миграций
        except Exception as e:
            logging.error(e)
            logging.error("Database didn't connect")

    def sql_query(self, query, is_single=True, is_update=False):
        with self.session_maker(expire_on_commit=True) as session:
            response = session.execute(query)
            if not is_update:
                return response.scalars().first() if is_single else response.all()
            session.commit()

    def create_object(self, model, ):
        with self.session_maker(expire_on_commit=True) as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model.id




    def create_objects(self, model_s: []):
        with self.session_maker(expire_on_commit=True) as session:
            session.add_all(model_s)
            session.commit()

load_dotenv()
logging.basicConfig(level=logging.INFO)
db = Database(os.getenv("db_url"))
db.connect()


# remove_user('Ivan')
#db.create_object(model=models.User(name="ams"))
# print([user.name for user in sql_query(query=select(models.User), is_single=False)])
# sql_query(query=update(models.User).where(models.User.name == "ilsaf").values(name="fedya"), is_update=True)
