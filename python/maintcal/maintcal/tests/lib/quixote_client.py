"""
Interface for interacting with Quixote


NOTE:  Here is the API for the browser controller object:  ( as of nov 9, 2009 )

['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_exec_command', '_exec_test', '_method_proxy', 'assertions', 'asserts', 'browser_debugging', 'check', 'click', 'closeWindow', 'commands', 'defer', 'doubleClick', 'dragDrop', 'dragDropAbs', 'dragDropElem', 'dragDropElemToElem', 'dragDropXY', 'execIDEJS', 'execJS', 'goBack', 'goForward', 'keyDown', 'keyPress', 'keyUp', 'mouseDown', 'mouseMove', 'mouseMoveTo', 'mouseOut', 'mouseOver', 'mouseUp', 'open', 'overrideDialogs', 'radio', 'reWriteAlert', 'reWriteConfirm', 'reWritePopups', 'reWritePrompt', 'refresh', 'revertWindow', 'scroll', 'select', 'setDocDomain', 'setPromptDefault', 'setTestWindow', 'setWindowByTitle', 'show', 'storeURL', 'storeVarFromIDEJS', 'storeVarFromJS', 'storeVarFromLocAttrib', 'triggerEvent', 'type', 'waits', 'what']


"""
from pylons import config

import socket
import select
import sys

try:
    import readline
except ImportError:
    pass

#HOST = config['quixote_host']
#PORT = int(config['quixote_port'])

HOST = ""
PORT = 0

class QuixoteClient(object):

    #######################################################################
    #
    #   The API for controlling the browser
    #
    #######################################################################

    def open(self, url):
        """
        Open a url in the browser.
        """
        # This is a convenience hack for now:
        full_url = "http://devhost.core:5000/maintcal/" + url

        cmd = 'browser.open(url="%s")' % full_url
        self.do_command(cmd)

    def execIDEJS(self, js):
        """
        Eval some JS in the context of the windmill remote control window.
        """
        cmd = 'result_string = browser.execIDEJS(js="%s")' % js
        return self.do_command(cmd)

    def execJS(self, js):
        """
        Eval some JS in the context of the windmill test window.
        """
        cmd = 'result_string = browser.execJS(js="%s")' % js
        return self.do_command(cmd)

    def close_windmill_remote(self):
        """
        This will close the windmill remote window.
        Tested in firefox 3.0
        """

        cmd = 'result_string = browser.execJS(js="w1 = window.open(\'\', \'windmill_Remote\');w1.close();")'
        return self.do_command(cmd)


    def close_test_window(self):
        """
        The windmill test window is available as _w in the execJS method.

        """
        cmd = 'result_string = browser.execJS(js="_w.location=\'http://google.com\'")'
        return self.do_command(cmd)


    def interact(self):
        """
        Open a prompt to interact directly with the browser.
        """
        print "Interacting directly with browser.  Type 'quit' on a line by itself to exit."
        while True:
            cmd = raw_input("Quixote > ")    
            if cmd == 'quit':
                break
            self.do_command(cmd)

    #######################################################################
    #
    #   Connection setup and teardown methods.
    #
    #######################################################################


    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            sys.stderr.write("[ERROR] %s\n" % msg[1])
            sys.exit(1)

        try:
            self.sock.connect((HOST, PORT))
        except socket.error, msg:
            sys.stderr.write("[ERROR] %s\n" % msg[1])
            sys.exit(2)

    def disconnect(self):
        print "disconnecting"
        #self.sock.send("bye\n")
        # Send an empty string of length >0  to server so that the server will know to
        # call close on its own socket
        #self.sock.send(" ")
        self.sock.close()

    def do_command(self, cmd_string):
        """
        Send a command.
        """

        # sending a cmd_string of length zero hangs the server
        if len(cmd_string) is 0:
            return

        print "-- Sending: %s" % cmd_string 
        self.sock.send(cmd_string)
        print "-- Sent"

        return self.receive_results()

    def receive_results(self):
        """

        """
        #print "-- Receiving"

        # Block until the response starts

        inputready, outputready, exceptionready = select.select([self.sock],[],[], 10)

        string = ""

        while True:
            #print "-- about to recv"

            data = self.sock.recv(1)

            #print "-- recv'd %s" % data
            string = string + data

            # Check if more is ready
            inputready, outputready, exceptionready = select.select([self.sock],[],[], 0)

            if len(inputready) == 0:
                break


        print "-- Received: " + string
        return string

    def create_browser(self):
        """
        Create a browser client object.
        """

        # This needs to be done at some point, maybe on the server?!?
        cmd = 'setup_module(sys.modules[__name__])'
        self.do_command(cmd)

        # setup an easy way to interact with the windmill_dict
        cmd = 'wd = sys.modules[__name__].windmill_dict'
        self.do_command(cmd)

        cmd = 'httpd = wd["httpd"]'
        self.do_command(cmd)

        cmd = 'httpd_thread = wd["httpd_thread"]'
        self.do_command(cmd)

        # Create the browser
        cmd = 'browser = WindmillTestClient("Quixote")'
        self.do_command(cmd)

    def test(self):
        self.connect()

        #cmd = 'client = WindmillTestClient("t")\n'
        #self.do_command(cmd)

        #cmd = 'client.open("http://google.com")\n'
        #self.do_command(cmd)

        #self.do_command('3 + 4');
        #self.do_command('4 + 5');
        cmd = 'browser.open(url="http://devhost.core:5000/maintcal/admin_console/")'
        self.do_command(cmd)

        import time
        time.sleep(15)

        cmd = 'browser.closeWindow()'
        self.do_command(cmd)

        #self.do_command('x = start_firefox()');
        #self.do_command('x = repr(start_firefox())');
        #self.do_command('result_string = dir(x)');

        # this gives an interactive prompt
        """
        while True:
            cmd = raw_input("Quixote > ")    
            if cmd == 'quit':
                break
            self.do_command(cmd)
        """

        #self.do_command('time.sleep(5)');
        #self.do_command('x.kill()');

        #self.do_command('import time; x = start_firefox(); time.sleep(5) ; x.kill()')

        self.disconnect()

