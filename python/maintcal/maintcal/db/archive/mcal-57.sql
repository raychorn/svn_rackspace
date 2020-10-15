-- Jira Issue: MCAL-57
-- Developer: Nathen Hinson
-- Database: CORE schema MCAL

\connect - core_write

begin;

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

UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',55,0,658,2,'f',55,0,658,2) WHERE id=11;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',3,0,30,2,'f',3,0,30,2) WHERE id=10;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',94,0,1152,2,'f',94,0,1152,2) WHERE id=13;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',5,0,40,2,'f',5,0,40,2) WHERE id=12;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',92,0,1126,2,'f',92,0,1126,2) WHERE id=15;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',83,0,1001,2,'f',83,0,1001,2) WHERE id=14;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',197,0,2637,2,'f',197,0,2637,2) WHERE id=17;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',189,0,2534,2,'f',189,0,2534,2) WHERE id=16;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',138,0,1772,2,'f',138,0,1772,2) WHERE id=19;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',187,0,2498,2,'f',187,0,2498,2) WHERE id=18;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',26,0,214,2,'f',26,0,214,2) WHERE id=1;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',1,0,3455,2,'f',1,0,3455,2) WHERE id=3;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',26,0,214,2,'f',26,0,214,2) WHERE id=2;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',7,0,13,2,'f',7,0,13,2) WHERE id=5;
   
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',1,0,3455,2,'f',1,0,3455,2) WHERE id=4;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',49,0,629,2,'f',49,0,629,2) WHERE id=7;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',165,7023,2154,2,'f',165,7023,2154,2) WHERE id=6;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',2,0,25,2,'f',2,0,25,2) WHERE id=9;
    
UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/New_York',17,0,121,2,'f',17,0,121,2) WHERE id=8;

UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',130,0,1653,2,'f',130,0,1653,2) WHERE id=20;

UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',175,0,2326,2,'f',175,0,2326,2) WHERE id=21;

UPDATE mcal.calendar SET
    (timezone, new_ticket_queue_id, new_ticket_category_id, new_ticket_status_id, time_before_ticket_refresh,
     refresh_ticket_assignment, refresh_ticket_queue_id, refresh_category_id, refresh_status_id, hold_tentative_time) = 
     ('America/Chicago',136,0,1734,2,'f',136,0,1734,2) WHERE id=22;

commit;
