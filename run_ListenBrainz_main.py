from venv import logger
from src.bronze.load_archive_listenbrainz import archive_bronze_data
from src.common.config import config
from src.silver.load_dim_date import load_dim_date
from src.silver.load_dim_artist import load_dim_artist
from src.silver.load_dim_release import load_dim_release
from src.silver.load_dim_recording import load_dim_recording
from src.silver.load_fact_listen import load_fact_listen
from src.database.create_db import (
    get_connection,
    create_schemas,
    create_source_tables,
    create_silver_tables,
    create_audit_tables,
)
from src.bronze.br_extract_lb_music import load_source_layer
from src.silver.load_dim_user import load_dim_user
from src.common.generate_logs import get_logger
from src.common.etl_utils import generate_load_id
from src.dq.run_dq_checks import run_dq_checks
from src.gold.load_gold_views import create_gold_views


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
    logger.info(f"Audit Schema    : {config.audit_schema}")
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

        # Create Audit Tables
        create_audit_tables(conn, logger)

        # Load Source Layer
        files_processed = load_source_layer(
            conn=conn,
            load_id=load_id,
            logger=logger,
        )

        # Stop ETL if no new files were processed
        if not files_processed:

            logger.info("=" * 80)
            logger.info("No new files found for processing.")
            logger.info("ETL Pipeline finished successfully.")
            return

        logger.info("ETL Pipeline for raw data loading completed successfully.")

        # Load Date Dimension
        load_dim_date(
            conn=conn,
            load_id=load_id,
            logger=logger
        )

        # Load User Dimension
        load_dim_user(
            conn=conn,
            load_id=load_id,
            logger=logger,
        )

        # Load Artist Dimension
        load_dim_artist(
            conn=conn,
            load_id=load_id,
            logger=logger
        )

        # Load Release Dimension
        load_dim_release(
            conn=conn,
            load_id=load_id,
            logger=logger
        )

        # Load Recording Dimension
        load_dim_recording(
            conn=conn,
            load_id=load_id,
            logger=logger
        )

        logger.info("ETL Pipeline for dimensions completed successfully.")

        # Load Listen Fact
        load_fact_listen(
            conn=conn,
            load_id=load_id,
            logger=logger
        )
        logger.info("ETL Pipeline for facts completed successfully.")

        # Archive Bronze Data
        archive_bronze_data(
            conn=conn,
            load_id=load_id,
            logger=logger
        )
        logger.info("Bronze archive completed successfully.")

        # Run Data Quality Framework
        
        run_dq_checks(
            conn=conn,
            load_id=load_id,
            logger=logger
        )

        logger.info("Data Quality checks completed successfully.")

        # Create Gold Layer Views

        create_gold_views(
            conn=conn,
            logger=logger
        )

        logger.info("Gold Layer created successfully.")
        

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