-- Jira issue: MCAL-130
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson, Derrick Wippler, Keith Swallow, Chris Gaither
-- Database: CORE
-- Schema : mcal

SET role TO postgres;

BEGIN;

    -- ALTER TABLES TO STORE DATES IN UTC

    ALTER TABLE mcal.scheduled_maintenance 
        ALTER COLUMN date_assigned TYPE TIMESTAMP WITHOUT TIME ZONE
            USING date_assigned AT TIME ZONE 'UTC';

    ALTER TABLE mcal.scheduled_service 
        ALTER COLUMN date_assigned TYPE TIMESTAMP WITHOUT TIME ZONE
            USING date_assigned AT TIME ZONE 'UTC',
        ALTER COLUMN start_time TYPE TIMESTAMP WITHOUT TIME ZONE
            USING start_time AT TIME ZONE 'UTC',
        ALTER COLUMN end_time TYPE TIMESTAMP WITHOUT TIME ZONE
            USING end_time AT TIME ZONE 'UTC';

    -- BACKUP TABLES

	ALTER TABLE mcal.blocked_time       SET SCHEMA rollback;
	ALTER TABLE mcal.service_category   SET SCHEMA rollback;
	ALTER TABLE mcal.times_available    SET SCHEMA rollback;

    -- CREATES

    CREATE TABLE mcal.available_defaults (
        id                   serial       primary key,
        calendar_id          integer      not null REFERENCES mcal.calendar (id),
        dow                  integer      not null,
        start_minutes        integer      not null,
        end_minutes          integer      not null,
        work_units_in_quanta integer      not null,
        comments             text         not null default '',
        creation_date        timestamp    not null,
        modification_date    timestamp    not null
    );

    CREATE TABLE mcal.available_exceptions (
        id                   serial       primary key,
        calendar_id          integer      not null REFERENCES mcal.calendar (id),
        exception_date       date         not null,
        start_minutes        integer      not null,
        end_minutes          integer      not null,
        work_units_in_quanta integer      not null,
        comments             text         not null default '',
        creation_date        timestamp    not null,
        modification_date    timestamp    not null
    );

    CREATE TABLE mcal.available_log_changes (
        id                   serial       primary key,
        calendar_id          integer      not null REFERENCES mcal.calendar (id),
        dow                  integer,
        exception_date       date,
        start_minutes        integer      not null,
        end_minutes          integer      not null,
        work_units_in_quanta integer      not null,
        comments             text         not null default '',
        creation_date        timestamp    not null,
        modification_date    timestamp    not null
    );

    -- TRIGGERS

    CREATE TRIGGER available_defaults_creation_date
        BEFORE INSERT ON mcal.available_defaults
        FOR EACH ROW EXECUTE PROCEDURE creation_date();

    CREATE TRIGGER available_defaults_modification_date
        BEFORE INSERT OR UPDATE ON mcal.available_defaults
        FOR EACH ROW EXECUTE PROCEDURE modification_date();

    CREATE TRIGGER available_exceptions_creation_date
        BEFORE INSERT ON mcal.available_exceptions
        FOR EACH ROW EXECUTE PROCEDURE creation_date();

    CREATE TRIGGER available_exceptions_modification_date
        BEFORE INSERT OR UPDATE ON mcal.available_exceptions
        FOR EACH ROW EXECUTE PROCEDURE modification_date();

    CREATE TRIGGER available_log_changes_creation_date
        BEFORE INSERT ON mcal.available_log_changes
        FOR EACH ROW EXECUTE PROCEDURE creation_date();

    CREATE TRIGGER available_log_changes_modification_date
        BEFORE INSERT OR UPDATE ON mcal.available_log_changes
        FOR EACH ROW EXECUTE PROCEDURE modification_date();

    -- GRANTS

    GRANT SELECT, DELETE, INSERT, UPDATE ON mcal.available_defaults TO core_write;
    GRANT SELECT, UPDATE ON mcal.available_defaults_id_seq TO core_write;

    GRANT SELECT, DELETE, INSERT, UPDATE ON mcal.available_exceptions TO core_write;
    GRANT SELECT, UPDATE ON mcal.available_exceptions_id_seq TO core_write;

    GRANT SELECT, DELETE, INSERT, UPDATE ON mcal.available_log_changes TO core_write;
    GRANT SELECT, UPDATE ON mcal.available_log_changes_id_seq TO core_write;

    -- UPDATES TO EXISTING TABLES WITH DATA

	ALTER TABLE mcal.calendar 
	    ADD new_ticket_queue_id         integer,
	    ADD new_ticket_category_id      integer,
	    ADD new_ticket_status_id        integer,
	    ADD time_before_ticket_refresh  float,
	    ADD refresh_ticket_assignment   boolean     default false   not null,
	    ADD refresh_ticket_queue_id     integer,
	    ADD refresh_category_id         integer,
	    ADD refresh_status_id           integer,
	    ADD hold_tentative_time         float;

    -- DC Ops (SAT4)
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',55,0,658,2,'f',55,0,658,2) WHERE id=11;

    -- DC Ops (SAT2)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',3,0,30,2,'f',3,0,30,2) WHERE id=10;

    -- DC Ops (LON2)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('Europe/London',94,0,1152,2,'f',94,0,1152,2) WHERE id=13;

   -- DC Ops (LON1) 
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('Europe/London',5,0,40,2,'f',5,0,40,2) WHERE id=12;

    -- Managed Storage SAN
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',92,0,1126,2,'f',92,0,1126,2) WHERE id=15;

    -- DC Ops (LONB)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('Europe/London',83,0,1001,2,'f',83,0,1001,2) WHERE id=14;

    -- DCOPs (HKG1)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('Asia/Hong_Kong',197,0,2637,2,'f',197,0,2637,2) WHERE id=17;

    --  DC Ops (LON3)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('Europe/London',189,0,2534,2,'f',189,0,2534,2) WHERE id=16;

    -- Managed Backup
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',138,0,1772,2,'f',138,0,1772,2) WHERE id=19;

    -- Managed Colocation
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',187,0,2498,2,'f',187,0,2498,2) WHERE id=18;

    -- Intensive Windows
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',26,0,214,2,'f',26,0,214,2) WHERE id=1;

    -- Managed Windows
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',1,0,3455,2,'f',1,0,3455,2) WHERE id=3;

    -- Intensive Unix
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',26,0,214,2,'f',26,0,214,2) WHERE id=2;

    -- Intensive Professional Services now Intensive Net Sec
	    
	UPDATE mcal.calendar SET
	    (name,timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('Intensive Net Sec','America/Chicago',7,0,13,2,'f',7,0,13,2) WHERE id=5;

    -- Managed Unix
	   
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',1,0,3455,2,'f',1,0,3455,2) WHERE id=4;

    -- DC Ops (DFW1)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',49,0,629,2,'f',49,0,629,2) WHERE id=7;

    -- Managed Net Sec
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',165,7023,2154,2,'f',165,7023,2154,2) WHERE id=6;

    -- DC Ops (SAT1)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',2,0,25,2,'f',2,0,25,2) WHERE id=9;

    -- DC Ops (IAD1)
	    
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/New_York',17,0,121,2,'f',17,0,121,2) WHERE id=8;

    --  Managed Storage DAS

	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',130,0,1653,2,'f',130,0,1653,2) WHERE id=20;

    -- Managed Storage NAS
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',175,0,2326,2,'f',175,0,2326,2) WHERE id=21;

    -- Virtualization
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',136,0,1734,2,'f',136,0,1734,2) WHERE id=22;

    -- DC Ops(IAD2) 
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/New_York',359,0,3932,2,'f',359,0,3932,2) WHERE id=23;

    -- redacted Cloud
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',360,0,3959,2,'f',360,0,3959,2) WHERE id=50;

    -- Enterprise Services Unix
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',390,0,4541,2,'f',390,0,4541,2) WHERE id=51;

    -- Enterprise Services Windows
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',390,0,4541,2,'f',390,0,4541,2) WHERE id=52;

    -- Enterprise Services Professional Services
	
	UPDATE mcal.calendar SET
	    (name,tckt_queue_id,timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('Enterprise Services Net Sec',388,'America/Chicago',388,0,4388,2,'f',388,0,4388,2) WHERE id=53;

    -- DC Ops(ORD1)
	
	UPDATE mcal.calendar SET
	    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
	     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
	     ('America/Chicago',391,0,4454,2,'f',391,0,4454,2) WHERE id=54;

COMMIT;

