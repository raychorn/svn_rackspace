from pylons import config
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import mapper, relation, column_property
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import select, label, func
from xmlrpclib import Fault

engine = config['pylons.g'].sa_engine

if 'test_use_thread_global_db_sess' in config:
    # This is for testing with a browser, 
    # make the db_sess variable global to all threads
    db_sess = (sessionmaker(autoflush=True,
		    #transactional=True,
	    	bind=engine))()
else:
    # This is the normal case, make the db_sess variable
    # local to each thread
    db_sess = scoped_session(sessionmaker(autoflush=True,
		    #transactional=True,
	    	bind=engine))


#from maintcal.lib import core_xmlrpc
import maintcal

from tables import metadata, calendar_table, maintenance_table, \
    scheduled_maintenance_table, scheduled_service_table, \
    service_type_table, user_table, server_table, \
    service_server_list_table, server_table, selector_table, \
    change_log_table, recurrence_id_seq, available_defaults_table, \
    available_exceptions_table, available_log_changes_table, \
    scheduled_service_status_reason_table

from Calendar import Calendar
from ScheduledService import ScheduledService
from ScheduledMaintenance import ScheduledMaintenance
from ServiceType import ServiceType
from MaintenanceCategory import MaintenanceCategory
from Contact import Contact
from Server import Server
from Selector import Selector
from ChangeLog import ChangeLog
from AvailableDefaults import AvailableDefaults, StaleDefaultsException
from AvailableExceptions import AvailableExceptions, StaleExceptionsException
from AvailableLogChanges import AvailableLogChanges
from ScheduledServiceReason import ScheduledServiceReason

# Map SA tables to classes
mapper(Contact, user_table)
mapper(Calendar, calendar_table)

mapper(ScheduledService, scheduled_service_table, properties={
		'calendar' : relation(Calendar),
		'servers' : relation(Server, secondary=service_server_list_table)})
mapper(ScheduledMaintenance, scheduled_maintenance_table, properties={
		'service_type': relation(ServiceType),
		'contact': relation(Contact),
		'services': relation(ScheduledService, backref='maintenance'),
		})
mapper(ServiceType, service_type_table, properties={
		'maintenance_category': relation(MaintenanceCategory)})
mapper(MaintenanceCategory, maintenance_table)
mapper(Server, server_table)
mapper(Selector, selector_table)
mapper(AvailableExceptions, available_exceptions_table)
mapper(AvailableDefaults, available_defaults_table)
mapper(AvailableLogChanges, available_log_changes_table)
mapper(ChangeLog, change_log_table)
mapper(ScheduledServiceReason, scheduled_service_status_reason_table)

def fetchContactId(username):
    cont_query = db_sess.query(Contact).filter_by(username=username)
    if cont_query.count():
        cont = cont_query.one()
    else:
        try:
            id = maintcal.lib.core_xmlrpc.Auth.getContactId(username)
            # check to see if this user has changed their SSO username
            # and already has an entry in the user_cache.
            cont = db_sess.query(Contact).get(id)
            if cont:
                cont.username = username
            else:
                cont = Contact(id)
                cont.username = username
                db_sess.save(cont)
            #db_sess.commit()
        except Fault:
            raise
    return cont.id

def fetchContactUserName(id):
    cont = db_sess.query(Contact).get(id)
    if not cont:
        try:
            cont = Contact(id)
            cont.username = maintcal.lib.core_xmlrpc.Auth.getUserName(id)
            db_sess.save(cont)
            #db_sess.commit()
        except Fault:
            raise
    return cont.username
