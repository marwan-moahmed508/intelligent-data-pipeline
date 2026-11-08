
from pathlib import Path
import pandas as pd

DATA = Path("data/raw/olist")

def load(name):
    return pd.read_csv(DATA / name)

payments = load("olist_order_payments_dataset.csv")
orders = load("olist_orders_dataset.csv")
products = load("olist_products_dataset.csv")
translations = load("product_category_name_translation.csv")

print("\n========== INVALID PAYMENTS ==========")

bad_payments = payments[
    payments["payment_value"] <= 0
]

print(f"Count: {len(bad_payments)}")
print(bad_payments.to_string(index=False))

print("\n========== INVALID INSTALLMENTS ==========")

bad_installments = payments[
    payments["payment_installments"] < 1
]

print(f"Count: {len(bad_installments)}")
print(bad_installments.to_string(index=False))

print("\n========== DELIVERED ORDERS WITHOUT DELIVERY DATE ==========")

bad_delivered = orders[
    (orders["order_status"] == "delivered")
    & (orders["order_delivered_customer_date"].isna())
]

print(f"Count: {len(bad_delivered)}")
print(bad_delivered.to_string(index=False))

print("\n========== CATEGORIES WITHOUT TRANSLATION ==========")

translated = set(translations["product_category_name"])
categories = set(products["product_category_name"].dropna())

untranslated = sorted(categories - translated)

print(f"Count: {len(untranslated)}")
for category in untranslated:
    print("-", category)

print("\n========== DATE ORDER VALIDATION ==========")

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_columns:
    orders[col] = pd.to_datetime(orders[col], errors="coerce", utc=True)

checks = {
    "Approval before purchase": (
        orders["order_approved_at"] < orders["order_purchase_timestamp"]
    ),
    "Carrier delivery before purchase": (
        orders["order_delivered_carrier_date"] < orders["order_purchase_timestamp"]
    ),
    "Customer delivery before carrier delivery": (
        orders["order_delivered_customer_date"] < orders["order_delivered_carrier_date"]
    ),
    "Customer delivery before purchase": (
        orders["order_delivered_customer_date"] < orders["order_purchase_timestamp"]
    ),
}

for label, condition in checks.items():
    print(f"{label}: {int(condition.fillna(False).sum())}")

print("\n========== DONE ==========")
