"""Setup the maintcal application"""
import logging

from paste.deploy import appconfig
from pylons import config

from maintcal.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup maintcal here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    
    ## Generate Models
    #from maintcal import model
    #print "Setting up DB connection..."
    #engine = config['pylons.g'].sa_engine
    #print "Creating Tables..."
    #model.metadata.create_all(bind=engine)
    #print "Tables created."
    