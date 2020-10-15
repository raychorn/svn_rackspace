"""
Note:

- All datetimes in the database will NOT BE ZONED.
- All datetimes, except for creation_date and modification_date, will contain UTC values.
- creation_date and modification_date will be local timestamps.
"""
from pylons import config
from sqlalchemy import MetaData, Table, Column, ForeignKey, types, Sequence, PassiveDefault, sql
from sqlalchemy.schema import FetchedValue
from maintcal.lib.date.maintcal_datetime import MaintcalDatetime

metadata = MetaData()

schema_name = config.get('db_schema_name')
if schema_name != None:
    fkey_schema_name = '%s.' % schema_name
else:
    fkey_schema_name = ''


# Define a couple of types

class MaintcalDatetimeType(types.TypeDecorator):
    """
        Convert database datetime types to MaintcalDateTime types
        and vice versa.
    """
    impl = types.DateTime


    def process_bind_param(self, value, engine):
        """
        # To db(?)
        value should be a maintcal_datetime
        """
        # TODO: kill this check when refactoring is done
        if hasattr(value, 'to_python_datetime'):
            return value.to_python_datetime()
        return value


    def process_result_value(self, value, engine):
        """
        # From db
        value should be a python_datetime
        """
        # value is None when the database is null
        if value is None:
            return None
        return MaintcalDatetime.from_python_datetime(value)


