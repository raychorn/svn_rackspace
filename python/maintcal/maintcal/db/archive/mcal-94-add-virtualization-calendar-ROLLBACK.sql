-- Jira Issue: MCAL-94
-- Developer: Nathen Hinson
-- Database: CORE Schema: mcal
-- Comments:  Sql will also remove any scheduled maintenances on calendar if rollback is executed.

\connect - core_write

BEGIN;

CREATE TEMP TABLE mcal_94_tmp (id int, scheduled_maintenance_id int);

INSERT INTO mcal_94_tmp (id,scheduled_maintenance_id)
SELECT id,scheduled_maintenance_id
  FROM mcal.scheduled_service
  WHERE scheduled_maintenance_id IN 
  (SELECT scheduled_maintenance_id FROM mcal.scheduled_service WHERE calendar_id = 22);  -- Virtualization calendar is 22.

DELETE FROM mcal.xref_scheduled_service_server_list
 WHERE scheduled_service_id IN (SELECT id from mcal_94_tmp);

DELETE FROM mcal.scheduled_service
 WHERE id IN (SELECT id FROM mcal_94_tmp);

DELETE FROM mcal.scheduled_maintenance
 WHERE id IN (SELECT DISTINCT scheduled_maintenance_id FROM mcal_94_tmp);

DELETE FROM mcal.calendar_selector
    WHERE mcal.calendar_selector.calendar_id = 22;

DELETE FROM mcal.times_available
 where calendar_id = 22;

DELETE from mcal.calendar
 where id = 22;

DROP TABLE mcal_94_tmp;

ALTER TABLE mcal.server_cache
	DROP is_virtual_machine,
        DROP is_hypervisor;

ALTER TABLE mcal.calendar_selector
	DROP is_virtual_machine,
        DROP is_hypervisor;

-- Activate old Virtualization calendar
UPDATE "UPGD_Queue" SET "Active" = 't'
    WHERE "UPGD_QueueID" = 38;

COMMIT;



