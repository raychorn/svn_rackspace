-- Jira Issue: MCAL-76
-- Developer: Ryan Springer 
-- Database: CORE Schema: mcal

\connect - core_write

BEGIN;

insert into mcal.calendar
(id,name,description,tckt_queue_id,active,bookings,timezone)
values (20,'Managed Storage DAS','Managed Storage DAS',130,'TRUE',1,'US/Central');

insert into mcal.calendar
(id,name,description,tckt_queue_id,active,bookings,timezone)
values (21,'Managed Storage NAS','Managed Storage NAS',175,'TRUE',1,'US/Central');

-- is it necessary to rename this calendar?
update mcal.calendar
set name='Managed Storage SAN',description='Managed Storage SAN'
where mcal.calendar.id = 15;

ALTER TABLE mcal.server_cache
	ADD managed_storage_type text;
COMMENT ON COLUMN mcal.server_cache.managed_storage_type IS 'A list of Managed Storage Types for this server.';

ALTER TABLE mcal.server_cache
	ADD attached_devices text;
COMMENT ON COLUMN mcal.server_cache.attached_devices IS 'A list of Device Ids attached to this server.';

ALTER TABLE mcal.calendar_selector
	ADD managed_storage_type text;
COMMENT ON COLUMN mcal.calendar_selector.managed_storage_type IS 'Type of Managed Storage to match against.';

delete from mcal.calendar_selector
where calendar_id=15 and category=2;

delete from mcal.calendar_selector
where calendar_id=15 and category=4;

insert into mcal.calendar_selector
(id,calendar_id,managed_storage_type)
values (default,15,'SAN');

insert into mcal.calendar_selector
(id,calendar_id,managed_storage_type)
values (default,20,'DAS');

insert into mcal.calendar_selector
(id,calendar_id,managed_storage_type)
values (default,21,'NAS');

commit;
