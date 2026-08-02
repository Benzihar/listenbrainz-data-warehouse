import duckdb
from pathlib import Path

from src.common.config import config


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

    conn.execute(
        f"""
        CREATE SCHEMA IF NOT EXISTS {config.audit_schema};
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
        CREATE TABLE IF NOT EXISTS {config.bronze_schema}.{config.archive_raw_table}
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

def create_silver_tables(conn, logger):
    """
    Creates all Silver Layer tables.
    """

    logger.info("Creating Silver Layer tables...")

    # DIM_DATE
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.silver_schema}.{config.dim_date_table}
        (
            date_key INTEGER PRIMARY KEY,
            full_date DATE NOT NULL,

            day_of_month TINYINT,
            day_of_week TINYINT,
            day_name VARCHAR,

            week_of_year TINYINT,

            month_number TINYINT,
            month_name VARCHAR,

            quarter_number TINYINT,
            year_number SMALLINT,

            is_weekend BOOLEAN,

            created_at TIMESTAMP,
            updated_at TIMESTAMP,

            load_id BIGINT,
            load_timestamp TIMESTAMP
        );
        """
    )

    # DIM_USER
    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS seq_dim_user;
    """)
    
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.silver_schema}.{config.dim_user_table}
        (
            user_key BIGINT PRIMARY KEY DEFAULT nextval('seq_dim_user'),
            user_name VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            load_id BIGINT,
            load_timestamp TIMESTAMP
        );
        """
    )

    # DIM_ARTIST
    # DIM_ARTIST
    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS seq_dim_artist;
    """)

    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.silver_schema}.{config.dim_artist_table}
        (
            artist_key BIGINT PRIMARY KEY DEFAULT nextval('seq_dim_artist'),

            artist_msid VARCHAR,
            artist_name VARCHAR,

            created_at TIMESTAMP,
            updated_at TIMESTAMP,

            load_id BIGINT,
            load_timestamp TIMESTAMP
        );
        """
    )

    # DIM_RELEASE
    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS seq_dim_release;
    """)

    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.silver_schema}.{config.dim_release_table}
        (
            release_key BIGINT PRIMARY KEY DEFAULT nextval('seq_dim_release'),
            release_msid VARCHAR,
            release_name VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            load_id BIGINT,
            load_timestamp TIMESTAMP
        );
        """
    )

    # DIM_RECORDING
    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS seq_dim_recording;
    """)

    conn.execute(
    f"""
    CREATE TABLE IF NOT EXISTS {config.silver_schema}.{config.dim_recording_table}
        (
            recording_key BIGINT PRIMARY KEY DEFAULT nextval('seq_dim_recording'),
            recording_msid VARCHAR,
            track_name VARCHAR,
            artist_key BIGINT,
            release_key BIGINT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            load_id BIGINT,
            load_timestamp TIMESTAMP,
            FOREIGN KEY (artist_key)
                REFERENCES {config.silver_schema}.{config.dim_artist_table}(artist_key),
            FOREIGN KEY (release_key)
                REFERENCES {config.silver_schema}.{config.dim_release_table}(release_key)
        );
        """
    )

    # FACT_LISTEN
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.silver_schema}.{config.fact_listen_table}
        (
            listen_key BIGINT PRIMARY KEY,
            user_key BIGINT,
            recording_key BIGINT,
            listened_at TIMESTAMP,
            load_id BIGINT,
            load_timestamp TIMESTAMP,
            FOREIGN KEY (user_key)
                REFERENCES {config.silver_schema}.{config.dim_user_table}(user_key),
            FOREIGN KEY (recording_key)
                REFERENCES {config.silver_schema}.{config.dim_recording_table}(recording_key)
        );
        """
    )

    logger.info("Silver Layer tables created successfully.")

def create_audit_tables(conn, logger):
    """
    Creates all Audit tables.
    """

    logger.info("Creating Audit tables...")

    # ETL_FILE_AUDIT
    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS seq_file_audit;
    """)

    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.audit_schema}.{config.etl_file_audit_table}
        (
        audit_id BIGINT PRIMARY KEY DEFAULT nextval('seq_file_audit'),
        load_id BIGINT,
        file_name VARCHAR,
        total_rows BIGINT,
        status VARCHAR,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        processing_time_seconds DOUBLE,
        error_message VARCHAR
        );
        """
    )

    # ETL_OBJECT_AUDIT
    conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS seq_object_audit;
    """);
    
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {config.audit_schema}.{config.etl_object_audit_table}
        (
        audit_id BIGINT PRIMARY KEY DEFAULT nextval('seq_object_audit'),
        load_id BIGINT,
        object_name VARCHAR,
        inserted_rows BIGINT,
        updated_rows BIGINT,
        deleted_rows BIGINT,
        rejected_rows BIGINT,
        status VARCHAR,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        processing_time_seconds DOUBLE,
        error_message VARCHAR
        );
        """
    )

    logger.info("Audit Layer tables created successfully.")