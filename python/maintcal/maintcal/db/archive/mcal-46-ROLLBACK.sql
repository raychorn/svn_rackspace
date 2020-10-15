-- Jira Issue: MCAL-46
-- Developer: Scott Gillenwater
-- Database: CORE Schema: mcal

\connect - core_write

BEGIN;

create temp table foo (id int, scheduled_maintenance_id int);

insert into foo (id,scheduled_maintenance_id)
SELECT id,scheduled_maintenance_id
  FROM mcal.scheduled_service
  where scheduled_maintenance_id in 
  (select scheduled_maintenance_id from mcal.scheduled_service where calendar_id = 18); 

Delete from mcal.xref_scheduled_service_server_list
 where scheduled_service_id in (select id from foo);

Delete from mcal.scheduled_service
 where id in (select id from foo);

Delete from mcal.scheduled_maintenance
 where id in (select distinct scheduled_maintenance_id from foo);

Delete from mcal.calendar_selector
 where calendar_id = 18;

Delete from mcal.times_available
 where calendar_id = 18;

Delete from mcal.calendar
 where id = 18;

drop table foo;

commit;


