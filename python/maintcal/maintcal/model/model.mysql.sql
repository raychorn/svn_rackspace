-- ================================================================================
--   mysql SQL DDL Script File
-- ================================================================================


-- ===============================================================================
-- 
--   Generated by:      tedia2sql -- v1.2.12
--                      See http://tedia2sql.tigris.org/AUTHORS.html for tedia2sql author information
-- 
--   Target Database:   mysql
--   Generated at:      Thu Nov 15 18:07:00 2007
--   Input Files:       model.dia
-- 
-- ================================================================================



-- Generated SQL Constraints Drop statements
-- --------------------------------------------------------------------

-- drop constraint qcmc_val_service_type_fk_Maintenance_category for mysql
-- drop constraint qcmc_scheduled_maintenance_fk_Service_type for mysql
-- drop constraint qcmc_xrf_schdld_mntnc_srvr_lst_fk_Scheduled_maintenance_id for mysql
-- drop constraint qcmc_val_service_type_fk_Service_category for mysql
-- drop constraint qcmc_scheduled_service_fk_Calendar for mysql
-- drop constraint qcmc_scheduled_service_fk_Scheduled_maintenance for mysql
-- drop constraint qcmc_xref_scheduled_service_computer_fk_Scheduled_service for mysql
-- drop constraint qcmc_log_completion_fk_Scheduled_service for mysql
-- drop constraint qcmc_calendar_blocked_times_fk_Calendar for mysql


-- Generated Permissions Drops
-- --------------------------------------------------------------------




-- Generated SQL View Drop Statements
-- --------------------------------------------------------------------



-- Generated SQL Schema Drop statements
-- --------------------------------------------------------------------

 drop table if exists qcmc_scheduled_maintenance ;
 drop table if exists qcmc_maintenance_category ;
 drop table if exists qcmc_scheduled_maintenance_maintenance_calendar_selector ;
 drop table if exists qcmc_val_service_category ;
 drop table if exists qcmc_val_service_type ;
 drop table if exists qcmc_xref_scheduled_maintenance_server_list ;
 drop table if exists qcmc_calendar ;
 drop table if exists qcmc_scheduled_service ;
 drop table if exists qcmc_log_completion ;
 drop table if exists qcmc_xref_scheduled_service_computer ;
 drop table if exists qcmc_calendar_blocked_times ;


-- Generated SQL Schema
-- --------------------------------------------------------------------


-- qcmc_scheduled_maintenance
create table qcmc_scheduled_maintenance (
  id                        serial not null,
  master_ticket             integer not null,	-- This references the ticket ID, not the ticket ref. no. We need the not null constraint, but we cannot provide a default, because that would not make sense.
  state                     integer default 1,	-- Foreign key to the "state" table.
  service_type              integer,
  expedite                  text,
  additional_duration       interval,
  general_description       text,
  billing_text              text,
  employee_contact          integer,
  employee_name             text,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_scheduled_maintenance primary key (id)
) ;

-- qcmc_maintenance_category
create table qcmc_maintenance_category (
  id                        serial not null,
  name                      text,
  description               text,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_maintenance_category primary key (id)
) ;

-- qcmc_scheduled_maintenance_maintenance_calendar_selector
-- Used to define what attributes of a scheduled maintenance object will
-- cause the selection of that calendar.
create table qcmc_scheduled_maintenance_maintenance_calendar_selector (
  id                        serial not null,
  calendar                  integer,	-- Foreign key reference to "UPGD_Queue"
  segment                   integer,	-- Foreign key reference to "ACCT_val_AccountType"
  category                  integer,	-- reference to the "maintenance_category" table
  server_os                 integer,	-- reference to the "COMP_val_OSGroup" table.
  datacenter                integer,	-- Reference to the "datacenter" table.
  service_type              integer,	-- Reference to the "service_type" table.
  sku                       integer,	-- reference to the "sku" table.
  constraint pk_Qcmc_scheduled_maintenance_maintenance_calendar_selector primary key (id)
) ;

-- qcmc_val_service_category
create table qcmc_val_service_category (
  id                        serial not null,
  name                      text,
  description               text,
  active                    boolean default false,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_val_service_category primary key (id)
) ;

