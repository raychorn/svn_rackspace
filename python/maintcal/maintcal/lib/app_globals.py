"""The application's Globals object"""
# added bits to try out the reaper thread concept. Need to do an svn revert to undo.
import logging, traceback
import threading
from time import sleep
import datetime
from pylons import config

from maintcal.lib import core_xmlrpc

log = logging.getLogger(__name__)

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        self.Reaper = Reaper

class Reaper(threading.Thread):
    def __init__(self,interval,fun,*args,**kw):
        threading.Thread.__init__(self)
        self.interval=interval
        self.fun=fun
        self.args=args
        self.kw=kw
        self.keep_going=True
        self.event = threading.Event()
    
    def run(self):
        while(self.keep_going):
            self.event.wait(self.interval)
            if not self.event.isSet():
                try:
                    self.fun(*self.args,**self.kw)
                except Exception, err:
                    log.error("[REAPER] %s\n%s" % (err, traceback.format_exc()))
                self.event.set()
            self.event.clear()
            

    def stop_repeating(self):
        self.event.set()
        self.keep_going=False
    
