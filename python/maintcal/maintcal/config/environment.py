"""Pylons environment configuration"""
import os

from pylons import config
from sqlalchemy import engine_from_config

import maintcal.lib.app_globals as app_globals
import maintcal.lib.helpers
from maintcal.lib import normalize
from maintcal.config.routing import make_map

from maintcal.lib import json_tz, core
#from maintcal.controllers import periodic_update

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='maintcal',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.g'] = app_globals.Globals()
    config['pylons.g'].sa_engine = engine_from_config(config, 'sqlalchemy.')
    config['pylons.h'] = maintcal.lib.helpers

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']
    
    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    #config['core.acct_url'] = "%s%s" % (config['core_url'], config['core_acct_page'])
    #config['core.server_url'] = "%s%s" % (config['core_url'],config['core_server_page'])
    #config['core.ticket_url']  = "%s%s" % (config['core_url'], config['core_ticket_page'])
    #config['core.ticket_url']  = "%s%s" % (config['core_url'], config['core_ticket_page'])
    #core.parse_config(global_conf)
    config['admin_departments'] = ['CORE', 'MCAL_ADMIN']
    if config.get('authkit.setup.enable'):
        if config['authkit.setup.enable'].lower() == 'false':
            config['use_auth'] = False
        else:
            config['use_auth'] = True
    else:
        config['use_auth'] = True
    core.parse_config(config)
    
    # Enable change log
    enable_change_log = config.get('enable_changelog')
    if enable_change_log and enable_change_log.lower() == 'true':
        config['enable_changelog'] = True
    else:
        config['enable_changelog'] = False
    
    # Create zonenames.js
    if (not config.get('init_tz_file')) or normalize.normalize_boolean(config.get('init_tz_file')):
        json_tz.gen_zonenamesjs()
        config['zonenamejs_file'] = "%s/%s" % (config['cache.dir'], json_tz.JSFILE)
        config['timezone.abbr_dict'] = json_tz.tzfile.get_abbr_dict()
    else:
        config['zonenamejs_file'] = ""
        config['timezone.abbr_dict'] = {}
    
    # Reaper
    if config.get('start_reaper') and config['start_reaper'].lower() == 'true':
        from maintcal.lib import periodic_update
        config['reaper_thread'] = config['pylons.g'].Reaper(int(config['calendar_granularity_seconds']), periodic_update.PeriodicUpdate.run_all)
        config['reaper_thread'].start()
        #pass

    # Calculator debug config
    if config.has_key('calculator_calendars'):
        config['calculator_calendars'] = [int(cal_id) for cal_id in config['calculator_calendars'].split(',')]
    else:
        config['calculator_calendars'] = []
