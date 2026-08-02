from datetime import datetime

from src.common.config import config


# ============================================================
# STATUS CONSTANTS
# ============================================================

STATUS_SUCCESS = "SUCCESS"
STATUS_SUCCESS_NO_CHANGE = "SUCCESS_NO_CHANGE"
STATUS_FAILED = "FAILED"


# ============================================================
# LOAD ID
# ============================================================

def generate_load_id():
    """
    Generates a unique LOAD_ID for a single ETL execution.
    """
    return int(datetime.now().strftime("%Y%m%d%H%M%S"))


# ============================================================
# OBJECT AUDIT
# ============================================================

def write_object_audit(
    conn,
    load_id,
    object_name,
    inserted_rows,
    updated_rows,
    deleted_rows,
    rejected_rows,
    status,
    start_time,
    end_time,
    error_message=None,
):
    """
    Writes one audit record for an ETL object.
    """

    processing_time_seconds = round(
        (end_time - start_time).total_seconds(),
        3
    )

    audit_table = (
        f"{config.audit_schema}."
        f"{config.etl_object_audit_table}"
    )

    sql = f"""
    INSERT INTO {audit_table}
    (
        load_id,
        object_name,
        inserted_rows,
        updated_rows,
        deleted_rows,
        rejected_rows,
        status,
        start_time,
        end_time,
        processing_time_seconds,
        error_message
    )
    VALUES
    (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    """

    conn.execute(
        sql,
        [
            load_id,
            object_name,
            inserted_rows,
            updated_rows,
            deleted_rows,
            rejected_rows,
            status,
            start_time,
            end_time,
            processing_time_seconds,
            error_message,
        ],
    )


# ============================================================
# INSERT
# ============================================================

def execute_insert(
    conn,
    sql,
    params,
    logger,
    object_name,
    expected_rows,
    load_id,
):
    """
    Executes an INSERT statement and writes ETL audit.
    """

    start_time = datetime.now()

    try:

        if expected_rows == 0:

            logger.info(f"{object_name}: No new records found.")

            end_time = datetime.now()

            write_object_audit(
                conn=conn,
                load_id=load_id,
                object_name=object_name,
                inserted_rows=0,
                updated_rows=0,
                deleted_rows=0,
                rejected_rows=0,
                status=STATUS_SUCCESS_NO_CHANGE,
                start_time=start_time,
                end_time=end_time,
            )

            return 0

        logger.info(
            f"{object_name}: Inserting {expected_rows} record(s)..."
        )

        conn.execute(sql, params)

        logger.info(
            f"{object_name}: Successfully inserted {expected_rows} record(s)."
        )

        end_time = datetime.now()

        write_object_audit(
            conn=conn,
            load_id=load_id,
            object_name=object_name,
            inserted_rows=expected_rows,
            updated_rows=0,
            deleted_rows=0,
            rejected_rows=0,
            status=STATUS_SUCCESS,
            start_time=start_time,
            end_time=end_time,
        )

        return expected_rows

    except Exception as ex:

        end_time = datetime.now()

        write_object_audit(
            conn=conn,
            load_id=load_id,
            object_name=object_name,
            inserted_rows=0,
            updated_rows=0,
            deleted_rows=0,
            rejected_rows=0,
            status=STATUS_FAILED,
            start_time=start_time,
            end_time=end_time,
            error_message=str(ex),
        )

        logger.exception(f"{object_name}: Insert failed.")

        raise


# ============================================================
# UPDATE
# ============================================================

def execute_update(
    conn,
    sql,
    params,
    logger,
    object_name,
    expected_rows,
    load_id,
):
    """
    Executes an UPDATE statement and writes ETL audit.
    """

    start_time = datetime.now()

    try:

        if expected_rows == 0:

            logger.info(
                f"{object_name}: No records require updating."
            )

            end_time = datetime.now()

            write_object_audit(
                conn=conn,
                load_id=load_id,
                object_name=object_name,
                inserted_rows=0,
                updated_rows=0,
                deleted_rows=0,
                rejected_rows=0,
                status=STATUS_SUCCESS_NO_CHANGE,
                start_time=start_time,
                end_time=end_time,
            )

            return 0

        logger.info(
            f"{object_name}: Updating {expected_rows} record(s)..."
        )

        conn.execute(sql, params)

        logger.info(
            f"{object_name}: Successfully updated {expected_rows} record(s)."
        )

        end_time = datetime.now()

        write_object_audit(
            conn=conn,
            load_id=load_id,
            object_name=object_name,
            inserted_rows=0,
            updated_rows=expected_rows,
            deleted_rows=0,
            rejected_rows=0,
            status=STATUS_SUCCESS,
            start_time=start_time,
            end_time=end_time,
        )

        return expected_rows

    except Exception as ex:

        end_time = datetime.now()

        write_object_audit(
            conn=conn,
            load_id=load_id,
            object_name=object_name,
            inserted_rows=0,
            updated_rows=0,
            deleted_rows=0,
            rejected_rows=0,
            status=STATUS_FAILED,
            start_time=start_time,
            end_time=end_time,
            error_message=str(ex),
        )

        logger.exception(f"{object_name}: Update failed.")

        raise