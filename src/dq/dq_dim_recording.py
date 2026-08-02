from src.common.config import config
from src.dq.dq_utils import execute_dq_rule


def run_dim_recording_dq(conn, load_id, logger):
    """
    Executes Data Quality checks for DIM_RECORDING.
    """

    logger.info("=" * 50)
    logger.info("Running DQ Checks - DIM_RECORDING")
    logger.info("=" * 50)

    recording_table = (
        f"{config.silver_schema}."
        f"{config.dim_recording_table}"
    )

    artist_table = (
        f"{config.silver_schema}."
        f"{config.dim_artist_table}"
    )

    release_table = (
        f"{config.silver_schema}."
        f"{config.dim_release_table}"
    )

    # ============================================================
    # RULE 1
    # Duplicate Recording MSID
    # ============================================================

    duplicate_recording_msid_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT recording_msid
        FROM {recording_table}
        WHERE recording_key <> 0
        GROUP BY recording_msid
        HAVING COUNT(*) > 1
    );
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RECORDING",
        rule_name="Duplicate Recording MSID",
        sql=duplicate_recording_msid_sql,
    )

    # ============================================================
    # RULE 2
    # Null Recording MSID
    # ============================================================

    null_recording_msid_sql = f"""
    SELECT COUNT(*)
    FROM {recording_table}
    WHERE recording_key <> 0
      AND recording_msid IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RECORDING",
        rule_name="Null Recording MSID",
        sql=null_recording_msid_sql,
    )

    # ============================================================
    # RULE 3
    # Blank Recording MSID
    # ============================================================

    blank_recording_msid_sql = f"""
    SELECT COUNT(*)
    FROM {recording_table}
    WHERE recording_key <> 0
      AND TRIM(recording_msid) = '';
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RECORDING",
        rule_name="Blank Recording MSID",
        sql=blank_recording_msid_sql,
    )

    # ============================================================
    # RULE 4
    # Null Track Name
    # ============================================================

    null_track_name_sql = f"""
    SELECT COUNT(*)
    FROM {recording_table}
    WHERE recording_key <> 0
      AND track_name IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RECORDING",
        rule_name="Null Track Name",
        sql=null_track_name_sql,
    )

    # ============================================================
    # RULE 5
    # Blank Track Name
    # ============================================================

    blank_track_name_sql = f"""
    SELECT COUNT(*)
    FROM {recording_table}
    WHERE recording_key <> 0
      AND TRIM(track_name) = '';
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RECORDING",
        rule_name="Blank Track Name",
        sql=blank_track_name_sql,
    )

    # ============================================================
    # RULE 6
    # Invalid Artist Key
    # ============================================================

    invalid_artist_key_sql = f"""
    SELECT COUNT(*)
    FROM {recording_table} r

    LEFT JOIN {artist_table} a
           ON r.artist_key = a.artist_key

    WHERE r.recording_key <> 0
      AND a.artist_key IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RECORDING",
        rule_name="Invalid Artist Key",
        sql=invalid_artist_key_sql,
    )

    # ============================================================
    # RULE 7
    # Invalid Release Key
    # ============================================================

    invalid_release_key_sql = f"""
    SELECT COUNT(*)
    FROM {recording_table} r

    LEFT JOIN {release_table} rel
           ON r.release_key = rel.release_key

    WHERE r.recording_key <> 0
      AND rel.release_key IS NULL;
    """

    execute_dq_rule(
        conn=conn,
        load_id=load_id,
        logger=logger,
        object_name="DIM_RECORDING",
        rule_name="Invalid Release Key",
        sql=invalid_release_key_sql,
    )

    logger.info("DIM_RECORDING DQ checks completed successfully.")