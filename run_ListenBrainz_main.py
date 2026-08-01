from src.common.config import config
from src.database.create_db import (
    get_connection,
    create_schemas,
    create_source_tables,
    create_silver_tables,
    create_audit_tables
)

from src.bronze.br_extract_lb_music import load_source_layer
from src.silver.load_dim_user import load_dim_user

from src.common.generate_logs import get_logger
from src.common.etl_utils import generate_load_id


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
    logger.info(f"Audit Schema     : {config.audit_schema}")

    logger.info(f"Incoming Folder : {config.incoming_folder}")
    logger.info(f"Archive Folder  : {config.archive_folder}")
    logger.info(f"Error Folder    : {config.error_folder}")

    conn = None

    try:

        # Establish database connection
        conn = get_connection(logger)

        # Generate one Load ID for the complete ETL execution
        load_id = generate_load_id()

        logger.info(f"ETL Load ID : {load_id}")

        # Create Schemas
        create_schemas(conn, logger)

        # Create Bronze Tables
        create_source_tables(conn, logger)

        # Create Silver Tables
        create_silver_tables(conn, logger)

        # Create Silver Tables
        create_audit_tables(conn, logger)

        # Load Bronze Layer
        load_source_layer(
            conn=conn,
            load_id=load_id,
            logger=logger
        )

        logger.info("ETL Pipeline for raw data loading completed successfully.")

        # Load Dimensions
        load_dim_user(
            conn=conn,
            load_id=load_id,
            logger=logger
        )

        logger.info("ETL Pipeline for dimensions completed successfully.")

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