from src.common.config import config
from src.common.etl_utils import execute_insert


def load_dim_user(conn, load_id, logger):
    """
    Load User Dimension from Bronze Layer.
    Inserts only new users (idempotent).
    """

    logger.info("=" * 50)
    logger.info("Loading User Dimension")
    logger.info("=" * 50)

    bronze_table = f"{config.bronze_schema}.{config.source_raw_table}"
    dim_table = f"{config.silver_schema}.{config.dim_user_table}"

    # ------------------------------------------------------------
    # Count new users
    # ------------------------------------------------------------
    count_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT DISTINCT
            TRIM(json_extract_string(RAW_JSON, '$.user_name')) AS USER_NAME

        FROM {bronze_table} b

        LEFT JOIN {dim_table} d
            ON TRIM(json_extract_string(b.RAW_JSON, '$.user_name')) = d.USER_NAME

        WHERE json_extract_string(b.RAW_JSON, '$.user_name') IS NOT NULL
          AND TRIM(json_extract_string(b.RAW_JSON, '$.user_name')) <> ''
          AND d.USER_NAME IS NULL
    ) src;
    """

    new_rows = conn.execute(count_sql).fetchone()[0]

    # ------------------------------------------------------------
    # Insert new users
    # ------------------------------------------------------------
    insert_sql = f"""
    INSERT INTO {dim_table}
    (
        USER_NAME,
        LOAD_ID,
        LOAD_TIMESTAMP,
        CREATED_AT,
        UPDATED_AT
    )

    SELECT
        src.USER_NAME,
        ?,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP

    FROM
    (
        SELECT DISTINCT
            TRIM(json_extract_string(RAW_JSON, '$.user_name')) AS USER_NAME

        FROM {bronze_table}

        WHERE json_extract_string(RAW_JSON, '$.user_name') IS NOT NULL
          AND TRIM(json_extract_string(RAW_JSON, '$.user_name')) <> ''
    ) src

    LEFT JOIN {dim_table} tgt
        ON src.USER_NAME = tgt.USER_NAME

    WHERE tgt.USER_NAME IS NULL;
    """

    execute_insert(
        conn=conn,
        sql=insert_sql,
        params=[load_id],
        logger=logger,
        object_name="DIM_USER",
        expected_rows=new_rows
    )

    logger.info("User Dimension loaded successfully.")