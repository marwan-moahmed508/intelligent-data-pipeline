
import ast
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.postgres import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def get_latest_csv():
    files = sorted(PROCESSED_DIR.glob("cleaned_jobs_*.csv"))

    if not files:
        raise FileNotFoundError("No cleaned jobs CSV file found.")

    return files[-1]


def clean_value(value):
    if pd.isna(value):
        return None
    return value


def parse_tags(value):
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []


def prepare_records(df):
    records = []

    for _, row in df.iterrows():
        publication_date = pd.to_datetime(
            row["publication_date"], errors="coerce", utc=True
        )

        if pd.isna(publication_date):
            publication_date = None
        else:
            publication_date = publication_date.to_pydatetime()

        records.append({
            "id": int(row["id"]),
            "url": clean_value(row["url"]),
            "title": clean_value(row["title"]),
            "company_name": clean_value(row["company_name"]),
            "category": clean_value(row["category"]),
            "tags": parse_tags(row["tags"]),
            "job_type": clean_value(row["job_type"]),
            "publication_date": publication_date,
            "candidate_required_location": clean_value(
                row["candidate_required_location"]
            ),
            "salary": clean_value(row["salary"]),
            "description": clean_value(row["description"]),
        })

    return records


UPSERT_QUERY = text("""
    INSERT INTO jobs (
        id, url, title, company_name, category, tags,
        job_type, publication_date, candidate_required_location,
        salary, description
    )
    VALUES (
        :id, :url, :title, :company_name, :category, :tags,
        :job_type, :publication_date, :candidate_required_location,
        :salary, :description
    )
    ON CONFLICT (id) DO UPDATE SET
        url = EXCLUDED.url,
        title = EXCLUDED.title,
        company_name = EXCLUDED.company_name,
        category = EXCLUDED.category,
        tags = EXCLUDED.tags,
        job_type = EXCLUDED.job_type,
        publication_date = EXCLUDED.publication_date,
        candidate_required_location = EXCLUDED.candidate_required_location,
        salary = EXCLUDED.salary,
        description = EXCLUDED.description,
        updated_at = CURRENT_TIMESTAMP;
""")


def load_jobs():
    csv_path = get_latest_csv()
    print(f"Loading data from: {csv_path.name}")

    df = pd.read_csv(csv_path)
    records = prepare_records(df)

    if not records:
        print("No records to load.")
        return

    with engine.begin() as connection:
        connection.execute(UPSERT_QUERY, records)

    print(f"Successfully loaded {len(records)} records into PostgreSQL.")


if __name__ == "__main__":
    load_jobs()
