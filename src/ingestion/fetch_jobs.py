import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests


# Project configuration
API_URL = "https://remotive.com/api/remote-jobs"
JOBS_LIMIT = 10
TIMEOUT = 30

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def fetch_jobs(limit: int = JOBS_LIMIT) -> dict:
    """Fetch remote job listings from Remotive API."""

    params = {"limit": limit}

    logger.info("Starting API request...")

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Unexpected API response format.")

        jobs = data.get("jobs")

        if not isinstance(jobs, list):
            raise ValueError("The API response does not contain a valid jobs list.")

        logger.info("Successfully fetched %d jobs.", len(jobs))

        return data

    except requests.RequestException:
        logger.exception("Failed to fetch data from the API.")
        raise

    except ValueError:
        logger.exception("Invalid API response.")
        raise


def save_raw_data(data: dict) -> Path:
    """Save the original API response as a timestamped JSON file."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    file_path = RAW_DATA_DIR / f"jobs_{timestamp}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    logger.info("Raw data saved to: %s", file_path)

    return file_path


def main():
    data = fetch_jobs()
    file_path = save_raw_data(data)

    print(f"\nSuccess! Fetched {len(data['jobs'])} jobs.")
    print(f"Saved file: {file_path}")


if __name__ == "__main__":
    main()