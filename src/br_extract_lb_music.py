import shutil
from datetime import datetime
from pathlib import Path

from config.config import config


def get_next_load_id(conn):
    """
    Generates the next Load ID in the format:
    YYYYMMDD100
    YYYYMMDD101
    YYYYMMDD102
    """

    today = datetime.now().strftime("%Y%m%d")

    result = conn.execute(
        f"""
        SELECT COALESCE(MAX(load_id), 0)
        FROM {config.bronze_schema}.{config.source_raw_table}
        WHERE CAST(load_id AS VARCHAR) LIKE '{today}%'
        """
    ).fetchone()

    if result[0] == 0:
        return int(f"{today}100")

    return result[0] + 1


def load_source_layer(conn, logger):
    """
    Loads ListenBrainz files from the incoming folder into the
    Bronze (Source) layer.
    """

    incoming_path = Path(config.incoming_folder)
    archive_path = Path(config.archive_folder)
    error_path = Path(config.error_folder)

    archive_path.mkdir(parents=True, exist_ok=True)
    error_path.mkdir(parents=True, exist_ok=True)

    files = list(incoming_path.glob("*.ndjson"))
    files.extend(incoming_path.glob("*.txt"))

    if not files:
        logger.warning("No source files found in incoming folder.")
        return

    for file in files:

        logger.info("=" * 80)
        logger.info(f"Processing File : {file.name}")

        load_id = get_next_load_id(conn)
        file_path = file.as_posix()

        logger.info(f"Load ID : {load_id}")

        try:

            logger.info(
                f"Loading '{file.name}' into "
                f"{config.bronze_schema}.{config.source_raw_table}"
            )

            conn.execute("BEGIN TRANSACTION")

            conn.execute(
                f"""
                INSERT INTO {config.bronze_schema}.{config.source_raw_table}
                SELECT
                    ROW_NUMBER() OVER () AS record_number,
                    json AS raw_json,
                    '{file.name}' AS file_name,
                    {load_id} AS load_id,
                    CURRENT_TIMESTAMP AS load_timestamp
                FROM read_ndjson_objects('{file_path}');
                """
            )

            conn.execute("COMMIT")

            rows_loaded = conn.execute(
                f"""
                SELECT COUNT(*)
                FROM {config.bronze_schema}.{config.source_raw_table}
                WHERE load_id = {load_id}
                """
            ).fetchone()[0]

            logger.info(f"Rows Loaded : {rows_loaded:,}")

            shutil.move(
                str(file),
                str(archive_path / file.name)
            )

            logger.info(f"Moved '{file.name}' to archive folder.")
            logger.info("Source Layer load completed successfully.")

        except Exception as ex:

            conn.execute("ROLLBACK")

            logger.exception(
                f"Failed to process '{file.name}'. Error: {ex}"
            )

            shutil.move(
                str(file),
                str(error_path / file.name)
            )

            logger.info(f"Moved '{file.name}' to error folder.")

            raise