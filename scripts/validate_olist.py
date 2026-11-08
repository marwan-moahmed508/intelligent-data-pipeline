
from pathlib import Path
import pandas as pd

DATA = Path("data/raw/olist")

def load(name):
    return pd.read_csv(DATA / name)

customers = load("olist_customers_dataset.csv")
orders = load("olist_orders_dataset.csv")
items = load("olist_order_items_dataset.csv")
payments = load("olist_order_payments_dataset.csv")
reviews = load("olist_order_reviews_dataset.csv")
products = load("olist_products_dataset.csv")
sellers = load("olist_sellers_dataset.csv")
translations = load("product_category_name_translation.csv")

def check(name, condition):
    print(f"{name}: {int(condition.sum()):,}")

print("\n========== PRIMARY KEY CHECKS ==========")

check("Duplicate customer_id", customers["customer_id"].duplicated())
check("Duplicate order_id", orders["order_id"].duplicated())
check("Duplicate product_id", products["product_id"].duplicated())
check("Duplicate seller_id", sellers["seller_id"].duplicated())

print("\n========== RELATIONSHIP CHECKS ==========")

check(
    "Orders with unknown customer",
    ~orders["customer_id"].isin(customers["customer_id"])
)

check(
    "Items with unknown order",
    ~items["order_id"].isin(orders["order_id"])
)

check(
    "Items with unknown product",
    ~items["product_id"].isin(products["product_id"])
)

check(
    "Items with unknown seller",
    ~items["seller_id"].isin(sellers["seller_id"])
)

check(
    "Payments with unknown order",
    ~payments["order_id"].isin(orders["order_id"])
)

check(
    "Reviews with unknown order",
    ~reviews["order_id"].isin(orders["order_id"])
)

print("\n========== COMPOSITE KEY CHECKS ==========")

check(
    "Duplicate order_id + order_item_id",
    items.duplicated(["order_id", "order_item_id"])
)

check(
    "Duplicate order_id + payment_sequential",
    payments.duplicated(["order_id", "payment_sequential"])
)

print("\n========== BUSINESS RULES ==========")

check("Invalid review scores", ~reviews["review_score"].between(1, 5))
check("Zero or negative item prices", items["price"] <= 0)
check("Negative freight values", items["freight_value"] < 0)
check("Zero or negative payment values", payments["payment_value"] <= 0)
check("Invalid payment installments", payments["payment_installments"] < 1)

print("\n========== ORDER STATUS ==========")

print(orders["order_status"].value_counts(dropna=False).to_string())

date_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date"
]

for col in date_columns:
    print(f"\nMissing {col} by order status:")
    print(
        orders.groupby("order_status")[col]
        .apply(lambda s: s.isna().sum())
        .to_string()
    )

print("\n========== CATEGORY TRANSLATION ==========")

mapped = set(translations["product_category_name"])
categories = set(products["product_category_name"].dropna())

print("Categories without English translation:", len(categories - mapped))

print("\n========== DONE ==========")
