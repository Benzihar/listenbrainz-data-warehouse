-- ============================================================
-- Question A1
-- Who are the Top 10 users with respect to number of songs listened?
-- ============================================================

SELECT

    user_name,

    SUM(listen_count) AS total_listens

FROM GLD_300_PL.VW_LISTEN_ANALYTICS

WHERE full_date
BETWEEN DATE '${from_date}'
    AND DATE '${to_date}'

GROUP BY

    user_name

ORDER BY

    total_listens DESC

LIMIT ${top_n};

-- ============================================================
-- Question A2
-- How many users listened to some song during the selected period?
-- ============================================================

SELECT

    COUNT(DISTINCT user_key) AS total_users

FROM GLD_300_PL.VW_LISTEN_ANALYTICS

WHERE full_date
BETWEEN DATE '${from_date}'
    AND DATE '${to_date}';

-- ============================================================
-- Question A3
-- For every user, what was the first song the user listened to?
-- ============================================================

SELECT

    user_name,

    track_name,

    listened_at

FROM
(
    SELECT

        user_name,

        track_name,

        listened_at,

        ROW_NUMBER() OVER
        (
            PARTITION BY user_key
            ORDER BY listened_at
        ) rn

    FROM GLD_300_PL.VW_LISTEN_ANALYTICS

    WHERE full_date
    BETWEEN DATE '${from_date}'
        AND DATE '${to_date}'
)

WHERE rn = 1

ORDER BY

    user_name;
	
-- ============================================================
-- Question B
-- Top 3 listening days for every user
-- ============================================================

WITH ranked_days AS
(
    SELECT

        user_name,

        full_date,

        SUM(listen_count) AS number_of_listens,

        ROW_NUMBER() OVER
        (
            PARTITION BY user_key
            ORDER BY
                SUM(listen_count) DESC,
                full_date
        ) AS row_num

    FROM GLD_300_PL.VW_LISTEN_ANALYTICS

    WHERE full_date
    BETWEEN DATE '${from_date}'
        AND DATE '${to_date}'

    GROUP BY

        user_key,
        user_name,
        full_date
)

SELECT

    user_name AS user,

    number_of_listens,

    full_date AS date

FROM ranked_days

WHERE row_num <= '${top_days}'

ORDER BY

    user_name,

    number_of_listens DESC,

    full_date;
	
-- ==============================================================================
-- Question C
-- Daily Active Users (Rolling 7-Day Window)
-- ==============================================================================

WITH user_inception AS
(
    SELECT

        user_key,

        MIN(full_date) AS first_listen_date

    FROM GLD_300_PL.VW_LISTEN_ANALYTICS

    GROUP BY

        user_key
),

running_user_base AS
(
    SELECT

        d.full_date,

        COUNT(ui.user_key) AS total_users

    FROM SIL_200_CL.DIM_DATE d

    LEFT JOIN user_inception ui

        ON ui.first_listen_date <= d.full_date

    WHERE d.full_date
    BETWEEN DATE '${from_date}'
        AND DATE '${to_date}'

    GROUP BY

        d.full_date
),

active_users AS
(
    SELECT

        d.full_date,

        COUNT(DISTINCT v.user_key) AS number_active_users

    FROM SIL_200_CL.DIM_DATE d

    LEFT JOIN GLD_300_PL.VW_LISTEN_ANALYTICS v

        ON v.full_date
        BETWEEN d.full_date - INTERVAL '${interval_days}' DAY
            AND d.full_date

    WHERE d.full_date
    BETWEEN DATE '${from_date}'
        AND DATE '${to_date}'

    GROUP BY

        d.full_date
)

SELECT

    a.full_date AS date,

    a.number_active_users,

    --r.total_users,

    ROUND
    (
        a.number_active_users * 100.0
        / NULLIF(r.total_users,0),
        2
    ) AS percentage_active_users

FROM active_users a

INNER JOIN running_user_base r

    ON a.full_date = r.full_date

ORDER BY

    a.full_date;