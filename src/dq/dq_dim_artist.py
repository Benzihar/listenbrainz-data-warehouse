from src.common.config import config
from src.dq.dq_utils import execute_dq_rule


def run_dim_artist_dq(conn, load_id, logger):
    """
    Executes Data Quality checks for DIM_ARTIST.
    """

    logger.info("=" * 50)
    logger.info("Running DQ Checks - DIM_ARTIST")
    logger.info("=" * 50)

    dim_table = (
        f"{config.silver_schema}."
        f"{config.dim_artist_table}"
    )

    # ============================================================
    # RULE 1
    # Duplicate Artist MSID
    # ============================================================

    duplicate_artist_msid_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT artist_msid
        FROM {dim_table}
        WHERE artist_key <> 0
        GROUP BY artist_msid
        HAVING COUNT(*) > 1
    );
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_ARTIST",
        rule_name="Duplicate Artist MSID",
        sql=duplicate_artist_msid_sql,
    )

    # ============================================================
    # RULE 2
    # Null Artist MSID
    # ============================================================

    null_artist_msid_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE artist_key <> 0
      AND artist_msid IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_ARTIST",
        rule_name="Null Artist MSID",
        sql=null_artist_msid_sql,
    )

    # ============================================================
    # RULE 3
    # Blank Artist MSID
    # ============================================================

    blank_artist_msid_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE artist_key <> 0
      AND TRIM(artist_msid) = '';
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_ARTIST",
        rule_name="Blank Artist MSID",
        sql=blank_artist_msid_sql,
    )

    # ============================================================
    # RULE 4
    # Null Artist Name
    # ============================================================

    null_artist_name_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE artist_key <> 0
      AND artist_name IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_ARTIST",
        rule_name="Null Artist Name",
        sql=null_artist_name_sql,
    )

    # ============================================================
    # RULE 5
    # Blank Artist Name
    # ============================================================

    blank_artist_name_sql = f"""
    SELECT COUNT(*)
    FROM {dim_table}
    WHERE artist_key <> 0
      AND TRIM(artist_name) = '';
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_ARTIST",
        rule_name="Blank Artist Name",
        sql=blank_artist_name_sql,
    )

    logger.info("DIM_ARTIST DQ checks completed successfully.")