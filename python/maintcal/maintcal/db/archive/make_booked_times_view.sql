-- Jira issue: MCAL-99
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson
-- Database: CORE
-- Schema : mcal

SET 
    role 
        TO postgres;

BEGIN;

    CREATE VIEW mcal.booked_times AS

            SELECT
                bt.id::text || '-bt'    AS id,
                bt.start_time           AS start_time,
                bt.end_time             AS end_time,
                bt.bookings             AS bookings,
                bt.calendar_id          AS calendar_id

            FROM
                mcal.blocked_time       AS bt

            WHERE
                    bt.start_time       IS NOT  NULL
                AND bt.end_time         >=      now()

        UNION

            SELECT
                ss.id::text || '-ss'    AS id,
                ss.start_time           AS start_time,
                ss.end_time             AS end_time,
                1                       AS bookings,
                ss.calendar_id          AS calendar_id

            FROM
                mcal.scheduled_service  AS ss

            WHERE
                    ss.start_time       IS NOT  NULL
                AND ss.end_time         >=      now()

            ORDER BY
                calendar_id,
                start_time;

    -- GRANTS

    GRANT
        SELECT
            ON mcal.booked_times
            TO core_write;

COMMIT;
