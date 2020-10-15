-- Jira Issue: MCAL-29 
-- Developer: Nathen Hinson
-- Database: CORE Schema: mcal

\connect - core_write

begin;

SET search_path = mcal;

delete from mcal.blocked_time where calendar_id=6 and recurrence_id=2;

commit;

