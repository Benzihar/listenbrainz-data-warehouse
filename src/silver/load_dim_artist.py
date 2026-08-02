from src.common.config import config
from src.common.etl_utils import execute_insert, execute_update


def load_dim_artist(conn, load_id, logger):
    """
    Load Artist Dimension.

    Business Key:
        ARTIST_MSID

    SCD Strategy:
        Type 1
    """

    logger.info("=" * 50)
    logger.info("Loading Artist Dimension")
    logger.info("=" * 50)

    bronze_table = f"{config.bronze_schema}.{config.source_raw_table}"
    dim_table = f"{config.silver_schema}.{config.dim_artist_table}"

    # ============================================================
    # COMMON CTE FOR SOURCE ARTIST DATA
    # ============================================================

    src_artist_cte = f"""
    WITH src_artist AS
    (
        SELECT
            artist_msid,
            artist_name
        FROM
        (
            SELECT

                TRIM(
                    json_extract_string(
                        raw_json,
                        '$.track_metadata.additional_info.artist_msid'
                    )
                ) AS artist_msid,

                TRIM(
                    json_extract_string(
                        raw_json,
                        '$.track_metadata.artist_name'
                    )
                ) AS artist_name,

                ROW_NUMBER() OVER
                (
                    PARTITION BY
                        TRIM(
                            json_extract_string(
                                raw_json,
                                '$.track_metadata.additional_info.artist_msid'
                            )
                        )

                    ORDER BY
                        record_number DESC

                ) AS rn

            FROM {bronze_table}

            WHERE json_extract_string(
                    raw_json,
                    '$.track_metadata.additional_info.artist_msid'
                ) IS NOT NULL

            AND TRIM(
                    json_extract_string(
                        raw_json,
                        '$.track_metadata.additional_info.artist_msid'
                    )
                ) <> ''

            AND json_extract_string(
                    raw_json,
                    '$.track_metadata.artist_name'
                ) IS NOT NULL

            AND TRIM(
                    json_extract_string(
                        raw_json,
                        '$.track_metadata.artist_name'
                    )
                ) <> ''
        )

        WHERE rn = 1
    )
    """

    # ============================================================
    # COUNT CHANGED ARTISTS
    # ============================================================

    update_count_sql = f"""
    {src_artist_cte}

    SELECT COUNT(*)

    FROM src_artist src

    INNER JOIN {dim_table} d

    ON d.artist_msid = src.artist_msid

    WHERE

    LOWER(TRIM(src.artist_name))
    <>
    LOWER(TRIM(d.artist_name));
    """

    update_rows = conn.execute(update_count_sql).fetchone()[0]

    # ============================================================
    # UPDATE EXISTING ARTISTS (SCD TYPE 1)
    # ============================================================

    update_sql = f"""
    {src_artist_cte}

    UPDATE {dim_table} d

    SET
        artist_name = src.artist_name,
        updated_at = CURRENT_TIMESTAMP,
        load_id = ?,
        load_timestamp = CURRENT_TIMESTAMP

    FROM src_artist src

    WHERE
        d.artist_msid = src.artist_msid

    AND

        LOWER(TRIM(d.artist_name))
        <>
        LOWER(TRIM(src.artist_name));
    """

    execute_update(
    conn=conn,
    sql=update_sql,
    params=[load_id],
    logger=logger,
    object_name="DIM_ARTIST",
    expected_rows=update_rows
    )

    # ============================================================
    # COUNT NEW ARTISTS
    # ============================================================

    insert_count_sql = f"""
    {src_artist_cte}

    SELECT COUNT(*)

    FROM src_artist src

    LEFT JOIN {dim_table} d

    ON d.artist_msid = src.artist_msid

    WHERE d.artist_msid IS NULL;
    """

    insert_rows = conn.execute(insert_count_sql).fetchone()[0]

    # ============================================================
    # INSERT NEW ARTISTS
    # ============================================================

    insert_sql = f"""
    {src_artist_cte}

    INSERT INTO {dim_table}
    (
        artist_msid,
        artist_name,
        created_at,
        updated_at,
        load_id,
        load_timestamp
    )

    SELECT

        src.artist_msid,
        src.artist_name,
        CURRENT_TIMESTAMP,
        NULL,
        ?,
        CURRENT_TIMESTAMP

    FROM src_artist src

    LEFT JOIN {dim_table} d

    ON d.artist_msid = src.artist_msid

    WHERE d.artist_msid IS NULL;
    """

    execute_insert(
    conn=conn,
    sql=insert_sql,
    params=[load_id],
    logger=logger,
    object_name="DIM_ARTIST",
    expected_rows=insert_rows
    )

    logger.info("Artist Dimension loaded successfully.")