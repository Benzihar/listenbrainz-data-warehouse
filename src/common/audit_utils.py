from src.common.config import config

def is_file_processed(conn, file_name):
    """
    Checks whether the given file has already been successfully processed.
    """

    result = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM {config.audit_schema}.{config.etl_file_audit_table}
        WHERE file_name = ?
          AND status = 'SUCCESS'
        """,
        [file_name]
    ).fetchone()[0]

    return result > 0

def log_file_audit(
    conn,
    load_id,
    file_name,
    total_rows,
    status,
    start_time,
    end_time,
    error_message=None,
):
    processing_time = (end_time - start_time).total_seconds()

    conn.execute(
        f"""
        INSERT INTO {config.audit_schema}.{config.etl_file_audit_table}
        (
            load_id,
            file_name,
            total_rows,
            status,
            start_time,
            end_time,
            processing_time_seconds,
            error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            load_id,
            file_name,
            total_rows,
            status,
            start_time,
            end_time,
            processing_time,
            error_message,
        ],
    )