import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()


def build_engine(database_name):
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=database_name,
    )
    return create_engine(database_url, pool_pre_ping=True)


olist_engine = build_engine(
    os.getenv("OLIST_DB_NAME", "olist_ecommerce_db")
)


def test_olist_connection():
    with olist_engine.connect() as connection:
        result = connection.execute(text("SELECT current_database()"))
        database_name = result.scalar_one()
        print("Olist database connection successful!")
        print(f"Connected database: {database_name}")


if __name__ == "__main__":
    test_olist_connection()
