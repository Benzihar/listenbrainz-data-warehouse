import duckdb
from pathlib import Path

from config.config import config


def get_connection(logger):
    """
    Creates a connection to the DuckDB database.
    If the database file does not exist, DuckDB creates it automatically.
    """

    db_path = Path(config.database)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Connecting to DuckDB database : {db_path}")

    conn = duckdb.connect(str(db_path))

    logger.info("Database connection established successfully.")

    return conn


def create_schemas(conn, logger):
    """
    Creates all required schemas.
    """

    logger.info("Creating database schemas...")

    conn.execute(
        f"""
        CREATE SCHEMA IF NOT EXISTS {config.bronze_schema};
        """
    )

    conn.execute(
        f"""
        CREATE SCHEMA IF NOT EXISTS {config.silver_schema};
        """
    )

    conn.execute(
        f"""
        CREATE SCHEMA IF NOT EXISTS {config.gold_schema};
        """
    )

    logger.info("Schemas created successfully.")


def create_source_tables(conn, logger):
    """
    Creates all Source Layer tables.
    """

    logger.info("Creating Source Layer tables...")

    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.bronze_schema}.{config.source_raw_table}
        (
            record_number BIGINT,
            raw_json JSON,
            file_name VARCHAR,
            load_id BIGINT,
            load_timestamp TIMESTAMP
        );
        """
    )

    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.bronze_schema}.ARCHIVE_LISTENBRAINZ_RAW
        (
            record_number BIGINT,
            raw_json JSON,
            file_name VARCHAR,
            load_id BIGINT,
            load_timestamp TIMESTAMP
        );
        """
    )

    logger.info("Source Layer tables created successfully.")