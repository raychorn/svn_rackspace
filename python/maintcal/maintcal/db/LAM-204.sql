-- Jira: LAM-204
-- Developer: Hirensinh chavda, Trinabh Shukla
-- Database: CORE
-- Schema: mcal

SET role postgres;

BEGIN;

CREATE TABLE mcal.scheduled_service_status_reason (
  id                        serial  primary key,
  reason                    text    not null,
  feedback                  text    default null,
  service_id                integer not null,
  creation_date             timestamp default now(),
  modification_date         timestamp default now()
);

CREATE TRIGGER scheduled_service_status_reason_creation_date
    BEFORE INSERT ON mcal.scheduled_service_status_reason
        FOR EACH ROW EXECUTE PROCEDURE creation_date();

CREATE TRIGGER scheduled_service_status_reason_modification_date
    BEFORE INSERT OR UPDATE ON mcal.scheduled_service_status_reason
        FOR EACH ROW EXECUTE PROCEDURE modification_date();

GRANT SELECT, UPDATE ON TABLE mcal.scheduled_service_status_reason_id_seq TO core_write;

GRANT SELECT ON TABLE mcal.scheduled_service_status_reason_id_seq TO core_support;

GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE mcal.scheduled_service_status_reason TO core_write;

GRANT SELECT ON TABLE mcal.scheduled_service_status_reason TO core_support, dw_read, rba_read;

COMMIT;
