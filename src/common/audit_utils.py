from src.common.config import config


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