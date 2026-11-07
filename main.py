
import logging

from src.ingestion.fetch_jobs import fetch_jobs, save_raw_data
from src.transformation.clean_jobs import transform_jobs, save_processed_data
from src.validation.quality_checks import run_quality_checks
from src.database.load_jobs import load_jobs


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_pipeline():
    """Execute the complete ETL pipeline."""

    try:
        # 1. Extract
        logger.info("========== EXTRACTION STARTED ==========")

        raw_data = fetch_jobs()
        save_raw_data(raw_data)

        jobs = raw_data["jobs"]

        # 2. Transform
        logger.info("========== TRANSFORMATION STARTED ==========")

        df = transform_jobs(jobs)
        save_processed_data(df)

        # 3. Validate
        logger.info("========== VALIDATION STARTED ==========")

        validation_passed = run_quality_checks(df)

        if not validation_passed:
            raise ValueError(
                "Pipeline stopped: Data quality checks failed."
            )

        # 4. Load
        logger.info("========== LOADING STARTED ==========")

        load_jobs()

        logger.info("========== PIPELINE COMPLETED ==========")

        print("\nSUCCESS: Complete ETL pipeline executed!")

    except Exception:
        logger.exception("Pipeline execution failed.")
        raise


if __name__ == "__main__":
    run_pipeline()
