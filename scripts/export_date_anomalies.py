
from pathlib import Path
import pandas as pd

DATA = Path("data/raw/olist")
OUT = Path("data/processed/anomalies")
OUT.mkdir(parents=True, exist_ok=True)

orders = pd.read_csv(DATA / "olist_orders_dataset.csv")

date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

# Carrier date earlier than purchase date
carrier_before_purchase = orders[
    orders["order_delivered_carrier_date"]
    < orders["order_purchase_timestamp"]
].copy()

# Customer delivery earlier than carrier date
customer_before_carrier = orders[
    orders["order_delivered_customer_date"]
    < orders["order_delivered_carrier_date"]
].copy()

# Save full records for investigation
carrier_before_purchase.to_csv(
    OUT / "carrier_before_purchase.csv", index=False
)

customer_before_carrier.to_csv(
    OUT / "customer_before_carrier.csv", index=False
)

print("Carrier before purchase:", len(carrier_before_purchase))
print("Customer before carrier:", len(customer_before_carrier))

columns = [
    "order_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]

print("\n========== CARRIER BEFORE PURCHASE (FIRST 20) ==========")
print(
    carrier_before_purchase[columns]
    .head(20)
    .to_string(index=False)
)

print("\n========== CUSTOMER BEFORE CARRIER (ALL) ==========")
print(
    customer_before_carrier[columns]
    .to_string(index=False)
)

print("\nFiles saved in:", OUT)
