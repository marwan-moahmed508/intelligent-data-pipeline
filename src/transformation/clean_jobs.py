
import json
import logging
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_raw_data() -> list:
    """Load the latest raw jobs JSON file."""

    files = sorted(RAW_DATA_DIR.glob("jobs_*.json"))

    if not files:
        raise FileNotFoundError("No raw data files found.")

    latest_file = files[-1]

    with latest_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    jobs = data.get("jobs", [])

    logger.info("Loaded %d jobs from %s", len(jobs), latest_file.name)

    return jobs


def clean_description(description) -> str:
    """Convert HTML job descriptions into plain text."""

    if not isinstance(description, str):
        return ""

    soup = BeautifulSoup(description, "html.parser")

    return soup.get_text(separator=" ", strip=True)


def transform_jobs(jobs: list) -> pd.DataFrame:
    """Clean and transform raw job records."""

    df = pd.DataFrame(jobs)

    # Keep only the fields needed for analysis
    selected_columns = [
        "id",
        "url",
        "title",
        "company_name",
        "category",
        "tags",
        "job_type",
        "publication_date",
        "candidate_required_location",
        "salary",
        "description",
    ]

    df = df[selected_columns].copy()

    # Remove duplicate job IDs
    df = df.drop_duplicates(subset=["id"])

    # Clean text fields
    text_columns = [
        "title",
        "company_name",
        "category",
        "job_type",
        "candidate_required_location",
        "salary",
    ]

    for column in text_columns:
        df[column] = df[column].fillna("").astype(str).str.strip()

    # Clean HTML descriptions
    df["description"] = df["description"].apply(clean_description)

    # Normalize tags
    df["tags"] = df["tags"].apply(
        lambda value: value if isinstance(value, list) else []
    )

    # Convert publication date
    df["publication_date"] = pd.to_datetime(
        df["publication_date"],
        errors="coerce",
        utc=True
    )

    # Remove records without essential information
    df = df[
        df["id"].notna()
        & df["title"].ne("")
        & df["company_name"].ne("")
    ].copy()

    logger.info("Transformed dataset contains %d jobs", len(df))

    return df


def save_processed_data(df: pd.DataFrame) -> Path:
    """Save cleaned jobs as CSV."""

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y%m%d_%H%M%S")

    output_file = PROCESSED_DATA_DIR / f"cleaned_jobs_{timestamp}.csv"

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    logger.info("Processed data saved to %s", output_file)

    return output_file


def main():
    jobs = load_raw_data()

    df = transform_jobs(jobs)

    output_file = save_processed_data(df)

    print("\nTransformation completed!")
    print(f"Total cleaned jobs: {len(df)}")
    print(f"Output file: {output_file}")

    print("\nData preview:")
    print(df[["id", "title", "company_name", "category"]].head())


if __name__ == "__main__":
    main()
