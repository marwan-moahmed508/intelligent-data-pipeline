
import logging
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "id",
    "url",
    "title",
    "company_name",
    "publication_date",
]


def load_latest_data() -> pd.DataFrame:
    """Load the latest processed CSV file."""

    files = sorted(PROCESSED_DATA_DIR.glob("cleaned_jobs_*.csv"))

    if not files:
        raise FileNotFoundError("No processed CSV files found.")

    latest_file = files[-1]

    df = pd.read_csv(latest_file)

    logger.info("Loaded %d records from %s", len(df), latest_file.name)

    return df


def run_quality_checks(df: pd.DataFrame) -> bool:
    """Run data quality checks and return the overall result."""

    errors = []
    warnings = []

    # 1. Check that the dataset is not empty
    if df.empty:
        errors.append("Dataset is empty.")

    # 2. Check required columns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")

    if missing_columns:
        for error in errors:
            logger.error(error)
        return False

    # 3. Check missing essential values
    for column in ["id", "title", "company_name"]:
        missing_count = df[column].isna().sum()

        if missing_count > 0:
            errors.append(
                f"{column} contains {missing_count} missing values."
            )

    # 4. Check duplicate job IDs
    duplicate_count = df["id"].duplicated().sum()

    if duplicate_count > 0:
        errors.append(
            f"Found {duplicate_count} duplicate job IDs."
        )

    # 5. Check invalid URLs
    invalid_urls = (
        df["url"].isna()
        | ~df["url"].astype(str).str.startswith("https://")
    ).sum()

    if invalid_urls > 0:
        warnings.append(
            f"Found {invalid_urls} missing or invalid URLs."
        )

    # 6. Check publication dates
    invalid_dates = pd.to_datetime(
        df["publication_date"],
        errors="coerce",
        utc=True
    ).isna().sum()

    if invalid_dates > 0:
        warnings.append(
            f"Found {invalid_dates} invalid publication dates."
        )

    # Print report
    print("\n========== DATA QUALITY REPORT ==========")
    print(f"Total records: {len(df)}")
    print(f"Duplicate IDs: {duplicate_count}")
    print(f"Missing IDs: {df['id'].isna().sum()}")
    print(f"Missing titles: {df['title'].isna().sum()}")
    print(f"Missing companies: {df['company_name'].isna().sum()}")

    print("\nWarnings:")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    else:
        print("No warnings.")

    print("\nErrors:")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
    else:
        print("No errors.")

    print("\nFinal result:")
    if errors:
        print("FAILED - Data quality checks did not pass.")
    else:
        print("PASSED - Data quality checks passed.")

    print("=========================================\n")

    return len(errors) == 0


def main():
    df = load_latest_data()
    passed = run_quality_checks(df)

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
