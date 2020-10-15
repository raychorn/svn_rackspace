"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('error/:action/:id', controller='error')

    # CUSTOM ROUTES HERE
    map.connect('maintenances/durations',controller='maintenances',action='durations')

    map.connect('maintenances/set_notify_customer_before_log/:(maintenance_id)', controller='maintenances', action='set_notify_customer_before_log')
    map.connect('maintenances/set_notify_customer_after_log/:(maintenance_id)', controller='maintenances', action='set_notify_customer_after_log')

    map.connect('formatted_maintenance_times_available', 'maintenances/times_available/:(id).:(format)', controller='maintenances', action='times_available',  
        conditions=dict(method=['GET']))

    # Make sure and use map.connect BEFORE specifying map.resource for a given route
    # otherwise get calendars/selector.json will call the map.resource calendars show()
    # method with an id of "selector"
    map.connect('calendars/selector.:(format)',controller='mcalendars', action='selector')
    
    map.connect('available_defaults/:(calendar_id)', controller='available_defaults', action='index')
    map.connect('available_defaults/:(calendar_id)/update', controller='available_defaults', action='update')

    map.connect('available_exceptions/:(calendar_id)', controller='available_exceptions', action='index')
    map.connect('available_exceptions/:(calendar_id)/update', controller='available_exceptions', action='update')

    map.connect('tickets/actors_on_ticket/:(id)', controller='tickets', action='actors_on_ticket')
    map.connect('tickets/assign/:(ticket)/:(id)', controller='tickets', action='assign')

    map.resource('maintenance', 'maintenances')
    map.resource('calendar', 'calendars', controller='mcalendars')
    map.resource('service', 'services')
    map.resource('servicetype', 'servicetypes')
    map.resource('maintenancecategory', 'maintenancecategories')
    map.connect('devices/shows.:(format)',controller='devices',action='shows')
    map.resource('device', 'devices')
    map.resource('account', 'accounts')
    map.resource('ticket', 'tickets')
    #map.resource('timezone','timezones')
    map.resource('blockedtime', 'blockedtimes')
    map.resource('schedule', 'schedules')
    
    map.connect('calendars/show_calendar_info.:(format)', controller='mcalendars', action='show_calendar_info')
    map.connect('calendars/update/:id', controller='mcalendars', action='update')
    map.connect('xmlrpcproxy/:interface_name/:method_name',controller='xmlrpcproxy',action='index')
    map.connect('shared/zonenames.js', controller='timezones', action='index')
    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')

    return map
