-- Jira Issue: MCAL-46
-- Developer: Scott Gillenwater
-- Database: CORE Schema: mcal

\connect - core_write

BEGIN;

insert into mcal.calendar
 (id,name,description,tckt_queue_id,active,bookings,timezone)
 values (18,'Platform Hosting','Platform Hosting',187,'TRUE',1,'US/Central');

 insert into mcal.calendar_selector
  (id,calendar_id,segment,category,service_type_id)
  values (default,18,'Platform Hosting',7,68);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',7,70);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',7,71);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,12);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,11);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,4);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,14);     

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,3);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,5);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,6);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,7);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,8);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,9);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,10);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,15);    

insert into mcal.calendar_selector
 (id,calendar_id,segment,category,service_type_id)
 values (default,18,'Platform Hosting',3,16);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category)
 values (default,18,'Platform Hosting',5);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category)
 values (default,18,'Platform Hosting',4);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category)
 values (default,18,'Platform Hosting',1);

insert into mcal.calendar_selector
 (id,calendar_id,segment,category)
 values (default,18,'Platform Hosting',2);

commit;
