import logging
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "olist"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


DATASET_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


DATASET_DTYPES = {
    "customers": {
        "customer_id": "string",
        "customer_unique_id": "string",
        "customer_zip_code_prefix": "string",
    },
    "geolocation": {
        "geolocation_zip_code_prefix": "string",
    },
    "order_items": {
        "order_id": "string",
        "product_id": "string",
        "seller_id": "string",
    },
    "payments": {
        "order_id": "string",
    },
    "reviews": {
        "review_id": "string",
        "order_id": "string",
    },
    "orders": {
        "order_id": "string",
        "customer_id": "string",
    },
    "products": {
        "product_id": "string",
    },
    "sellers": {
        "seller_id": "string",
        "seller_zip_code_prefix": "string",
    },
    "category_translation": {
        "product_category_name": "string",
    },
}


def load_olist_data() -> dict[str, pd.DataFrame]:
    """Load all original Olist CSV datasets without modifying source files."""

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Olist raw data directory not found: {RAW_DATA_DIR}"
        )

    datasets = {}

    for dataset_name, filename in DATASET_FILES.items():
        file_path = RAW_DATA_DIR / filename

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Required Olist file not found: {file_path}"
            )

        logger.info("Reading dataset: %s", filename)

        df = pd.read_csv(
            file_path,
            dtype=DATASET_DTYPES.get(dataset_name),
            low_memory=False,
            encoding="utf-8",
        )

        datasets[dataset_name] = df

        logger.info(
            "Loaded %s: %s rows, %s columns",
            dataset_name,
            f"{len(df):,}",
            len(df.columns),
        )

    logger.info(
        "Successfully loaded all %d Olist datasets.",
        len(datasets),
    )

    return datasets


if __name__ == "__main__":
    data = load_olist_data()

    print("\n========== OLIST DATASETS SUMMARY ==========")

    for name, df in data.items():
        print(f"{name:20} | Rows: {len(df):>10,} | Columns: {len(df.columns):>3}")

    print("\nOrders preview:")
    print(data["orders"].head())

    print("\n============================================")
