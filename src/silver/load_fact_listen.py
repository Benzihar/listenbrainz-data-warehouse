from src.common.config import config
from src.common.etl_utils import execute_insert


def load_fact_listen(conn, load_id, logger):
    """
    Load Listen Fact.

    Grain:
        One row per user listen event.

    Business Key:
        user_key
        recording_key
        listened_at

    Strategy:
        Insert Only (Idempotent)
    """

    logger.info("=" * 50)
    logger.info("Loading Listen Fact")
    logger.info("=" * 50)

    bronze_table = f"{config.bronze_schema}.{config.source_raw_table}"

    fact_table = f"{config.silver_schema}.{config.fact_listen_table}"

    user_table = f"{config.silver_schema}.{config.dim_user_table}"

    recording_table = f"{config.silver_schema}.{config.dim_recording_table}"

    date_table = f"{config.silver_schema}.{config.dim_date_table}"

    # ============================================================
    # SOURCE FACT CTE
    # ============================================================

    src_fact_cte = f"""
    WITH src_base AS
    (
        SELECT

            TRIM(
                json_extract_string(
                    raw_json,
                    '$.user_name'
                )
            ) AS user_name,

            TRIM(
                json_extract_string(
                    raw_json,
                    '$.track_metadata.additional_info.recording_msid'
                )
            ) AS recording_msid,

            TO_TIMESTAMP
            (
                CAST
                (
                    json_extract_string(
                        raw_json,
                        '$.listened_at'
                    ) AS BIGINT
                )
            ) AS listened_at

        FROM {bronze_table}
    ),

    src_fact AS
    (
        SELECT

            d.date_key,

            u.user_key,

            COALESCE(r.recording_key, 0) AS recording_key,

            b.listened_at

        FROM src_base b

        INNER JOIN {user_table} u

            ON b.user_name = u.user_name

        INNER JOIN {date_table} d

        ON d.full_date = CAST(b.listened_at AS DATE)

        LEFT JOIN {recording_table} r

            ON b.recording_msid = r.recording_msid
    )
    """
    # ============================================================
    # COUNT NEW FACT RECORDS
    # ============================================================

    insert_count_sql = f"""
    {src_fact_cte}

    SELECT COUNT(*)

    FROM src_fact src

    LEFT JOIN {fact_table} f

    ON

        src.user_key = f.user_key

    AND

        src.recording_key = f.recording_key

    AND

        src.listened_at = f.listened_at

    WHERE

        f.fact_listen_key IS NULL;
    """

    insert_rows = conn.execute(insert_count_sql).fetchone()[0]

    # ============================================================
    # INSERT NEW FACT RECORDS
    # ============================================================

    insert_sql = f"""
    {src_fact_cte}

    INSERT INTO {fact_table}
    (
        date_key,
        user_key,
        recording_key,
        listened_at,
        listen_count,
        load_id,
        load_timestamp
    )

    SELECT

        src.date_key,

        src.user_key,

        src.recording_key,

        src.listened_at,

        1,

        ?,

        CURRENT_TIMESTAMP

    FROM src_fact src

    LEFT JOIN {fact_table} f

    ON

        src.user_key = f.user_key

    AND

        src.recording_key = f.recording_key

    AND

        src.listened_at = f.listened_at

    WHERE

        f.fact_listen_key IS NULL;
    """

    execute_insert(
    conn=conn,
    sql=insert_sql,
    params=[load_id],
    logger=logger,
    object_name="FACT_LISTEN",
    expected_rows=insert_rows,
    load_id=load_id
    )

    logger.info("Listen Fact loaded successfully.")

    