-- Jira Issue: MCAL-47
-- Developer: Scott Gillenwater
-- Database: CORE Schema: mcal

\connect - core_write

BEGIN;

ALTER TABLE mcal.server_cache
	ADD has_managed_backup BOOLEAN;

ALTER TABLE mcal.calendar_selector
	ADD has_managed_backup BOOLEAN;
COMMENT ON COLUMN mcal.calendar_selector.has_managed_backup IS 'Set if managed backup is a factor. Null will mean that it does not matter.';

insert into mcal.calendar
(id,name,description,tckt_queue_id,tckt_subcategory_id,active,bookings,timezone)
values (19,'Managed Backup','Managed Backup',138,6105,'TRUE',1,'US/Central');

insert into mcal.maintenance_category
values (8,'Managed Backup','This maintenance type includes on demand backup requests.  Managed Backup will be included in this request');

insert into mcal.service_type
values(default,'On Demand Backup','On Demand Backup', 'TRUE','0:30:00','2:00:00',1,8,default,default);

insert into mcal.calendar_selector
(id,calendar_id,category,has_managed_backup)
values (default,19,2,'TRUE');

insert into mcal.calendar_selector
(id,calendar_id,category,has_managed_backup)
values (default,19,8,'TRUE');

update "UPGD_Queue"
set "Active" = 'f'
where "Name" = 'Managed Backup';

commit;