user_table = Table('user_cache', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('username', types.Text),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

calendar_table = Table('calendar', metadata,
        Column('id',  types.Integer, primary_key=True),
        Column('name', types.UnicodeText),
        Column('description', types.UnicodeText),
        Column('tckt_queue_id', types.Integer),
        Column('tckt_subcategory_id', types.Integer),
        Column('active', types.Boolean, nullable=False, default=True),
        Column('timezone', types.Text),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        Column('new_ticket_queue_id', types.Integer),
        Column('new_ticket_category_id', types.Integer),
        Column('new_ticket_status_id', types.Integer),
        Column('time_before_ticket_refresh', types.Interval),
        Column('refresh_ticket_assignment', types.Boolean, nullable=False, default=False),
        Column('refresh_ticket_queue_id', types.Integer),
        Column('refresh_category_id', types.Integer),
        Column('refresh_status_id', types.Integer),
        Column('hold_tentative_time', types.Interval),
        schema = schema_name)

scheduled_service_table = Table('scheduled_service', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('description', types.UnicodeText),
        Column('ticket_number', types.Text),
        Column('start_time', MaintcalDatetimeType),
        Column('end_time', MaintcalDatetimeType),
        Column('calendar_id', types.Integer, ForeignKey('%scalendar.id' % fkey_schema_name)),
        Column('scheduled_maintenance_id', types.Integer, ForeignKey('%sscheduled_maintenance.id' % fkey_schema_name)),
        Column('state_id', types.Integer),
        Column('date_assigned', MaintcalDatetimeType, server_default=FetchedValue()),
        Column('creation_date', types.DateTime, server_default=FetchedValue()),
        Column('modification_date', types.DateTime, server_default=FetchedValue()),
        Column('ticket_popped', types.Boolean),
        schema = schema_name)

scheduled_maintenance_table = Table('scheduled_maintenance', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('master_ticket', types.Text),
        Column('account_id', types.Integer),
        Column('account_name', types.UnicodeText),
        Column('state_id', types.Integer, default=1),
        Column('additional_duration', types.Interval),
        Column('expedite', types.Boolean, nullable=False, default=False),
        Column('general_description', types.UnicodeText),
        Column('service_type_id', types.Integer, ForeignKey('%sservice_type.id' % fkey_schema_name)),
        Column('contact_id', types.Integer, ForeignKey('%suser_cache.id' % fkey_schema_name)),

        Column('notify_customer_before', types.Boolean, nullable=False, default=False),
        Column('notify_customer_after', types.Boolean, nullable=False, default=False),
        Column('notify_customer_name', types.UnicodeText, nullable=False, default=u''),
        Column('notify_customer_info', types.UnicodeText, nullable=False, default=u''),
        Column('notify_customer_department', types.UnicodeText, nullable=False, default=u''),
        Column('notify_customer_before_log', types.UnicodeText, nullable=False, default=u''),
        Column('notify_customer_after_log', types.UnicodeText, nullable=False, default=u''),
        Column('date_assigned', MaintcalDatetimeType, server_default=FetchedValue()),
        Column('creation_date', types.DateTime, server_default=FetchedValue()),
        Column('modification_date', types.DateTime, server_default=FetchedValue()),
        schema = schema_name)

service_type_table = Table('service_type', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('name', types.UnicodeText),
        Column('description', types.UnicodeText),
        Column('active', types.Boolean, nullable=False, default=True),
        Column('length', types.Interval),
        Column('lead_time', types.Interval),
        Column('maintenance_category_id', types.Integer, ForeignKey('%smaintenance_category.id' % fkey_schema_name)),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

maintenance_table = Table('maintenance_category', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('name', types.UnicodeText),
        Column('description', types.UnicodeText),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

service_server_list_table = Table('xref_scheduled_service_server_list', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('scheduled_service_id', types.Integer, ForeignKey('%sscheduled_service.id' % fkey_schema_name)),
        Column('computer_number', types.Integer, ForeignKey('%sserver_cache.id' % fkey_schema_name)),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

server_table = Table('server_cache', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('name', types.UnicodeText),
        Column('os_type', types.UnicodeText),
        Column('datacenter_symbol', types.UnicodeText),
        Column('has_managed_storage', types.Boolean),
        Column('managed_storage_type', types.UnicodeText),
        Column('has_managed_backup', types.Boolean),
        Column('attached_devices', types.UnicodeText),
        Column('is_virtual_machine', types.Boolean),
        Column('is_hypervisor', types.Boolean),
        Column('segment', types.UnicodeText),
        Column('active', types.Boolean),
        Column('icon', types.UnicodeText),
        Column('is_uk_account', types.Boolean),
        Column('is_critical_sites_device', types.Boolean),
        Column('has_openstack_role', types.Boolean),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

# Just in case we need this...
"""
ticket_table = Table('TCKT_Ticket', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('ticket_number', types.UnicodeText),
        Column('age', types.Integer),
        Column('idle', types.Integer),
        Column('assignee', types.UnicodeText),
        Column('assignee_id', types.Integer),
        Column('account_number', types.Integer),
        Column('queue_id', types.Integer),
        schema = schema_name)
"""
selector_table = Table('calendar_selector', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('calendar_id', types.Integer),
        Column('segment', types.UnicodeText),
        Column('category', types.Integer),
        Column('server_os', types.UnicodeText),
        Column('datacenter', types.UnicodeText),
        Column('has_managed_storage', types.Boolean),
        Column('managed_storage_type', types.UnicodeText),
        Column('is_virtual_machine', types.Boolean),
        Column('is_hypervisor', types.Boolean),
        Column('has_managed_backup', types.Boolean),
        Column('service_type_id', types.Integer),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        Column('attached_devices', types.Boolean),
        Column('is_uk_account', types.Boolean),
        Column('has_openstack_role', types.Boolean),
        schema = schema_name)

change_log_table = Table('change_log', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('table_id', types.Text(1)),
        Column('row_id', types.Integer),
        Column('contact', types.Text),
        Column('date', types.DateTime),
        Column('field', types.Text),
        Column('old_value', types.UnicodeText),
        Column('new_value', types.UnicodeText),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

available_defaults_table = Table('available_defaults', metadata,
        Column('id', types.Integer, primary_key = True),
        Column('calendar_id', types.Integer),
        Column('dow', types.Integer, nullable=False),
        Column('start_minutes', types.Integer, nullable=False),
        Column('end_minutes', types.Integer, nullable=False),
        Column('work_units_in_quanta', types.Integer, nullable=False),
        Column('comments', types.Text),
        Column('creation_date', types.DateTime, PassiveDefault(sql.expression._Null())),
        Column('modification_date', types.DateTime, PassiveDefault(sql.expression._Null())),
        schema = schema_name)

available_exceptions_table = Table('available_exceptions', metadata,
        Column('id', types.Integer, primary_key = True),
        Column('calendar_id', types.Integer, ForeignKey('%scalendar.id' % fkey_schema_name)),
        Column('exception_date', types.Date, nullable=False),
        Column('start_minutes', types.Integer, nullable=False),
        Column('end_minutes', types.Integer, nullable=False),
        Column('work_units_in_quanta', types.Integer, nullable=False),
        Column('comments', types.Text),
        Column('creation_date', types.DateTime, PassiveDefault(sql.expression._Null())),
        Column('modification_date', types.DateTime, PassiveDefault(sql.expression._Null())),
        schema = schema_name)

available_log_changes_table = Table('available_log_changes', metadata,
        Column('id', types.Integer, primary_key = True),
        Column('calendar_id', types.Integer, ForeignKey('%scalendar.id' % fkey_schema_name)),
        Column('dow', types.Integer),
        Column('exception_date', types.Date),
        Column('start_minutes', types.Integer, nullable=False),
        Column('end_minutes', types.Integer, nullable=False),
        Column('work_units_in_quanta', types.Integer, nullable=False),
        Column('comments', types.Text),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

scheduled_service_status_reason_table = Table('scheduled_service_status_reason', metadata,
        Column('id', types.Integer, primary_key=True),
        Column('reason', types.Text),
        Column('feedback', types.Text),
        Column('service_id', types.Integer),
        Column('creation_date', types.DateTime),
        Column('modification_date', types.DateTime),
        schema = schema_name)

recurrence_id_seq = Sequence('recurrence_id_seq', schema=schema_name)

