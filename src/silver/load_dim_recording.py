from src.common.config import config
from src.common.etl_utils import execute_insert, execute_update


def load_dim_recording(conn, load_id, logger):
    """
    Load Recording Dimension.

    Business Key:
        RECORDING_MSID

    SCD Strategy:
        Type 1
    """

    logger.info("=" * 50)
    logger.info("Loading Recording Dimension")
    logger.info("=" * 50)

    bronze_table = f"{config.bronze_schema}.{config.source_raw_table}"
    dim_table = f"{config.silver_schema}.{config.dim_recording_table}"

    artist_table = f"{config.silver_schema}.{config.dim_artist_table}"
    release_table = f"{config.silver_schema}.{config.dim_release_table}"

    # ============================================================
    # COMMON CTE FOR SOURCE RELEASE DATA
    # ============================================================

    src_recording_cte = f"""
    WITH src_recording AS
    (
        SELECT
            recording_msid,
            track_name,
            artist_key,
            release_key

        FROM
        (
            SELECT

                TRIM(
                    json_extract_string(
                        b.raw_json,
                        '$.track_metadata.additional_info.recording_msid'
                    )
                ) AS recording_msid,

                TRIM(
                    json_extract_string(
                        b.raw_json,
                        '$.track_metadata.track_name'
                    )
                ) AS track_name,

                a.artist_key,

                r.release_key,

                ROW_NUMBER() OVER
                (
                    PARTITION BY

                        TRIM(
                            json_extract_string(
                                b.raw_json,
                                '$.track_metadata.additional_info.recording_msid'
                            )
                        )

                    ORDER BY
                        CAST(json_extract_string(b.raw_json,'$.listened_at') AS BIGINT) DESC,
                        b.record_number DESC

                ) AS rn

            FROM {bronze_table} b

            LEFT JOIN {artist_table} a

                ON
                TRIM(
                    json_extract_string(
                        b.raw_json,
                        '$.track_metadata.additional_info.artist_msid'
                    )
                )
                =
                a.artist_msid

            LEFT JOIN {release_table} r

                ON
                TRIM(
                    json_extract_string(
                        b.raw_json,
                        '$.track_metadata.additional_info.release_msid'
                    )
                )
                =
                r.release_msid

            WHERE

                json_extract_string(
                    b.raw_json,
                    '$.track_metadata.additional_info.recording_msid'
                ) IS NOT NULL

            AND

                TRIM(
                    json_extract_string(
                        b.raw_json,
                        '$.track_metadata.additional_info.recording_msid'
                    )
                ) <> ''

            AND

                json_extract_string(
                    b.raw_json,
                    '$.track_metadata.track_name'
                ) IS NOT NULL

            AND

                TRIM(
                    json_extract_string(
                        b.raw_json,
                        '$.track_metadata.track_name'
                    )
                ) <> ''
        )

        WHERE rn = 1
    )
    """

    # ============================================================
    # COUNT UPDATED RECORDINGS
    # ============================================================

    update_count_sql = f"""
    {src_recording_cte}

    SELECT COUNT(*)

    FROM src_recording src

    INNER JOIN {dim_table} d

    ON d.recording_msid = src.recording_msid

    WHERE

        LOWER(TRIM(d.track_name))
        <>
        LOWER(TRIM(src.track_name))

        OR

        d.artist_key <> src.artist_key

        OR

        d.release_key <> src.release_key;
    """

    update_rows = conn.execute(update_count_sql).fetchone()[0]

        # ============================================================
    # UPDATE EXISTING RECORDINGS (SCD TYPE 1)
    # ============================================================

    update_sql = f"""
    {src_recording_cte}

    UPDATE {dim_table} d

    SET
        track_name = src.track_name,
        artist_key = src.artist_key,
        release_key = src.release_key,
        updated_at = CURRENT_TIMESTAMP,
        load_id = ?,
        load_timestamp = CURRENT_TIMESTAMP

    FROM src_recording src

    WHERE

        d.recording_msid = src.recording_msid

    AND
    (
        LOWER(TRIM(d.track_name))
        <>
        LOWER(TRIM(src.track_name))

        OR

        d.artist_key <> src.artist_key

        OR

        d.release_key <> src.release_key
    );
    """
    execute_update(
        conn=conn,
        sql=update_sql,
        params=[load_id],
        logger=logger,
        object_name="DIM_RECORDING",
        expected_rows=update_rows
    )

        # ============================================================
    # COUNT NEW RECORDINGS
    # ============================================================

    insert_count_sql = f"""
    {src_recording_cte}

    SELECT COUNT(*)

    FROM src_recording src

    LEFT JOIN {dim_table} d

    ON d.recording_msid = src.recording_msid

    WHERE d.recording_msid IS NULL;
    """

    insert_rows = conn.execute(insert_count_sql).fetchone()[0]

        # ============================================================
    # INSERT NEW RECORDINGS
    # ============================================================

    insert_sql = f"""
    {src_recording_cte}

    INSERT INTO {dim_table}
    (
        recording_msid,
        track_name,
        artist_key,
        release_key,
        created_at,
        updated_at,
        load_id,
        load_timestamp
    )

    SELECT

        src.recording_msid,
        src.track_name,
        src.artist_key,
        src.release_key,
        CURRENT_TIMESTAMP,
        NULL,
        ?,
        CURRENT_TIMESTAMP

    FROM src_recording src

    LEFT JOIN {dim_table} d

    ON d.recording_msid = src.recording_msid

    WHERE d.recording_msid IS NULL;
    """

    execute_insert(
        conn=conn,
        sql=insert_sql,
        params=[load_id],
        logger=logger,
        object_name="DIM_RECORDING",
        expected_rows=insert_rows
    )

    logger.info("Recording Dimension loaded successfully.")