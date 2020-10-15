BEGIN;

INSERT INTO maintenance_category VALUES(1,'Implementation Call	','imp call desc');
INSERT INTO maintenance_category VALUES(2,'Server Migration','server mig. desc');
INSERT INTO scheduled_maintenance VALUES(1,'071215-00001',1,NULL,'','Move server','',2,NULL);
INSERT INTO service_category VALUES(1,'General','general service category','true');
INSERT INTO service_category VALUES(2,'Firewall','firewall related services','true');
INSERT INTO service_type VALUES(1,'Implementation Call','imp call desc','true','1970-01-01 04:00:00.0','1970-01-01 04:00:00.0',1,1);
INSERT INTO service_type VALUES(2,'Cabinet Migration','imp call desc','true','1970-01-01 01:00:00.0','1970-01-04 00:00:00.0',2,2);

COMMIT;
