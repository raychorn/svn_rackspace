begin;

-- Create recurrence ID sequence
CREATE SEQUENCE recurrence_id_seq;

-- Insert maintenance categories
INSERT INTO maintenance_category (id, name, description)
    VALUES
        (1, 'Implementation Call', 'This maintenance type is used for scheduling time for support to conduct the Implemenation Call.  Support and Network Security will be included in this request.');

INSERT INTO maintenance_category (id, name, description)
    VALUES
        (2, 'Server Migration', 'This maintenance type is for migrating or moving servers in the data center for any reason.  DC Operations, Network Security and Support will be included in this request as well as Managed Storage if SAN is included in the migration.');

INSERT INTO maintenance_category (id, name, description)
    VALUES
        (3, 'Network Hardware Upgrade/Maintenance', 'This maintenance type includes networking hardware replacements and upgrades, i.e. Firewall, Load Balancers, and Switch upgrades.  DC Operations, Network Security and Support will be included in this request.');

INSERT INTO maintenance_category (id, name, description)
    VALUES
        (4, 'Server Hardware Upgrade/Maintenance', 'This maintenance type includes server hardware replacements and upgrades, i.e. RAM, HDD and CPU upgrades.  DC Operations and Support will be included in this request as well as Managed Storage if SAN is included.');

INSERT INTO maintenance_category (id, name, description)
    VALUES
        (5, 'Network Software Upgrade/Maintenance/Walkthrough', 'This maintenance type includes networking software installations and updates, i.e. IOS upgrades.  Network Security and Support will be included in this request.');

INSERT INTO maintenance_category (id, name, description)
    VALUES
        (6, 'Managed Server Software Upgrade/Maintenance/Walkthrough', 'This maintenance type includes server software installations and updates, i.e. Software install and patches.  Support will be included in this request.');

INSERT INTO maintenance_category (id, name, description)
    VALUES
        (7, 'Intensive Server Software Upgrade/Maintenance/Walkthrough', 'This maintenance type includes server software installations and updates, i.e. Software install and patches.  Support will be included in this request.');

SELECT setval('maintenance_category_id_seq', 7);

-- Insert service categories
INSERT INTO service_category (id, name)
    VALUES
        (1, 'General');
INSERT INTO service_category (id, name)
    VALUES
        (2, 'Firewall');
INSERT INTO service_category (id, name)
    VALUES
        (3, 'Load Balancer');
INSERT INTO service_category (id, name)
    VALUES
        (4, 'Conference Call');
INSERT INTO service_category (id, name)
    VALUES
        (5, 'VPN');
INSERT INTO service_category (id, name)
    VALUES
        (6, 'Reboot');
INSERT INTO service_category (id, name)
    VALUES
        (7, 'Upgrades/Downgrades');
INSERT INTO service_category (id, name)
    VALUES
        (8, 'Updates');

SELECT setval('service_category_id_seq', 8);

-- Insert service types
-- Implementation Call Service Types
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (1, 'Implementation Call', 1, '4 hours', '4 hours');

-- Server Migration Service Types
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (2, 'Cabinet Migration', 1, '1 hour', '72 hours');

-- Network Hardware Upgrade
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Add a Firewall', 2, '1 hour', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Add a DMZ', 2, '30 minutes', '48 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Firewall Maintenance', 2, '1 hour', '2 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Add a WebMux', 3, '1 hour', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Add a CSS', 3, '1 hour', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Migrate Load Balancers', 3, '1 hour', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Redhill to CSS Migration', 3, '1 hour', '72 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Load Balancer Maintenance', 3, '1 hour', '1 hour');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Add PrivateNet', 1, '30 minutes', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Add LocalNet', 1, '30 minutes', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
	(3, 'Add Managed Backup', 1, '30 minutes', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Move Server in Zones', 1, '30 minutes', '8 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'HA Setup', 1, '1 hour', '96 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (3, 'Non-Standard Configurations', 1, '2 hours', '96 hours');

-- Server Hardware Upgrade
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'Ghost Drive', 1, '3 hours', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'FSCK', 1, '1 hour', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'Rebuild RAID', 1, '2 hours', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'Hardware Maintenance', 1, '1 hour', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'Hardware Upgrade', 1, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'Troubleshoot Hardware', 1, '1 hour', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'OS Install (Windows)', 1, '2 hours', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'OS Install (Linux)', 1, '1 hour', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (4, 'HA Cluster Testing', 1, '3 hours', '24 hours');

-- Network Software Upgrade
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Upgrade/Downgrade Code on PIX', 2, '30 minutes', '1 hour');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Firewall Model Upgrade', 2, '30 minutes', '48 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Reboot Firewall', 2, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Repair Firewall', 2, '1 hour', '1 hour');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot Firewall', 2, '2 hours', '2 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Change NAT Scheme on Firewall', 2, '30 minutes', '48 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Upgrade/Downgrade Code on LB', 3, '1 hour', '2 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'CSS Model Upgrade', 3, '1 hour', '48 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Reboot Load Balancer', 3, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Repair Load Balancer', 3, '1 hour', '2 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot Load Balancer', 3, '2 hours', '2 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Add SSL Certificate to CSS', 3, '30 minutes', '24 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot PrivateNet', 1, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot LocalNet', 1, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot Managed Backup', 1, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Port Speed Upgrade', 1, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'GIG Upgrade', 1, '1 hour', '96 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot', 1, '2 hours', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'IDS/Alert Logic Walkthrough', 1, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot VPN', 4, '2 hours', '1 hour');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot Firewall', 4, '2 hours', '1 hour');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot Load Balancer', 4, '2 hours', '2 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Configuration Change VPN', 5, '30 minutes', '1 hour');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Add VPN', 5, '30 minutes', '2 hours');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Reset VPN', 5, '30 minutes', '1 hour');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Change Peer VPN', 5, '30 minutes', '30 minutes');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (5, 'Troubleshoot VPN', 5, '30 minutes', '30 minutes');



