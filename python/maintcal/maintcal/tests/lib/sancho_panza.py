"""
Superclass for maintcal browser tests.

"""
from maintcal_test import MaintcalTest
from quixote_client import QuixoteClient

from paste import httpserver
from paste.deploy import loadapp
from maintcal.tests import conf_dir

import os
import sys
import signal

        
import thread
import threading
import datetime


        
class SanchoPanza_threaded(threading.Thread):
    """
    This copy should have its own special copy of httpserver,
    that can be remotely controlled
    """
    def __init__(self, app, host, port, test):
        threading.Thread.__init__(self)
        self.app = app
        self.host = host
        self.port = port
        self.test = test

        self.cmds_to_exec = []

    def run(self):
        print "run 1"
        self.server = httpserver.serve(self.app, host=self.host, port=self.port, start_loop=False)

        # The following block of code can be used to exec arbitrary commands
        # in the context of the httpserver thread.
        # It is not currently needed
        """
        sancho_panza = self

        self.server.old_handle_request = self.server.handle_request
        
        # I have no clue why it complains if I define this method to take self as an arg

        def new_handle_request():
            # Handle any pending requests
            if len(sancho_panza.cmds_to_exec):
                cmd = sancho_panza.cmds_to_exec.pop()
                print "sancho_panza.py is in %s " % thread.get_ident()    
                print "Sancho Panza exec'ing command: %s" % cmd
                # the globals() locals() stuff is necessary
                exec cmd in globals(), locals()
                print "Done."

            # dispatch to the original method
            sancho_panza.server.old_handle_request()

        setattr(self.server, 'handle_request', new_handle_request)
        """

        print "run 2"
        self.server.serve_forever()
        print "run 3"

    def exec_cmd(self, cmd):
        """Run a command in the context of this thread."""

        self.cmds_to_exec.append(cmd)
        print "command added to queue"
        

    def stop(self):
        print "kill the windmill!"
        self.server.running = False
        self.join()


class SanchoPanza_forking(object):
    """
    Sancho panza can launch and control a webserver for a pylons app.
    """
    def __init__(self, app, host, port):
        self.app = app
        self.host = host
        self.port = port

    def start(self):
        self.pid = os.fork()
        if not self.pid:
            # we are the child
            httpserver.serve(self.app, host=self.host, port=self.port)
            sys.exit(0)
        else:
            # we are the parent
            pass

    def stop(self):
        print "kill the windmill!"
        os.kill(self.pid, signal.SIGKILL)
        killedpid, stat = os.waitpid(self.pid, 0)
        if killedpid == 0:
            print "ACK! PROCESS NOT KILLED?"

SanchoPanza = SanchoPanza_threaded
