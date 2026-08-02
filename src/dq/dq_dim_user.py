from src.common.config import config
from src.dq.dq_utils import execute_dq_rule


def run_dim_user_dq(conn, load_id, logger):
    """
    Executes Data Quality checks for DIM_USER.
    """

    logger.info("=" * 50)
    logger.info("Running DQ Checks - DIM_USER")
    logger.info("=" * 50)

    dim_table = (
        f"{config.silver_schema}."
        f"{config.dim_user_table}"
    )

    # ============================================================
    # RULE 1
    # Duplicate User Name
    # ============================================================

    duplicate_user_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT
            user_name
        FROM {dim_table}
        GROUP BY
            user_name
        HAVING COUNT(*) > 1
    );
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_USER",
        rule_name="Duplicate User Name",
        sql=duplicate_user_sql,
    )

    # ============================================================
    # RULE 2
    # Null User Name
    # ============================================================

    null_user_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE user_name IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_USER",
        rule_name="Null User Name",
        sql=null_user_sql,
    )

    # ============================================================
    # RULE 3
    # Blank User Name
    # ============================================================

    blank_user_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE TRIM(user_name) = '';
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_USER",
        rule_name="Blank User Name",
        sql=blank_user_sql,
    )

    logger.info("DIM_USER DQ checks completed successfully.")