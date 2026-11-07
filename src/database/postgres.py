import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "remote_jobs_db"),
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))

        print("PostgreSQL connection successful!")
        print(result.scalar())


if __name__ == "__main__":
    test_connection()