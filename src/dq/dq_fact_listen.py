from src.common.config import config
from src.dq.dq_utils import execute_dq_rule


def run_fact_listen_dq(conn, load_id, logger):
    """
    Executes Data Quality checks for FACT_LISTEN.
    """

    logger.info("=" * 50)
    logger.info("Running DQ Checks - FACT_LISTEN")
    logger.info("=" * 50)

    fact_table = (
        f"{config.silver_schema}."
        f"{config.fact_listen_table}"
    )

    date_table = (
        f"{config.silver_schema}."
        f"{config.dim_date_table}"
    )

    user_table = (
        f"{config.silver_schema}."
        f"{config.dim_user_table}"
    )

    recording_table = (
        f"{config.silver_schema}."
        f"{config.dim_recording_table}"
    )

    # ============================================================
    # RULE 1
    # Duplicate Fact Grain
    # ============================================================

    duplicate_fact_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT
            date_key,
            user_key,
            recording_key,
            listened_at
        FROM {fact_table}
        GROUP BY
            date_key,
            user_key,
            recording_key,
            listened_at
        HAVING COUNT(*) > 1
    );
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="FACT_LISTEN",
        rule_name="Duplicate Fact Grain",
        sql=duplicate_fact_sql,
    )

    # ============================================================
    # RULE 2
    # Invalid Date Key
    # ============================================================

    invalid_date_sql = f"""
    SELECT COUNT(*)
    FROM {fact_table} f

    LEFT JOIN {date_table} d
           ON f.date_key = d.date_key

    WHERE d.date_key IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="FACT_LISTEN",
        rule_name="Invalid Date Key",
        sql=invalid_date_sql,
    )

    # ============================================================
    # RULE 3
    # Invalid User Key
    # ============================================================

    invalid_user_sql = f"""
    SELECT COUNT(*)
    FROM {fact_table} f

    LEFT JOIN {user_table} u
           ON f.user_key = u.user_key

    WHERE u.user_key IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="FACT_LISTEN",
        rule_name="Invalid User Key",
        sql=invalid_user_sql,
    )

    # ============================================================
    # RULE 4
    # Invalid Recording Key
    # ============================================================

    invalid_recording_sql = f"""
    SELECT COUNT(*)
    FROM {fact_table} f

    LEFT JOIN {recording_table} r
           ON f.recording_key = r.recording_key

    WHERE r.recording_key IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="FACT_LISTEN",
        rule_name="Invalid Recording Key",
        sql=invalid_recording_sql,
    )

    # ============================================================
    # RULE 5
    # Null Listened At
    # ============================================================

    null_listened_at_sql = f"""
    SELECT COUNT(*)
    FROM {fact_table}
    WHERE listened_at IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="FACT_LISTEN",
        rule_name="Null Listened At",
        sql=null_listened_at_sql,
    )

    # ============================================================
    # RULE 6
    # Future Listen Timestamp
    # ============================================================

    future_listened_at_sql = f"""
    SELECT COUNT(*)
    FROM {fact_table}
    WHERE listened_at > CURRENT_TIMESTAMP;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="FACT_LISTEN",
        rule_name="Future Listen Timestamp",
        sql=future_listened_at_sql,
    )

    # ============================================================
    # RULE 7
    # Invalid Listen Count
    # ============================================================

    invalid_listen_count_sql = f"""
    SELECT COUNT(*)
    FROM {fact_table}
    WHERE listen_count <= 0;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="FACT_LISTEN",
        rule_name="Invalid Listen Count",
        sql=invalid_listen_count_sql,
    )

    logger.info("FACT_LISTEN DQ checks completed successfully.")