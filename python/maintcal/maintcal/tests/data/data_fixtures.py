from datetime import datetime, timedelta

from maintcal.model import metadata, engine, MaintenanceCategory, \
    Calendar, Contact, ScheduledMaintenance, \
    ServiceType, ScheduledService, Server, Selector
from maintcal.model.ChangeLog import ServiceTypeChangeLog
from maintcal.model import db_sess

def set_sequence(sequence_name, sequence_number):
    """ Manually advance the pkey for scheduled_service """
    db_sess.execute("select setval('maintcal_test.%s', %i);" % (sequence_name, sequence_number))

def init_db():
    """
    Because we have an sqlalchemy session with Transactional=True,
    we are automatically in a top-level transaction at the start
    of each test.
    This means that there is an implicit db_sess.begin() that has
    been called.
    """
    pass

def empty_maintcal_tables():
    """
    We perform each test inside of a transaction, and then 
    we roll that transaction back at the end of the test
    to reset the database.
    """
    db_sess.rollback()
    db_sess.close()

def clear_db():
    empty_maintcal_tables()

def commit_db():
    """
    Commit changes to the database, by committing the top-level transaction.
    This can be useful for test-driven development or debugging tests, because
    it makes the results of the test run visible in the database for manual
    inspection.
    """
    db_sess.commit()
    db_sess.close()

