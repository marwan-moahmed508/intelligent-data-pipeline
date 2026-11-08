from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "olist"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "olist"


@pytest.fixture(scope="module")
def raw():
    return {
        "customers": pd.read_csv(RAW_DIR / "olist_customers_dataset.csv"),
        "orders": pd.read_csv(RAW_DIR / "olist_orders_dataset.csv"),
        "items": pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv"),
        "payments": pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv"),
        "reviews": pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv"),
        "products": pd.read_csv(RAW_DIR / "olist_products_dataset.csv"),
        "sellers": pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv"),
    }


@pytest.fixture(scope="module")
def data():
    return {
        name: pd.read_csv(PROCESSED_DIR / f"{name}.csv")
        for name in [
            "customers",
            "orders",
            "order_items",
            "payments",
            "reviews",
            "products",
            "sellers",
        ]
    }


def test_processed_row_counts_match_raw(raw, data):
    mapping = {
        "items": "order_items",
    }

    for raw_name, processed_name in mapping.items():
        assert len(data[processed_name]) == len(raw[raw_name])

    for name in ["customers", "orders", "payments", "reviews", "products", "sellers"]:
        assert len(data[name]) == len(raw[name])


@pytest.mark.parametrize(
    "table,key",
    [
        ("customers", "customer_id"),
        ("orders", "order_id"),
        ("products", "product_id"),
        ("sellers", "seller_id"),
    ],
)
def test_primary_keys_are_unique(data, table, key):
    assert data[table][key].notna().all()
    assert not data[table][key].duplicated().any()


def test_order_item_composite_key_is_unique(data):
    items = data["order_items"]
    assert not items.duplicated(["order_id", "order_item_id"]).any()


def test_payment_composite_key_is_unique(data):
    payments = data["payments"]
    assert not payments.duplicated(
        ["order_id", "payment_sequential"]
    ).any()


def test_orders_reference_existing_customers(data):
    assert data["orders"]["customer_id"].isin(
        data["customers"]["customer_id"]
    ).all()


def test_order_items_reference_existing_orders_products_and_sellers(data):
    items = data["order_items"]

    assert items["order_id"].isin(data["orders"]["order_id"]).all()
    assert items["product_id"].isin(data["products"]["product_id"]).all()
    assert items["seller_id"].isin(data["sellers"]["seller_id"]).all()


def test_payments_reference_existing_orders(data):
    assert data["payments"]["order_id"].isin(
        data["orders"]["order_id"]
    ).all()


def test_reviews_reference_existing_orders(data):
    assert data["reviews"]["order_id"].isin(
        data["orders"]["order_id"]
    ).all()


def test_order_date_quality_flags(data):
    orders = data["orders"]

    expected_counts = {
        "flag_approval_before_purchase": 0,
        "flag_carrier_before_purchase": 166,
        "flag_customer_before_carrier": 23,
        "flag_delivered_missing_customer_date": 8,
    }

    for column, expected in expected_counts.items():
        assert int(orders[column].sum()) == expected


def test_product_translation_column_exists(data):
    assert "product_category_name_english" in data["products"].columns