-- qcmc_val_service_type
-- The type of service that can be sch ... ades.
create table qcmc_val_service_type (
  id                        serial not null,
  name                      text,
  description               text,
  active                    boolean default false,
  service_category          integer,
  length                    interval,
  maintenance_category      integer,	-- Foreign key to the maintenance_category table.
  lead_time                 interval,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_val_service_type primary key (id)
) ;

-- qcmc_xref_scheduled_maintenance_server_list
create table qcmc_xref_scheduled_maintenance_server_list (
  id                        serial not null,
  scheduled_maintenance_id  integer,	-- Reference to scheduled_maintenance object.
  computer                  integer,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_xref_scheduled_maintenance_server_list primary key (id)
) ;

-- qcmc_calendar
-- A queue to collect upgrades.
create table qcmc_calendar (
  id                        serial not null,
  name                      text,
  description               text,
  TCKT_QueueID              integer,
  active                    boolean default true,
  max_bookings              integer default 1,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_calendar primary key (id)
) ;

-- qcmc_scheduled_service
-- A scheduled upgrade service.
create table qcmc_scheduled_service (
  id                        serial not null,
  service_type              integer,
  description               text,
  contact                   integer,
  date_assigned             date default now(),
  ticket                    integer,
  start_time                timestamp with time zone,
  end_time                  timestamp with time zone,
  calendar                  integer,
  scheduled_maintenance     integer,	-- Foreign key reference to the "UPGD_ScheduledMaintenance" table.
  special_instructions      text,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_scheduled_service primary key (id)
) ;

-- qcmc_log_completion
-- A log of when upgrade services were ... eted.
create table qcmc_log_completion (
  id                        serial not null,
  scheduled_service         integer,
  contact                   integer,
  date                      timestamp with time zone,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_log_completion primary key (id)
) ;

-- qcmc_xref_scheduled_service_computer
create table qcmc_xref_scheduled_service_computer (
  id                        serial not null,
  scheduled_service         integer,
  computer_number           integer,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_xref_scheduled_service_computer primary key (id)
) ;

-- qcmc_calendar_blocked_times
create table qcmc_calendar_blocked_times (
  id                        serial not null,
  calendar                  integer,
  start_time                timestamp with time zone,
  end_time                  timestamp with time zone,
  creation_date             timestamp default now(),
  modification_date         timestamp default now(),
  constraint pk_Qcmc_calendar_blocked_times primary key (id)
) ;













-- Generated SQL Views
-- --------------------------------------------------------------------




-- Generated Permissions
-- --------------------------------------------------------------------



-- Generated SQL Insert statements
-- --------------------------------------------------------------------



-- Generated SQL Constraints
-- --------------------------------------------------------------------

-- alter table qcmc_val_service_type add constraint qcmc_val_service_type_fk_Maintenance_category
  foreign key (maintenance_category) references
  qcmc_maintenance_category (id) for mysql
-- alter table qcmc_scheduled_maintenance add constraint qcmc_scheduled_maintenance_fk_Service_type
  foreign key (service_type) references
  qcmc_val_service_type (id) for mysql
-- alter table qcmc_xref_scheduled_maintenance_server_list add constraint qcmc_xrf_schdld_mntnc_srvr_lst_fk_Scheduled_maintenance_id
  foreign key (scheduled_maintenance_id) references
  qcmc_scheduled_maintenance (id) for mysql
-- alter table qcmc_val_service_type add constraint qcmc_val_service_type_fk_Service_category
  foreign key (service_category) references
  qcmc_val_service_category (id) for mysql
-- alter table qcmc_scheduled_service add constraint qcmc_scheduled_service_fk_Calendar
  foreign key (calendar) references
  qcmc_calendar (id) for mysql
-- alter table qcmc_scheduled_service add constraint qcmc_scheduled_service_fk_Scheduled_maintenance
  foreign key (scheduled_maintenance) references
  qcmc_scheduled_maintenance (id) for mysql
-- alter table qcmc_xref_scheduled_service_computer add constraint qcmc_xref_scheduled_service_computer_fk_Scheduled_service
  foreign key (scheduled_service) references
  qcmc_scheduled_service (id) for mysql
-- alter table qcmc_log_completion add constraint qcmc_log_completion_fk_Scheduled_service
  foreign key (scheduled_service) references
  qcmc_scheduled_service (id) for mysql
-- alter table qcmc_calendar_blocked_times add constraint qcmc_calendar_blocked_times_fk_Calendar
  foreign key (calendar) references
  qcmc_calendar (id) for mysql

