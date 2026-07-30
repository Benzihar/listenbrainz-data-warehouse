from config.config import config
from src.create_db import (
    get_connection,
    create_schemas,
    create_source_tables
)
from src.br_extract_lb_music import load_source_layer
from src.generate_logs import get_logger


def main():

    logger = get_logger()

    logger.info("=" * 80)
    logger.info("ListenBrainz ETL Pipeline Started")
    logger.info("=" * 80)

    logger.info("Configuration loaded successfully.")

    logger.info(f"Database Path   : {config.database}")
    logger.info(f"Bronze Schema   : {config.bronze_schema}")
    logger.info(f"Silver Schema   : {config.silver_schema}")
    logger.info(f"Gold Schema     : {config.gold_schema}")

    logger.info(f"Incoming Folder : {config.incoming_folder}")
    logger.info(f"Archive Folder  : {config.archive_folder}")
    logger.info(f"Error Folder    : {config.error_folder}")

    conn = None

    try:

        # Establish database connection
        conn = get_connection(logger)

        # Create schemas
        create_schemas(conn, logger)

        # Create Source Layer tables
        create_source_tables(conn, logger)

        # Load NDJSON files into Source Layer
        load_source_layer(conn, logger)

        logger.info("ETL Pipeline completed successfully.")

    except Exception:

        logger.exception("ETL Pipeline failed.")
        raise

    finally:

        if conn:
            conn.close()
            logger.info("Database connection closed.")

        logger.info("=" * 80)
        logger.info("ListenBrainz ETL Pipeline Finished")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()