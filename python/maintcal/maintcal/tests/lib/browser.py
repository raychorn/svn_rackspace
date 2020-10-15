"""
Superclass for maintcal browser tests.

This class defines the API for the browser tests

"""
from maintcal_test import MaintcalTest
#from quixote_client import QuixoteClient

from paste import httpserver
from paste.deploy import loadapp
from maintcal.tests import conf_dir

import sys

from sancho_panza import SanchoPanza

from maintcal.tests.lib.selenium import selenium

# for debugging
from maintcal.model import db_sess, Calendar

from pylons import config

HOST = config['selenium_rc_server_host']
PORT = config['selenium_rc_server_port']

class MaintcalBrowserTest(MaintcalTest):

    #def __init__(self):
    #    MaintcalTest.__init__(self)
    #    #self.q = QuixoteClient()
    #    pass


    def assert_contains(self, search_text):
        """
        Assert that the html page contains
        the given text.
        """
        # get the html for the page
        body_innerhtml = self.q.execJS("window.document.body.innerHTML")
        found = search_text in body_innerhtml
        self.assertTrue(found)



    #######################################################################
    #
    #   Methods to handle default setup and teardown behavior.
    #
    #######################################################################
       
    def demo_go_to_google(self):
        sel = self.s
        sel.open("http://devhost.core:5000/maintcal/admin_console")
        #sel.type("q", "hello world")
        #sel.click("btnG")
        sel.wait_for_page_to_load(5000)
        #self.assertEqual("hello world - Google Search", sel.get_title())
        import time
        time.sleep(5)
    
    def browser_setup(self):
        """Used in browser tests.  Does nothing by default."""

        #self.q = QuixoteClient()
        #self.q.connect()
        #self.q.create_browser()

        self.s = selenium(HOST, PORT, "*firefox", "http://www.google.com/webhp")
        self.s.start()
 
        #import time
        #print "waiting"
        #time.sleep(15)
        #print "done waiting"

    def local_setup(self):
        self.insert_data()

        #self.q.test()

    def browser_teardown(self):
        """Used in browser tests.  Does nothing by default."""
        print "-- close down browser connection"
        self.s.stop()

        print "-- close down maintcal server in sancho_panza"
        self.sancho_panza.stop()

    def application_setup(self):
        """Default hook method."""

        from maintcal.tests.data.data_fixtures import init_db, clear_db, commit_db
        self.init_db = init_db
        self.insert_data = self.dh.insert_data
        self.clear_db = clear_db
        self.commit_db = commit_db
        self.init_db()

        wsgiapp = loadapp('config:browsertest.ini', relative_to=conf_dir)

        # Accept connections from anywhere
        self.sancho_panza = SanchoPanza(wsgiapp, '0.0.0.0', '5000', self)
        self.sancho_panza.start()
        print "Sancho Panza serving on 0.0.0.0 port 5000 using browsertest.ini"

        #import thread
        #print "browser.py is in %s " % thread.get_ident()    
        #self.sancho_panza.exec_cmd('sancho_panza.test.init_db()')
        #self.sancho_panza.exec_cmd('sancho_panza.test.insert_data()')

