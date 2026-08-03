from src.common.config import config


def create_gold_views(conn, logger):
    """
    Creates all Gold Layer semantic and reporting views.
    """

    logger.info("=" * 50)
    logger.info("Creating Gold Layer Views")
    logger.info("=" * 50)

    fact_table = (
        f"{config.silver_schema}."
        f"{config.fact_listen_table}"
    )

    date_table = (
        f"{config.silver_schema}."
        f"{config.dim_date_table}"
    )

    user_table = (
        f"{config.silver_schema}."
        f"{config.dim_user_table}"
    )

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

    conn.execute(
        f"""
        CREATE OR REPLACE VIEW
        {config.gold_schema}.VW_LISTEN_ANALYTICS
        AS

        SELECT

        ---------------------------------------------------------
        -- FACT
        ---------------------------------------------------------

        f.fact_listen_key,

        CAST(f.listened_at AS DATE) AS listen_date,

        EXTRACT(HOUR FROM f.listened_at) AS listen_hour,

        CASE
        WHEN EXTRACT(HOUR FROM f.listened_at) BETWEEN 5 AND 11 THEN 'Morning'
        WHEN EXTRACT(HOUR FROM f.listened_at) BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN EXTRACT(HOUR FROM f.listened_at) BETWEEN 17 AND 20 THEN 'Evening'
        ELSE 'Night'
        END AS time_of_day,

        f.listened_at,

        f.listen_count,

        f.load_id,

        f.load_timestamp,

        ---------------------------------------------------------
        -- DATE
        ---------------------------------------------------------

        d.date_key,

        d.full_date,

        d.day_of_month,

        d.day_of_week,

        d.day_name,

        d.week_of_year,

        d.month_number,

        d.month_name,

        d.quarter_number,

        d.year_number,

        d.is_weekend,

        CASE
            WHEN d.is_weekend
            THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,

        ---------------------------------------------------------
        -- USER
        ---------------------------------------------------------

        u.user_key,

        u.user_name,

        ---------------------------------------------------------
        -- RECORDING
        ---------------------------------------------------------

        r.recording_key,

        r.recording_msid,

        r.track_name,

        ---------------------------------------------------------
        -- ARTIST
        ---------------------------------------------------------

        a.artist_key,

        a.artist_msid,

        a.artist_name,

        ---------------------------------------------------------
        -- RELEASE
        ---------------------------------------------------------

        rel.release_key,

        rel.release_msid,

        rel.release_name

        FROM {fact_table} f

        INNER JOIN {date_table} d
            ON f.date_key = d.date_key

        INNER JOIN {user_table} u
            ON f.user_key = u.user_key

        INNER JOIN {recording_table} r
            ON f.recording_key = r.recording_key

        INNER JOIN {artist_table} a
            ON r.artist_key = a.artist_key

        INNER JOIN {release_table} rel
            ON r.release_key = rel.release_key;
        """
    )

    logger.info("VW_LISTEN_ANALYTICS created successfully.")

    
    logger.info("Gold Layer Views created successfully.")