def insert_data(dh):

    # Maintenance Categories
    mc1 = MaintenanceCategory(u'Implementation Call', u'imp call desc')
    mc1.id = 1
    db_sess.add(mc1)

    mc2 = MaintenanceCategory(u'Server Migration', u'server mig. desc')
    mc2.id = 2
    db_sess.add(mc2)
    
    set_sequence('maintenance_category_id_seq', 3)

    # Service Types
    st1 = ServiceType(u'Implementation Call', u'imp call desc', 1,
                             timedelta(hours=4), timedelta(hours=4))
    st1.id = 1
    db_sess.add(st1)
    st2 = ServiceType(u'Cabinet Migration', u'cab mig desc', 2,
                             timedelta(hours=1), timedelta(hours=72))
    st2.id = 2
    db_sess.add(st2)
    st3 = ServiceType(u'Old Service Type', u'old desc', 2,
                             timedelta(hours=1), timedelta(hours=72))
    st3.active=False
    st3.id = 3
    db_sess.add(st3)

    set_sequence('service_type_id_seq', 4)
   
    # Service Type ChangeLog with meaningful data.
    stcl1 = ServiceTypeChangeLog(
        1,
        contact = 'nath1234',
        field = 'active',
        old_value = u"True",
        new_value = u"False"
    )
    db_sess.add(stcl1)
    stcl1_latest = ServiceTypeChangeLog(
        1,
        contact = 'nath6666',
        field = 'active',
        old_value = u"False",
        new_value = u"True"
    )
    db_sess.add(stcl1_latest)
    stcl2 = ServiceTypeChangeLog(
        2,
        contact = 'nath6666',
        field = 'lead_time',
        old_value = u"01:00:00",
        new_value = u"72:00:00"
    )
    db_sess.add(stcl2)
    # Servers
    # todo: need to add a server with managed backup.
    #db_sess.commit()

    server1 = dh.insertTestComputer(110912)
    server2 = dh.insertTestComputer(110914)
    server3 = dh.insertTestComputer(110945)
    server4 = dh.insertTestComputer(176991)
    
    #db_sess.begin()

    # Users
    user_jd = Contact(1)
    user_jd.first_name = 'John'
    user_jd.last_name = 'Doe'
    user_jd.username = 'john.doe'
    db_sess.add(user_jd)
    
    user_dc = Contact(2)
    user_dc.first_name = 'Bob'
    user_dc.last_name = 'Racker'
    user_dc.username = 'bob.racker'
    db_sess.add(user_dc)
    
    user_tech = Contact(3)
    user_tech.first_name = 'Steve'
    user_tech.last_name = 'Techie'
    user_tech.username = 'steve.techie'
    db_sess.add(user_tech)
    
    # Maintenances

    sm_move_server = ScheduledMaintenance('071215-00001')
    sm_move_server.service_type_id = 2
    sm_move_server.general_description = u'Move Server'
    sm_move_server.contact_id = 1
    sm_move_server.date_assigned = datetime(2008, 1, 1, 0, 0)
    sm_move_server.additional_duration = timedelta(minutes=60)
    sm_move_server.id = 1
    sm_move_server.servers = [server1]
    db_sess.add(sm_move_server)
    
    
    sm_blank = ScheduledMaintenance('')
    sm_blank.id = 2
    sm_blank.creation_date = datetime(2008, 2, 5, 10)
    sm_blank.state_id=1
    db_sess.add(sm_blank)
    
    sm3 = ScheduledMaintenance('080101-00002')
    sm3.service_type_id = 1
    sm3.date_assigned = datetime(2008, 1, 1, 0, 0)
    sm3.additional_duration = timedelta(minutes=60)
    # sm3.length == 5 hrs
    sm3.id = 3
    db_sess.add(sm3)
    
    sm4 = ScheduledMaintenance('080101-00002')
    sm4.service_type_id = 1
    sm4.state_id = 2
    sm4.additional_duration = timedelta(minutes=60)
    sm4.id = 4
    db_sess.add(sm4)
    
    sm5 = ScheduledMaintenance('080101-00002')
    sm5.service_type_id = 1
    sm5.state_id = 2
    sm5.id = 5
    db_sess.add(sm5)

    set_sequence('scheduled_maintenance_id_seq', 6)

    # Calendars

    dh.insertCalendars()

    # Services
    service_rerack = ScheduledService(u"Rerack server", calendar=1, maintenance_id=1)
    service_rerack.ticket_number = '080112-00443'
    service_rerack.special_instructions = u"handle with care"
    service_rerack.start_time = datetime(2008, 1, 10, 12)
    service_rerack.end_time = datetime(2008, 1, 10, 14)
    service_rerack.id = 1
    service_rerack.state_id = 2
    service_rerack.servers = [server1, server3]
    db_sess.add(service_rerack)
    
    service_recon = ScheduledService(u"Reconfigure network settings", calendar=2, maintenance_id=1)
    service_recon.ticket_number = '080112-00456'
    service_recon.start_time = datetime(2008, 1, 10, 12)
    service_recon.end_time = datetime(2008, 1, 10, 14)
    service_recon.id = 2
    service_recon.state_id = 2
    service_recon.servers = [server1]
    db_sess.add(service_recon)
    
    service_3 = ScheduledService(u"Do nothing", calendar=2, maintenance_id=2)
    service_3.ticket_number = '080112-05000' 
    service_3.start_time = datetime(2008, 1, 8, 10)
    service_3.end_time = datetime(2008, 1, 8, 11)
    service_3.id = 3
    db_sess.add(service_3)
    
    service_4 = ScheduledService(u"Do stuff", calendar=1, maintenance_id=3)
    #service_4.ticket_number = '080112-06000' 
    #service_4.start_time = datetime(2008, 1, 8, 10)
    #service_4.end_time = datetime(2008, 1, 8, 11)
    service_4.id = 4
    db_sess.add(service_4)
    
    service_5 = ScheduledService(u"Do stuff", calendar=2, maintenance_id=3)
    #service_5.ticket_number = '080112-06000' 
    #service_4.start_time = datetime(2008, 1, 8, 10)
    #service_4.end_time = datetime(2008, 1, 8, 11)
    service_5.id = 5
    db_sess.add(service_5)
    
    service_6 = ScheduledService(u"Do nothing", calendar=2, maintenance_id=4)
    service_6.start_time = datetime(2008, 2, 8, 10)
    service_6.end_time = datetime(2008, 2, 8, 11)
    service_6.id = 6
    service_6.calendar_id = 1
    db_sess.add(service_6)

    service_7 = ScheduledService(u"Do nothing", calendar=3, maintenance_id=5)
    service_7.id = 7
    db_sess.add(service_7)

    set_sequence('scheduled_service_id_seq', 24)

    # Selectors
    selector1 = Selector()
    selector1.calendar_id = 3
    selector1.segment = u"Intensive"
    selector1.server_os = u'Microsoft Windows'
    db_sess.add(selector1)
    
    selector2 = Selector()
    selector2.calendar_id = 2
    selector2.segment = u"Managed"
    selector2.server_os = u'Linux'
    db_sess.add(selector2)
    
    selector3 = Selector()
    selector3.calendar_id = 1
    selector3.category = 2
    selector3.datacenter = u"SAT1"
    db_sess.add(selector3)
    
    selector4 = Selector()
    selector4.calendar_id = 4
    selector4.category = 2
    selector4.has_managed_storage = True
    db_sess.add(selector4)
    
    selector5 = Selector()
    selector5.calendar_id = 5
    selector5.category = 2
    selector5.datacenter = u"DFW1"
    db_sess.add(selector5)
    
    selector6 = Selector()
    selector6.calendar_id = 6
    selector6.category = 2
    selector6.has_managed_backup = True
    db_sess.add(selector6)
