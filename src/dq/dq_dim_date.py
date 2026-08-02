from src.common.config import config
from src.dq.dq_utils import execute_dq_rule


def run_dim_date_dq(conn, load_id, logger):
    """
    Executes Data Quality checks for DIM_DATE.
    """

    logger.info("=" * 50)
    logger.info("Running DQ Checks - DIM_DATE")
    logger.info("=" * 50)

    dim_table = (
        f"{config.silver_schema}."
        f"{config.dim_date_table}"
    )

    # ============================================================
    # RULE 1
    # Duplicate Date Key
    # ============================================================

    duplicate_date_key_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT
            date_key
        FROM {dim_table}
        GROUP BY
            date_key
        HAVING COUNT(*) > 1
    );
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_DATE",
        rule_name="Duplicate Date Key",
        sql=duplicate_date_key_sql,
    )

    # ============================================================
    # RULE 2
    # Duplicate Full Date
    # ============================================================

    duplicate_full_date_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT
            full_date
        FROM {dim_table}
        GROUP BY
            full_date
        HAVING COUNT(*) > 1
    );
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_DATE",
        rule_name="Duplicate Full Date",
        sql=duplicate_full_date_sql,
    )

    # ============================================================
    # RULE 3
    # Null Full Date
    # ============================================================

    null_full_date_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE full_date IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_DATE",
        rule_name="Null Full Date",
        sql=null_full_date_sql,
    )

    logger.info("DIM_DATE DQ checks completed successfully.")