import logging

from src.transformation.clean_olist import main as transform_olist
from src.database.load_olist import main as load_olist


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def run_pipeline():
    """Run the Olist data transformation and database loading pipeline."""
    try:
        logger.info("========== OLIST TRANSFORMATION ==========")
        transform_olist()

        logger.info("========== OLIST DATABASE LOADING ==========")
        load_olist()

        logger.info("========== OLIST PIPELINE COMPLETED ==========")

    except Exception:
        logger.exception("Olist pipeline failed.")
        raise


if __name__ == "__main__":
    run_pipeline()
