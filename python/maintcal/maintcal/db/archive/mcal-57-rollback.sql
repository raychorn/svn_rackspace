-- Jira Issue: MCAL-57
-- Developer: Nathen Hinson
-- Database: CORE schema MCAL

\connect - core_write

begin;

ALTER TABLE mcal.calendar 
    DROP new_ticket_queue_id,
    DROP new_ticket_category_id, 
    DROP new_ticket_status_id, 
    DROP time_before_ticket_refresh, 
    DROP refresh_ticket_assignment,
    DROP refresh_ticket_queue_id,
    DROP refresh_category_id,
    DROP refresh_status_id,
    DROP hold_tentative_time; 

commit;
