import logging
from pathlib import Path

import pandas as pd

from src.ingestion.read_olist import load_olist_data


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "olist"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": [
        "shipping_limit_date",
    ],
    "reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


NUMERIC_COLUMNS = {
    "order_items": [
        "order_item_id",
        "price",
        "freight_value",
    ],
    "payments": [
        "payment_sequential",
        "payment_installments",
        "payment_value",
    ],
    "reviews": [
        "review_score",
    ],
    "products": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
}


def convert_data_types(datasets):
    """Convert date and numeric columns without changing raw source files."""

    for dataset_name, columns in DATE_COLUMNS.items():
        df = datasets[dataset_name].copy()

        for column in columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
            )

        datasets[dataset_name] = df

    for dataset_name, columns in NUMERIC_COLUMNS.items():
        df = datasets[dataset_name].copy()

        for column in columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        datasets[dataset_name] = df

    return datasets


def add_order_quality_flags(datasets):
    """Flag suspicious order timestamps without changing their values."""

    orders = datasets["orders"].copy()

    purchase = orders["order_purchase_timestamp"]
    approved = orders["order_approved_at"]
    carrier = orders["order_delivered_carrier_date"]
    delivered = orders["order_delivered_customer_date"]

    orders["flag_approval_before_purchase"] = (
        approved.notna()
        & purchase.notna()
        & (approved < purchase)
    )

    orders["flag_carrier_before_purchase"] = (
        carrier.notna()
        & purchase.notna()
        & (carrier < purchase)
    )

    orders["flag_customer_before_carrier"] = (
        delivered.notna()
        & carrier.notna()
        & (delivered < carrier)
    )

    orders["flag_delivered_missing_customer_date"] = (
        orders["order_status"].eq("delivered")
        & delivered.isna()
    )

    datasets["orders"] = orders

    return datasets


def add_translated_product_categories(datasets):
    """Add English category names while preserving original category values."""

    products = datasets["products"].copy()
    translations = datasets["category_translation"].copy()

    products = products.merge(
        translations,
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )

    datasets["products"] = products

    return datasets


def transform_olist_data(datasets):
    """Prepare Olist datasets while preserving all source records."""

    datasets = {
        name: df.copy()
        for name, df in datasets.items()
    }

    datasets = convert_data_types(datasets)
    datasets = add_order_quality_flags(datasets)
    datasets = add_translated_product_categories(datasets)

    return datasets


def save_processed_data(datasets):
    """Save transformed datasets as separate CSV files."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for dataset_name, df in datasets.items():
        output_path = PROCESSED_DIR / f"{dataset_name}.csv"

        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
        )

        logger.info(
            "Saved %s: %s rows, %s columns",
            output_path.name,
            f"{len(df):,}",
            len(df.columns),
        )


def print_quality_flags(datasets):
    """Display the number of flagged order records."""

    orders = datasets["orders"]

    flag_columns = [
        "flag_approval_before_purchase",
        "flag_carrier_before_purchase",
        "flag_customer_before_carrier",
        "flag_delivered_missing_customer_date",
    ]

    print("\n========== ORDER DATE QUALITY FLAGS ==========")

    for column in flag_columns:
        count = int(orders[column].sum())
        print(f"{column:45} {count:>8,}")

    print("===============================================\n")


def main():
    logger.info("Loading original Olist datasets...")
    datasets = load_olist_data()

    logger.info("Transforming Olist datasets...")
    transformed = transform_olist_data(datasets)

    logger.info("Saving processed datasets...")
    save_processed_data(transformed)

    print_quality_flags(transformed)

    print("Olist transformation completed successfully.")
    print(f"Output directory: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
