-- Jira Issue: MCAL-47
-- Developer: Scott Gillenwater
-- Database: CORE Schema: mcal
-- Comments:  Sql will also remove any scheduled maintenances on calendar if rollback is executed.  

\connect - core_write

BEGIN;

create temp table foo (id int, scheduled_maintenance_id int);

insert into foo (id,scheduled_maintenance_id)
SELECT id,scheduled_maintenance_id
  FROM mcal.scheduled_service
  where scheduled_maintenance_id in 
  (select scheduled_maintenance_id from mcal.scheduled_service where calendar_id = 19);  --Managed Backup calendar is 19.

Delete from mcal.xref_scheduled_service_server_list
 where scheduled_service_id in (select id from foo);

Delete from mcal.scheduled_service
 where id in (select id from foo);

Delete from mcal.scheduled_maintenance
 where id in (select distinct scheduled_maintenance_id from foo);

Delete from mcal.service_type
where maintenance_category_id = 8; -- delete all service_types that are in category of Managed Backup

Delete from mcal.maintenance_category
where id = 8; --Managed Backup id is 8

Delete from mcal.calendar_selector
 where calendar_id = 19;

Delete from mcal.times_available
 where calendar_id = 19;

Delete from mcal.calendar
 where id = 19;

drop table foo;

ALTER TABLE mcal.server_cache
	DROP has_managed_backup;

ALTER TABLE mcal.calendar_selector
	DROP has_managed_backup;

update "UPGD_Queue"
set "Active" = 't'
where "Name" = 'Managed Backup';

commit;


