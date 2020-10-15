-- Jira Issue: MCAL-76
-- Developer: RyanSpringer 
-- Database: CORE Schema: mcal
-- Comments:  Sql will also remove any scheduled maintenances on calendar if rollback is executed.  

\connect - core_write

BEGIN;

create temp table foo (id int, scheduled_maintenance_id int);

insert into foo (id,scheduled_maintenance_id)
SELECT id,scheduled_maintenance_id
  FROM mcal.scheduled_service
  where scheduled_maintenance_id in 
  (select scheduled_maintenance_id from mcal.scheduled_service where calendar_id = 20);  --Managed Storage DAS is 20.
  
insert into foo (id,scheduled_maintenance_id)
SELECT id,scheduled_maintenance_id
  FROM mcal.scheduled_service
  where scheduled_maintenance_id in 
  (select scheduled_maintenance_id from mcal.scheduled_service where calendar_id = 21);  --Managed Storage NAS is 21.
  

Delete from mcal.xref_scheduled_service_server_list
 where scheduled_service_id in (select id from foo);

Delete from mcal.scheduled_service
 where id in (select id from foo);

Delete from mcal.scheduled_maintenance
 where id in (select distinct scheduled_maintenance_id from foo);

-- is it necessary to rename this calendar?
update mcal.calendar
set name='Managed Storage',description='Managed Storage Maintenance Calendar'
where mcal.calendar.id = 15;

Delete from mcal.calendar_selector
 where calendar_id = 20;
 
Delete from mcal.times_available
 where calendar_id = 20;

Delete from mcal.calendar
 where id = 20;
 

Delete from mcal.calendar_selector
 where calendar_id = 21;
 
Delete from mcal.times_available
 where calendar_id = 21;

Delete from mcal.calendar
 where id = 21;
 
 
Delete from mcal.calendar_selector
 where managed_storage_type = 'SAN';
 

drop table foo;

ALTER TABLE mcal.server_cache
	DROP managed_storage_type;
        
ALTER TABLE mcal.server_cache
	DROP attached_devices;

ALTER TABLE mcal.calendar_selector
	DROP managed_storage_type;

insert into mcal.calendar_selector
(id,calendar_id,category,has_managed_storage)
values (default,15,2,'TRUE');

insert into mcal.calendar_selector
(id,calendar_id,category,has_managed_storage)
values (default,15,4,'TRUE');

commit;


