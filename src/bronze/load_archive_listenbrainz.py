from src.common.config import config
from src.common.etl_utils import execute_insert


def archive_bronze_data(conn, load_id, logger):
    """
    Archive successfully processed Bronze records.
    """

    logger.info("=" * 50)
    logger.info("Archiving Bronze Data")
    logger.info("=" * 50)

    raw_table = (
        f"{config.bronze_schema}."
        f"{config.source_raw_table}"
    )

    archive_table = (
        f"{config.bronze_schema}."
        f"{config.archive_raw_table}"
    )

    # ============================================================
    # COUNT ROWS TO ARCHIVE
    # ============================================================

    count_sql = f"""
    SELECT COUNT(*)
    FROM {raw_table};
    """

    archive_rows = conn.execute(count_sql).fetchone()[0]

    # ============================================================
    # ARCHIVE BRONZE DATA
    # ============================================================

    archive_sql = f"""
    INSERT INTO {archive_table}
    (
        record_number,
        raw_json,
        file_name,
        load_id,
        load_timestamp
    )

    SELECT
        record_number,
        raw_json,
        file_name,
        load_id,
        load_timestamp

    FROM {raw_table};
    """

    execute_insert(
        conn=conn,
        sql=archive_sql,
        params=[],
        logger=logger,
        object_name="BRONZE_ARCHIVE",
        expected_rows=archive_rows,
        load_id=load_id,
    )

    logger.info("Bronze data archived successfully.")

    # ============================================================
    # VALIDATE ARCHIVE
    # ============================================================

    raw_count_sql = f"""
    SELECT COUNT(*)
    FROM {raw_table};
    """

    raw_rows = conn.execute(raw_count_sql).fetchone()[0]

    archive_count_sql = f"""
    SELECT COUNT(*)
    FROM {archive_table}
    WHERE load_id = ?;
    """

    archived_rows = conn.execute(
        archive_count_sql,
        [load_id]
    ).fetchone()[0]

    logger.info(f"Raw Rows      : {raw_rows:,}")
    logger.info(f"Archived Rows : {archived_rows:,}")

    if raw_rows != archived_rows:

        raise Exception(
            "Archive validation failed. "
            "Raw and Archive row counts do not match."
        )

    logger.info("Archive validation completed successfully.")

        # ============================================================
    # CLEANUP RAW TABLE
    # ============================================================

    logger.info("Cleaning Bronze Raw table...")

    truncate_sql = f"""
    DELETE FROM {raw_table} WHERE load_id = ?;
    """

    conn.execute(truncate_sql,[load_id])

    logger.info("Bronze Raw table cleaned successfully.")

    # ============================================================
    # DELETE ARCHIVE DATA OLDER THAN 7 DAYS
    # ============================================================

    delete_count_sql = f"""
    SELECT COUNT(*)
    FROM {archive_table}
    WHERE load_timestamp <
          CURRENT_TIMESTAMP - INTERVAL '7 DAYS';
    """

    delete_rows = conn.execute(
        delete_count_sql
    ).fetchone()[0]

    if delete_rows > 0:

        logger.info(
            f"Deleting {delete_rows:,} archived record(s) older than 7 days..."
        )

        delete_sql = f"""
        DELETE
        FROM {archive_table}
        WHERE load_timestamp <
              CURRENT_TIMESTAMP - INTERVAL '7 DAYS';
        """

        conn.execute(delete_sql)

        logger.info(
            f"Successfully deleted {delete_rows:,} archived record(s)."
        )

    else:

        logger.info(
            "No archived records older than 7 days found."
        )

    logger.info("Bronze housekeeping completed successfully.")