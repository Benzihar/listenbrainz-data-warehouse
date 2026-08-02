from src.common.config import config
from src.common.etl_utils import execute_insert, execute_update


def load_dim_release(conn, load_id, logger):
    """
    Load Release Dimension.

    Business Key:
        RELEASE_MSID

    SCD Strategy:
        Type 1
    """

    logger.info("=" * 50)
    logger.info("Loading Release Dimension")
    logger.info("=" * 50)

    bronze_table = f"{config.bronze_schema}.{config.source_raw_table}"
    dim_table = f"{config.silver_schema}.{config.dim_release_table}"

    # ============================================================
    # COUNT CHANGED RELEASES
    # ============================================================

    update_count_sql = f"""
    WITH src_release AS
    (
        SELECT DISTINCT

            LOWER(TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ))) AS release_msid,

            TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            )) AS release_name

        FROM {bronze_table}

        WHERE json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ) IS NOT NULL

        AND TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            )) <> ''
    )

    SELECT COUNT(*)

    FROM src_release src

    INNER JOIN {dim_table} d

    ON src.release_msid = LOWER(TRIM(d.release_msid))

    WHERE

    LOWER(TRIM(src.release_name))
    <>
    LOWER(TRIM(d.release_name));
    """

    update_rows = conn.execute(update_count_sql).fetchone()[0]

    # ============================================================
    # UPDATE EXISTING RELEASES (SCD TYPE 1)
    # ============================================================

    update_sql = f"""
    WITH src_release AS
    (
        SELECT DISTINCT

            LOWER(TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ))) AS release_msid,

            TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            )) AS release_name

        FROM {bronze_table}

        WHERE json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ) IS NOT NULL

        AND TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            )) <> ''
    )

    UPDATE {dim_table} d

    SET
        release_name = src.release_name,
        updated_at = CURRENT_TIMESTAMP,
        load_id = ?,
        load_timestamp = CURRENT_TIMESTAMP

    FROM src_release src

    WHERE

    LOWER(TRIM(d.release_msid))
    =
    src.release_msid

    AND

    LOWER(TRIM(d.release_name))
    <>
    LOWER(TRIM(src.release_name));
    """

    execute_update(
        conn=conn,
        sql=update_sql,
        params=[load_id],
        logger=logger,
        object_name="DIM_RELEASE",
        expected_rows=update_rows
    )

    # ============================================================
    # COUNT NEW RELEASES
    # ============================================================

    insert_count_sql = f"""
    WITH src_release AS
    (
        SELECT DISTINCT

            LOWER(TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ))) AS release_msid,

            TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            )) AS release_name

        FROM {bronze_table}

        WHERE json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ) IS NOT NULL

        AND TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            )) <> ''

        AND json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            ) IS NOT NULL

        AND TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            )) <> ''
    )

    SELECT COUNT(*)

    FROM src_release src

    LEFT JOIN {dim_table} d

    ON src.release_msid =
    LOWER(TRIM(d.release_msid))

    WHERE d.release_msid IS NULL;
    """

    insert_rows = conn.execute(insert_count_sql).fetchone()[0]

    # ============================================================
    # INSERT NEW RELEASES
    # ============================================================

    insert_sql = f"""
    WITH src_release AS
    (
        SELECT DISTINCT

            LOWER(TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ))) AS release_msid,

            TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            )) AS release_name

        FROM {bronze_table}

        WHERE json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            ) IS NOT NULL

        AND TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.additional_info.release_msid'
            )) <> ''

        AND json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            ) IS NOT NULL

        AND TRIM(json_extract_string(
                raw_json,
                '$.track_metadata.release_name'
            )) <> ''
    )

    INSERT INTO {dim_table}
    (
        release_msid,
        release_name,
        created_at,
        updated_at,
        load_id,
        load_timestamp
    )

    SELECT

        src.release_msid,
        src.release_name,
        CURRENT_TIMESTAMP,
        NULL,
        ?,
        CURRENT_TIMESTAMP

    FROM src_release src

    LEFT JOIN {dim_table} d

    ON src.release_msid =
    LOWER(TRIM(d.release_msid))

    WHERE d.release_msid IS NULL;
    """

    execute_insert(
        conn=conn,
        sql=insert_sql,
        params=[load_id],
        logger=logger,
        object_name="DIM_RELEASE",
        expected_rows=insert_rows
    )

    logger.info("Release Dimension loaded successfully.")