-- Managed Server Software Upgrade
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Kernel', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Plesk Update (Package Update)', 1, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Plesk Update (Version Update)', 1, '2 hours', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Plesk Update (Multi Version)', 1, '4 hours', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Updates via up2date', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Software Install/Update (non-up2date)', 1, '2 hours', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Software/OS Troubleshooting', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Reboot', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'PSA/SQL Dump', 1, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Monitor Server', 1, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (6, 'Customer Walkthrough', 1, '1 hour', '0');

-- Intensive Server Software Upgrade
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Backup/Stress Test', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'PSA/SQL Dump', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'MS SQL', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Monitor Server', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Other', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Software/OS Troubleshooting', 1, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Customer Walkthrough', 1, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Reboot', 6, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Custom Software', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Kernel', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'MailMax', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Other', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Plesk', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Security/Patch', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Urchin', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Webmail', 7, '1 hour', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Critical', 8, '30 minutes', '0');
INSERT INTO service_type (maintenance_category_id, name, service_category_id, length, lead_time)
    VALUES
        (7, 'Non-Critical', 8, '30 minutes', '0');
-- Activate all service types
UPDATE service_type SET active = true;

-- Insert calendars
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (1, 'Intensive Windows', 'Intensive Windows', 26, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (2, 'Intensive Unix', 'Intensive Unix', 26, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (3, 'Managed Windows', 'Managed Windows (M1,M3,M5,M7,M9)', 1, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (4, 'Managed Unix', 'Managed Unix (M2,M4,M6,M8,M12)', 1, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (5, 'Intensive Professional Services', 'Intensive Professional Services', 7, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone, tckt_subcategory_id) VALUES
    (6, 'Managed Net Sec', 'Managed NetSec', 165, 'US/Central', 7023);
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (7, 'DC Ops (DFW1)', 'Datacenter Operations (Grapevine)', 49, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (8, 'DC Ops (IAD1)', 'Datacenter Operations (DullesOne)', 17, 'US/Eastern');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (9, 'DC Ops (SAT1)', 'Datacenter Operations (Weston Centre)', 2, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (10, 'DC Ops (SAT2)', 'Datacenter Operations (Vegas)', 3, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (11, 'DC Ops (SAT4)', 'Datacenter Operations (Datapoint)', 55, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (12, 'DC Ops (LON1)', 'Datacenter Operations (London)', 5, 'Europe/London');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (13, 'DC Ops (LON2)', 'Datacenter Operations (LON2 - Wembley)', 94, 'Europe/London');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (14, 'DC Ops (LONB)', 'Datacenter Operations (LONB)', 83, 'Europe/London');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (15, 'Managed Storage', 'Managed Storage Maintenance Calendar', 92, 'US/Central');
INSERT INTO calendar (id, name, description, tckt_queue_id, timezone) VALUES
    (16, 'DC Ops (LON3)', 'Datacenter Operations (LON3)', 189, 'Europe/London');
SELECT setval('calendar_id_seq', 16);

-- Insert selector
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (1, 'Intensive', 'Microsoft Windows');
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (2, 'Intensive', 'Linux');
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (2, 'Intensive', 'BSD');
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (2, 'Intensive', 'Sun/Solaris');
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (3, 'Managed', 'Microsoft Windows');
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (4, 'Managed', 'Linux');
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (4, 'Managed', 'BSD');
INSERT INTO calendar_selector (calendar_id, segment, server_os) VALUES
    (4, 'Managed', 'Sun/Solaris');
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (5, 'Intensive', 1);
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (5, 'Intensive', 2);
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (5, 'Intensive', 3);
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (5, 'Intensive', 5);
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (6, 'Managed', 1);
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (6, 'Managed', 2);
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (6, 'Managed', 3);
INSERT INTO calendar_selector (calendar_id, segment, category) VALUES
    (6, 'Managed', 5);
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (7, 2, 'DFW1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (7, 3, 'DFW1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (7, 4, 'DFW1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (8, 2, 'IAD1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (8, 3, 'IAD1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (8, 4, 'IAD1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (9, 2, 'SAT1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (9, 3, 'SAT1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (9, 4, 'SAT1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (10, 2, 'SAT2');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (10, 3, 'SAT2');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (10, 4, 'SAT2');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (11, 2, 'SAT4');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (11, 3, 'SAT4');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (11, 4, 'SAT4');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (12, 2, 'LON1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (12, 3, 'LON1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (12, 4, 'LON1');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (13, 2, 'LON2');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (13, 3, 'LON2');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (13, 4, 'LON2');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (14, 2, 'LONB');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (14, 3, 'LONB');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (14, 4, 'LONB');
INSERT INTO calendar_selector (calendar_id,category,has_managed_storage) VALUES
    (15,2,true);
INSErT INTO calendar_selector (calendar_id,category,has_managed_storage) VALUES
    (15,4,true);
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (16, 2, 'LON3');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (16, 3, 'LON3');
INSERT INTO calendar_selector (calendar_id, category, datacenter) VALUES
    (16, 4, 'LON3');
commit;
