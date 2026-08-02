from datetime import datetime
from src.common.config import config


def write_dq_result(
    conn,
    load_id,
    object_name,
    rule_name,
    failed_rows,
    status,
    start_time,
    end_time,
    error_message=None,
):
    """
    Writes one Data Quality audit record.
    """

    processing_time_seconds = (
        end_time - start_time
    ).total_seconds()

    dq_table = (
        f"{config.audit_schema}.{config.dq_results_table}"
    )

    sql = f"""
    INSERT INTO {dq_table}
    (
        load_id,
        object_name,
        rule_name,
        failed_rows,
        status,
        start_time,
        end_time,
        processing_time_seconds,
        error_message
    )
    VALUES
    (
        ?, ?, ?, ?, ?, ?, ?, ?, ?
    );
    """

    conn.execute(
        sql,
        [
            load_id,
            object_name,
            rule_name,
            failed_rows,
            status,
            start_time,
            end_time,
            processing_time_seconds,
            error_message,
        ],
    )


def execute_dq_rule(
    conn,
    load_id,
    logger,
    object_name,
    rule_name,
    sql,
):
    """
    Executes one Data Quality rule.

    The SQL must return a single value:
        COUNT(*) of failed records.
    """

    start_time = datetime.now()

    try:

        failed_rows = conn.execute(sql).fetchone()[0]

        end_time = datetime.now()

        if failed_rows == 0:

            status = "PASS"

            logger.info(
                f"{object_name} | {rule_name} : PASS"
            )

        else:

            status = "FAIL"

            logger.warning(
                f"{object_name} | {rule_name} : "
                f"{failed_rows} failed record(s)"
            )

        write_dq_result(
            conn=conn,
            load_id=load_id,
            object_name=object_name,
            rule_name=rule_name,
            failed_rows=failed_rows,
            status=status,
            start_time=start_time,
            end_time=end_time,
        )

        return failed_rows

    except Exception as ex:

        end_time = datetime.now()

        logger.exception(
            f"{object_name} | {rule_name} : ERROR"
        )

        write_dq_result(
            conn=conn,
            load_id=load_id,
            object_name=object_name,
            rule_name=rule_name,
            failed_rows=0,
            status="ERROR",
            start_time=start_time,
            end_time=end_time,
            error_message=str(ex),
        )

        raise