-- Jira issue: LAM-102
-- Developer: Ryan Springer
-- Database: CORE
-- Schema : mcal

SET role TO postgres;

BEGIN;

    ALTER TABLE mcal.scheduled_maintenance 
	    ADD notify_customer_before      boolean         default false   not null,
	    ADD notify_customer_after       boolean         default false   not null,
	    ADD notify_customer_name        varchar(255)    default ''      not null,
	    ADD notify_customer_info        varchar(255)    default ''      not null,
	    ADD notify_customer_department  varchar(255)    default ''      not null,
	    ADD notify_customer_before_log  varchar(255)    default ''      not null,
	    ADD notify_customer_after_log   varchar(255)    default ''      not null;

COMMIT;

