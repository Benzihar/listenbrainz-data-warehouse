from src.dq.dq_dim_date import run_dim_date_dq
from src.dq.dq_dim_user import run_dim_user_dq
from src.dq.dq_dim_artist import run_dim_artist_dq
from src.dq.dq_dim_release import run_dim_release_dq
from src.dq.dq_dim_recording import run_dim_recording_dq
from src.dq.dq_fact_listen import run_fact_listen_dq


def run_dq_checks(conn, load_id, logger):
    """
    Executes all Data Quality checks.
    """

    logger.info("=" * 80)
    logger.info("Starting Data Quality Framework")
    logger.info("=" * 80)

    # ============================================================
    # DIM_DATE
    # ============================================================

    run_dim_date_dq(
        conn=conn,
        load_id=load_id,
        logger=logger
    )

    # ============================================================
    # DIM_USER
    # ============================================================

    run_dim_user_dq(
        conn=conn,
        load_id=load_id,
        logger=logger
    )

    # ============================================================
    # DIM_ARTIST
    # ============================================================

    run_dim_artist_dq(
        conn=conn,
        load_id=load_id,
        logger=logger
    )

    # ============================================================
    # DIM_RELEASE
    # ============================================================

    run_dim_release_dq(
        conn=conn,
        load_id=load_id,
        logger=logger
    )

    # ============================================================
    # DIM_RECORDING
    # ============================================================

    run_dim_recording_dq(
        conn=conn,
        load_id=load_id,
        logger=logger
    )

    # ============================================================
    # FACT_LISTEN
    # ============================================================

    run_fact_listen_dq(
        conn=conn,
        load_id=load_id,
        logger=logger
    )

    logger.info("=" * 80)
    logger.info("Data Quality Framework completed successfully.")
    logger.info("=" * 80)