from src.common.config import config
from src.dq.dq_utils import execute_dq_rule


def run_dim_release_dq(conn, load_id, logger):
    """
    Executes Data Quality checks for DIM_RELEASE.
    """

    logger.info("=" * 50)
    logger.info("Running DQ Checks - DIM_RELEASE")
    logger.info("=" * 50)

    dim_table = (
        f"{config.silver_schema}."
        f"{config.dim_release_table}"
    )

    # ============================================================
    # RULE 1
    # Duplicate Release MSID
    # ============================================================

    duplicate_release_msid_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT release_msid
        FROM {dim_table}
        WHERE release_key <> 0
        GROUP BY release_msid
        HAVING COUNT(*) > 1
    );
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RELEASE",
        rule_name="Duplicate Release MSID",
        sql=duplicate_release_msid_sql,
    )

    # ============================================================
    # RULE 2
    # Null Release MSID
    # ============================================================

    null_release_msid_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE release_key <> 0
      AND release_msid IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RELEASE",
        rule_name="Null Release MSID",
        sql=null_release_msid_sql,
    )

    # ============================================================
    # RULE 3
    # Blank Release MSID
    # ============================================================

    blank_release_msid_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE release_key <> 0
      AND TRIM(release_msid) = '';
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RELEASE",
        rule_name="Blank Release MSID",
        sql=blank_release_msid_sql,
    )

    # ============================================================
    # RULE 4
    # Null Release Name
    # ============================================================

    null_release_name_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE release_key <> 0
      AND release_name IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RELEASE",
        rule_name="Null Release Name",
        sql=null_release_name_sql,
    )

    # ============================================================
    # RULE 5
    # Blank Release Name
    # ============================================================

    blank_release_name_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE release_key <> 0
      AND TRIM(release_name) = '';
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RELEASE",
        rule_name="Blank Release Name",
        sql=blank_release_name_sql,
    )

    logger.info("DIM_RELEASE DQ checks completed successfully.")