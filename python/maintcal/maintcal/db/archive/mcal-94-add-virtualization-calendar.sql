-- Jira Issue: MCAL-94
-- Developer: Nathen Hinson
-- Database: CORE Schema: mcal

\connect - core_write

BEGIN;

ALTER TABLE mcal.server_cache
	ADD is_virtual_machine BOOLEAN,
        ADD is_hypervisor BOOLEAN;

ALTER TABLE mcal.calendar_selector
	ADD is_virtual_machine BOOLEAN,
        ADD is_hypervisor BOOLEAN;

INSERT INTO mcal.calendar
    (id,name,description,tckt_queue_id,active,bookings,timezone)
    VALUES (22,'Virtualization','Virtualization',136,'TRUE',1,'America/Chicago');

INSERT INTO mcal.calendar_selector
    (calendar_id,is_hypervisor)
    VALUES (22,'TRUE');

-- only include virtualization if these service types 
-- are present and the device is a virtual machine.
INSERT INTO mcal.calendar_selector
    (calendar_id,service_type_id,is_virtual_machine)
    VALUES (22,1,'TRUE'),(22,12,'TRUE'),(22,13,'TRUE'),
            (22,11,'TRUE'),(22,4,'TRUE'),(22,14,'TRUE'),
            (22,3,'TRUE'),(22,6,'TRUE'),(22,7,'TRUE'),
            (22,8,'TRUE'),(22,16,'TRUE'),(22,17,'TRUE'),
            (22,18,'TRUE'),(22,19,'TRUE'),(22,20,'TRUE'),
            (22,21,'TRUE'),(22,22,'TRUE'),(22,23,'TRUE'),
            (22,24,'TRUE'),(22,25,'TRUE'),(22,2,'TRUE');

-- Do not include the DC if a device is a virtual machine.
UPDATE mcal.calendar_selector SET is_virtual_machine='FALSE'
    WHERE mcal.calendar_selector.datacenter IS NOT NULL;

-- Deactivate old Virtualization calendar
UPDATE "UPGD_Queue" SET "Active" = 'f'
    WHERE "UPGD_QueueID" = 38;

COMMIT;










