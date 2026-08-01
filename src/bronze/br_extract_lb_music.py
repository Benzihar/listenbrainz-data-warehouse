import shutil
from datetime import datetime
from pathlib import Path

from src.common.audit_utils import log_file_audit
from src.common.config import config


def load_source_layer(conn, load_id, logger):
    """
    Loads ListenBrainz files from the incoming folder into the Bronze layer.
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

        start_time = datetime.now()

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

            end_time = datetime.now()

            logger.info(f"Rows Loaded : {rows_loaded:,}")

            log_file_audit(
                conn=conn,
                load_id=load_id,
                file_name=file.name,
                total_rows=rows_loaded,
                status="SUCCESS",
                start_time=start_time,
                end_time=end_time,
                error_message=None,
            )

            shutil.move(
                str(file),
                str(archive_path / file.name)
            )

            logger.info(f"Moved '{file.name}' to archive folder.")
            logger.info("Source Layer load completed successfully.")

        except Exception as ex:

            conn.execute("ROLLBACK")

            end_time = datetime.now()

            log_file_audit(
                conn=conn,
                load_id=load_id,
                file_name=file.name,
                total_rows=0,
                status="FAILED",
                start_time=start_time,
                end_time=end_time,
                error_message=str(ex),
            )

            logger.exception(
                f"Failed to process '{file.name}'. Error: {ex}"
            )

            shutil.move(
                str(file),
                str(error_path / file.name)
            )

            logger.info(f"Moved '{file.name}' to error folder.")

            raise