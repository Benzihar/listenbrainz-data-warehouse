from datetime import datetime


def generate_load_id():
    """
    Generates a unique LOAD_ID for a single ETL execution.
    """
    return int(datetime.now().strftime("%Y%m%d%H%M%S"))


def execute_insert(conn, sql, params, logger, object_name, expected_rows):
    """
    Executes an INSERT statement and logs the outcome.
    """

    if expected_rows == 0:
        logger.info(f"{object_name}: No new records found.")
        return 0

    logger.info(f"{object_name}: Inserting {expected_rows} record(s)...")

    conn.execute(sql, params)

    logger.info(f"{object_name}: Successfully inserted {expected_rows} record(s).")

    return expected_rows