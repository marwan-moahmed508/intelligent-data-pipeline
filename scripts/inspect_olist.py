
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw/olist")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(DATA_DIR.glob("*.csv"))

if not files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

summary = []

for file in files:
    print("\n" + "=" * 70)
    print(f"FILE: {file.name}")
    print("=" * 70)

    df = pd.read_csv(file)

    rows, columns = df.shape
    duplicate_rows = int(df.duplicated().sum())
    missing_cells = int(df.isna().sum().sum())

    print(f"Rows: {rows:,}")
    print(f"Columns: {columns}")
    print(f"Duplicate rows: {duplicate_rows:,}")
    print(f"Missing cells: {missing_cells:,}")

    print("\nColumn details:")
    details = pd.DataFrame({
        "column": df.columns,
        "dtype": [str(df[col].dtype) for col in df.columns],
        "missing": [int(df[col].isna().sum()) for col in df.columns],
        "missing_percent": [
            round(df[col].isna().mean() * 100, 2)
            for col in df.columns
        ],
        "unique_values": [int(df[col].nunique()) for col in df.columns]
    })

    print(details.to_string(index=False))

    summary.append({
        "file": file.name,
        "rows": rows,
        "columns": columns,
        "duplicate_rows": duplicate_rows,
        "missing_cells": missing_cells
    })

report = pd.DataFrame(summary)
report.to_csv(
    OUTPUT_DIR / "olist_quality_summary.csv",
    index=False
)

print("\n" + "=" * 70)
print("QUALITY SUMMARY")
print("=" * 70)
print(report.to_string(index=False))

print(f"\nReport saved to: {OUTPUT_DIR / 'olist_quality_summary.csv'}")
