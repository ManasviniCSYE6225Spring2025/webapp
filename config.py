import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"mysql+pymysql://{username}:{password}@{host}/{db_name}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
