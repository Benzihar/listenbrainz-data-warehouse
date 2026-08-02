from src.common.config import config
from src.common.etl_utils import execute_insert


def load_dim_date(conn, load_id, logger):
    """
    Load Date Dimension.

    Business Key:
        DATE_KEY

    Loading Strategy:
        Incremental

    Notes:
        - Generates a calendar using DuckDB generate_series().
        - Inserts only missing dates.
        - Existing dates are never updated.
    """

    logger.info("=" * 50)
    logger.info("Loading Date Dimension")
    logger.info("=" * 50)

    dim_table = f"{config.silver_schema}.{config.dim_date_table}"

    # ------------------------------------------------------------
    # Count Missing Dates
    # ------------------------------------------------------------

    count_sql = f"""
    SELECT COUNT(*)
    FROM
    (
        SELECT
            CAST(strftime(dt,'%Y%m%d') AS INTEGER) AS DATE_KEY

        FROM generate_series(
                DATE '{config.dim_date_start}',
                DATE '{config.dim_date_end}',
                INTERVAL 1 DAY
             ) t(dt)
    ) src

    LEFT JOIN {dim_table} tgt
        ON src.DATE_KEY = tgt.DATE_KEY

    WHERE tgt.DATE_KEY IS NULL;
    """

    new_rows = conn.execute(count_sql).fetchone()[0]

    # ------------------------------------------------------------
    # Insert Missing Dates
    # ------------------------------------------------------------

    insert_sql = f"""
    INSERT INTO {dim_table}
    (
        DATE_KEY,
        FULL_DATE,
        DAY_OF_MONTH,
        DAY_OF_WEEK,
        DAY_NAME,
        WEEK_OF_YEAR,
        MONTH_NUMBER,
        MONTH_NAME,
        QUARTER_NUMBER,
        YEAR_NUMBER,
        IS_WEEKEND,
        CREATED_AT,
        UPDATED_AT,
        LOAD_ID,
        LOAD_TIMESTAMP
    )

    SELECT
        src.DATE_KEY,
        src.FULL_DATE,
        src.DAY_OF_MONTH,
        src.DAY_OF_WEEK,
        src.DAY_NAME,
        src.WEEK_OF_YEAR,
        src.MONTH_NUMBER,
        src.MONTH_NAME,
        src.QUARTER_NUMBER,
        src.YEAR_NUMBER,
        src.IS_WEEKEND,
        CURRENT_TIMESTAMP,
        NULL,
        ?,
        CURRENT_TIMESTAMP

    FROM
    (
        SELECT

            CAST(strftime(dt,'%Y%m%d') AS INTEGER) AS DATE_KEY,

            dt AS FULL_DATE,

            EXTRACT(DAY FROM dt) AS DAY_OF_MONTH,

            CASE
                WHEN EXTRACT(DOW FROM dt) = 0 THEN 7
                ELSE EXTRACT(DOW FROM dt)
            END AS DAY_OF_WEEK,

            strftime(dt,'%A') AS DAY_NAME,

            EXTRACT(WEEK FROM dt) AS WEEK_OF_YEAR,

            EXTRACT(MONTH FROM dt) AS MONTH_NUMBER,

            strftime(dt,'%B') AS MONTH_NAME,

            EXTRACT(QUARTER FROM dt) AS QUARTER_NUMBER,

            EXTRACT(YEAR FROM dt) AS YEAR_NUMBER,

            CASE
                WHEN EXTRACT(DOW FROM dt) IN (0,6)
                THEN TRUE
                ELSE FALSE
            END AS IS_WEEKEND

        FROM generate_series(
                DATE '{config.dim_date_start}',
                DATE '{config.dim_date_end}',
                INTERVAL 1 DAY
             ) t(dt)

    ) src

    LEFT JOIN {dim_table} tgt
        ON src.DATE_KEY = tgt.DATE_KEY

    WHERE tgt.DATE_KEY IS NULL;
    """

    execute_insert(
        conn=conn,
        sql=insert_sql,
        params=[load_id],
        logger=logger,
        object_name="DIM_DATE",
        expected_rows=new_rows,
        load_id=load_id
    )

    logger.info("Date Dimension loaded successfully.")