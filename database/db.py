
import logging
import os


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

        try:
            self.engine = create_engine(self.url)
            self.session_maker = sessionmaker(bind=self.engine)
            self.sql_query(query=select(1))
            logging.info("Database connected")
        except Exception as e:
            logging.error(e)
            logging.error("Database didn't connect")

    def sql_query(self, query, is_single=True, is_update=False):
        with self.session_maker(expire_on_commit=True) as session:
            response = session.execute(query)
            if not is_update:
                return response.scalars().first() if is_single else response.all()
            session.commit()

    def create_object(self, model):
        with self.session_maker(expire_on_commit=True) as session:
            session.add(model)
            session.commit()

    def formed_post(self, id_place):
        res = {}
        res["place_name"] = self.sql_query(query=select(models.Place).where(models.Place.id == id_place))
        res["name_of_writer"] = self.sql_query(query=select(models.User.name).where(
            models.User.id == res["place_name"].id_writer))
        result = self.sql_query(query=select(models.Category.name_of_category).select_from(
                join(
                    models.Place_Category,
                    models.Category,
                    models.Place_Category.id_category == models.Category.id
                )
            ).where(
            models.Place_Category.id_place == id_place), is_single=False)
        tags = ""
        for item in result:
            tags += f"#{item[0].replace(' ', '')} "
        res["tags"] = tags
        res["description"] = self.sql_query(query=select(models.Description.text).where(
            models.Description.id_places == id_place))
        res["photo"] = self.sql_query(query=select(models.Place_photo.photo_path).where(
            models.Place_photo.id_place == id_place))
        res["website"] = self.sql_query(query=select(models.Place_Info.website_path).where(
            models.Place_Info.id_place == id_place))
        return res

load_dotenv()
logging.basicConfig(level=logging.INFO)
db = Database(os.getenv("db_url"))
db.connect()


# remove_user('Ivan')
#db.create_object(model=models.User(name="ams"))
# print([user.name for user in sql_query(query=select(models.User), is_single=False)])
# sql_query(query=update(models.User).where(models.User.name == "ilsaf").values(name="fedya"), is_update=True)
