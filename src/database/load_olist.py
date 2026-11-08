
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.postgres import olist_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "olist"

CHUNK_SIZE = 20_000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# Load parent tables before tables that reference them.
LOAD_ORDER = [
    ("customers", "customers.csv"),
    ("geolocation", "geolocation.csv"),
    ("sellers", "sellers.csv"),
    ("category_translation", "category_translation.csv"),
    ("products", "products.csv"),
    ("orders", "orders.csv"),
    ("order_items", "order_items.csv"),
    ("payments", "payments.csv"),
    ("reviews", "reviews.csv"),
]


TABLE_COLUMNS = {
    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
    "geolocation": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ],
    "sellers": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
    "category_translation": [
        "product_category_name",
        "product_category_name_english",
    ],
    "products": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "flag_approval_before_purchase",
        "flag_carrier_before_purchase",
        "flag_customer_before_carrier",
        "flag_delivered_missing_customer_date",
    ],
    "order_items": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
    "payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],
    "reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


NULLABLE_INTEGER_COLUMNS = {
    "products": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
    ],
}


def prepare_chunk(table_name, chunk):
    """Prepare CSV values for PostgreSQL."""

    columns = TABLE_COLUMNS[table_name]
    chunk = chunk[columns].copy()

    for column in DATE_COLUMNS.get(table_name, []):
        chunk[column] = pd.to_datetime(
            chunk[column],
            errors="coerce",
        )

    for column in NULLABLE_INTEGER_COLUMNS.get(table_name, []):
        chunk[column] = chunk[column].map(
            lambda value: None if pd.isna(value) else int(value)
        )

    return chunk


def get_table_count(connection, table_name):
    result = connection.execute(
        text(f'SELECT COUNT(*) FROM "{table_name}"')
    )
    return result.scalar_one()


def load_table(connection, table_name, filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Missing processed file: {file_path}")

    logger.info("Loading table: %s", table_name)

    total_loaded = 0

    for chunk in pd.read_csv(
        file_path,
        chunksize=CHUNK_SIZE,
        encoding="utf-8-sig",
        low_memory=False,
    ):
        chunk = prepare_chunk(table_name, chunk)

        chunk.to_sql(
            name=table_name,
            con=connection,
            if_exists="append",
            index=False,
            chunksize=5_000,
        )

        total_loaded += len(chunk)

        logger.info(
            "%s: loaded %s rows",
            table_name,
            f"{total_loaded:,}",
        )

    logger.info(
        "Finished %s: %s rows",
        table_name,
        f"{total_loaded:,}",
    )

    return total_loaded


def main():
    logger.info("Starting Olist database loading...")

    expected_counts = {}

    # One transaction for all tables.
    # If any table fails, all inserts are rolled back.
    with olist_engine.begin() as connection:

        # Prevent accidental duplicate loading.
        existing_counts = {
            table_name: get_table_count(connection, table_name)
            for table_name, _ in LOAD_ORDER
        }

        non_empty_tables = {
            name: count
            for name, count in existing_counts.items()
            if count > 0
        }

        if non_empty_tables:
            raise RuntimeError(
                "Database is not empty. Loading cancelled to prevent "
                f"duplicate records: {non_empty_tables}"
            )

        for table_name, filename in LOAD_ORDER:
            expected_counts[table_name] = load_table(
                connection,
                table_name,
                filename,
            )

        logger.info("Verifying database row counts...")

        for table_name, expected in expected_counts.items():
            actual = get_table_count(connection, table_name)

            logger.info(
                "%s | expected: %s | actual: %s",
                table_name,
                f"{expected:,}",
                f"{actual:,}",
            )

            if actual != expected:
                raise RuntimeError(
                    f"Row count mismatch in {table_name}: "
                    f"expected {expected}, got {actual}"
                )

    logger.info("All Olist datasets loaded and verified successfully.")


if __name__ == "__main__":
    main()
