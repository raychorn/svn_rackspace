"""
Superclass for maintcal tests.
Placeholder for functionality shared between unit and functional tests.

Note: All maintcal tests extend MockerTestCase

Manual Mocks:

    Note: We are calling any mocks done without usign Mocker a "manual mock".
            Each manual mock will have a method that does the mocking
            and that also creates a manual_mock_info dict and stores
            it in self._manualMockRegistry.  The manual_mock_info dict will
            contain enough information to remove the manual mock.
            All manual mocks will be automatically removed after each 
            individual test method inside of self.remove_manual_mocks
"""
import paste
from paste.deploy import loadapp
import os
import sys

from unittest import TestCase

from maintcal.tests import conf_dir
from maintcal.tests.lib.runner import TestRunner
from mocker import MockerTestCase, ANY, KWARGS, ARGS
from maintcal.tests.data.data_helper import DataHelper, computer_detail
from sqlalchemy.exceptions import ProgrammingError

import inspect
import simplejson
from datetime import datetime

import types

import maintcal.lib 
core_xmlrpc = maintcal.lib.core_xmlrpc

import xmlrpclib
from maintcal.model import db_sess

class MaintcalTest(MockerTestCase):
    def setUp(self):
        """
        The unittest.TestCase setUp and tearDown methods
        are used to provide application, and local setup and teardown hook
        methods.

        Individual tests can override the local setup/teardown hooks.
        """
        self.dh = DataHelper()
        self._manualMockRegistry = []
        self.application_setup() 
        self.browser_setup() 
        self.local_setup() 


    def tearDown(self):
        self.local_teardown() 
        self.browser_teardown() 
        self.application_teardown() 
        self.remove_manual_mocks()


    def remove_manual_mocks(self):
        """
        Remove all the manual monkeypatching.
        """
        for manual_mock_info in self._manualMockRegistry:
            # If we added in a named attribute that was not originally present,
            # then we remove it
            if manual_mock_info['unmock_action'] == 'del':
                #print "deleting manually mocked attribute"
                target = manual_mock_info['target'] 
                attribute_name = manual_mock_info['attribute_name']
                delattr(target, attribute_name)
            # If we added in a named attribute that was originally present,
            # then we replace the old attribute
            elif manual_mock_info['unmock_action'] == 'replace':
                #print "replacing original manually mocked attribute"
                target = manual_mock_info['target'] 
                attribute_name = manual_mock_info['attribute_name']
                old_attribute_value = manual_mock_info['old_attribute_value']
                setattr(target, attribute_name, old_attribute_value)


    def application_setup(self):
        """Default hook method."""
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
        from maintcal.tests.data.data_fixtures import init_db, clear_db, commit_db
        self.init_db = init_db
        self.insert_data = self.dh.insert_data
        self.clear_db = clear_db
        self.commit_db = commit_db
        self.init_db()

    def application_teardown(self):
        """Default hook method."""
        if TestRunner.currentTestRunner.shouldRollbackData():
            self.clear_db()
        else:
            self.commit_db()

    def browser_setup(self):
        """Used in browser tests.  Does nothing by default."""
        pass

    def browser_teardown(self):
        """Used in browser tests.  Does nothing by default."""
        pass

    def local_setup(self):
        """Default hook method."""
        self.insert_data()

    def local_teardown(self):
        """Default hook method."""
        pass

    # Test-helper stuff

    def post(self, url, params, status=None):
        """This method does a self.app.post, but can correctly handle params that are lists."""

        param_string = ''
        for key in params:
            value = params[key]
            if isinstance(value, (list, tuple)):
                for list_item_value in value:
                    param_string += '&%s=%s' % (key, list_item_value)
            else:
                param_string += '&%s=%s' % (key, value)

        if status:
            result = self.app.post(url, params=param_string, status=status)
        else:
            result = self.app.post(url, params=param_string)

        return result

    def assert400(self, response, message):
        """Assert that a response was a 400, and validates that the given message appears
        properly in the response.body"""
        target_body = '400 Bad Request\r\nThe server could not comply with the request since\r\nit is either malformed or otherwise incorrect.\r\n\r\n%s\r\n\r\n' % message
        self.assertEqual(response.status, 400)
        self.assertEqual(response.body,target_body)

    def assert500(self, response, message):
        """Assert that a response was a 500, and validates that the given message appears
        properly in the response.body"""
        target_body = '500 Internal Server Error\r\nThe server has either erred or is incapable of performing\r\nthe requested operation.\r\n\r\n%s\r\n\r\n' % message
        self.assertEqual(response.status, 500)
        self.assertEqual(response.body,target_body)

    def assertRecordCount(self, table_name, expected_count):
        query = "SELECT COUNT(*) from maintcal_test.%s" % table_name
        try:
            result = db_sess.execute(query)
        except ProgrammingError, e:
            raise ValueError("Incorrect datetime and/or timezone input.")
        actual_count = result.fetchone()[0]
        self.assertEqual(actual_count, expected_count)

    def assertNoSelectedCalendars(self, post_params):
        """ Assert that the selector found no calendars.
            The logic in the controller sets "is_error" equal to true for every calendar
            in this situation."""

        response_json = self.post('/calendars/selector.json', post_params)
        response_rows = simplejson.loads(response_json.body)['rows']

        # assert that every returned calendar id had is_error == True
        error_ids = self.getRecordIdsMatchingValue(response_rows, 'is_error', True)

        target_calendar_ids = []
        for some_dict in response_rows:
            target_calendar_ids.append(some_dict['id'])

        self.assertEqual(set(error_ids), set(target_calendar_ids))
            
    def assertSelectedCalendars(self, post_params, target_calendar_ids):
        """Run a post to calendars/selector, and assert the target calendars were chosen."""
        response_json = self.post('/calendars/selector.json', post_params)
        response_rows = simplejson.loads(response_json.body)['rows']
        actually_selected_ids = self.getRecordIdsMatchingValue(response_rows, 'is_selected', True)
        self.assertEqual(set(actually_selected_ids), set(target_calendar_ids))

    def getRecordIdsMatchingValue(self, list_of_dicts, field_name, field_value):
        """Get the ids from a list of records ( that is, dicts ) 
        where a given field_name has a given field_value."""
        results = []
        for some_dict in list_of_dicts:
            if some_dict[field_name] == field_value:
                results.append(some_dict['id'])
        return results

    # Date and Time helpers

    def safeutcnow(self):
        """ Note: /blocktimes does not use seconds or microseconds for start_time
               and end_time, so we must remove them here."""
        return self.safetznow()

    def safetznow(self):
        """ Note: /blocktimes does not use seconds or microseconds for start_time
               and end_time, so we must remove them here."""
        from maintcal.lib.date import get_database_utc_now
        db_utc_now = get_database_utc_now()
        return db_utc_now.to_python_datetime()

    def safenowseconds(self):
        """Returns the safenow in seconds since the epoch."""
        return self.safetznow().strftime("%s")

    # Manual mocks

    def mockAuthToken(self):
        """
        """
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.count(0,None)
        self.mocker.replay()


    def manuallyMockFakeAttribute(self, target, attribute_name, new_attribute_value):
        """
            Mock out an attribute that is determined through dynamic attribute lookup.

            Note:  We are mocking an attribute that does not exist.  The normal behavior
            of the target is to use __getattr__ to implement the fake attribute.
            Therefore all we have to do to mock is to create the named attribute.
            In the same way, all we have to do to unmock is to delete our named
            attribute, and the original behavior will work automatically again."""

        # If we need a reference to the original attribute that is found dynamically,
        # we can use the following two lines:
        # x = target()
        # old_attribute_value = target.__getattr__(x, attribute_name)

        manual_mock_info = {}
        manual_mock_info['target'] = target
        manual_mock_info['attribute_name'] = attribute_name
        manual_mock_info['unmock_action'] = 'del'
        self._manualMockRegistry.append(manual_mock_info)

        setattr(target, attribute_name, new_attribute_value)


    def manuallyMockRealClassAttribute(self, target, attribute_name, new_attribute_value):
        """
            Mock out a named class attribute that actually exists, not a named class
            attribute that is determined through dynamic class lookup.
        
            We must store a reference to the original attribute value so that we
            can unmock the attribute properly."""

        old_attribute_value = target.__getattribute__(target, attribute_name)

        manual_mock_info = {}
        manual_mock_info['target'] = target
        manual_mock_info['attribute_name'] = attribute_name
        manual_mock_info['unmock_action'] = 'replace'
        manual_mock_info['old_attribute_value'] = old_attribute_value
        self._manualMockRegistry.append(manual_mock_info)

        setattr(target, attribute_name, new_attribute_value)


    def mockTicketGetInfoForTickets(self):
        """Mock out the call to Ticket.getInfoForTickets to avoid an annoying
        xmlrpc call."""
        def mockedGetInfoForTickets(self, ticket_numbers):
            return {}
        self.manuallyMockFakeAttribute(xmlrpclib.Server, 'getInfoForTickets', mockedGetInfoForTickets)


    def mockServerGetDetailsByComputers(self):
        """Note: we are mocking an attribute that does not exist.  The normal behavior
           of xmlrpclib is to use __getattr__ to implement the fake attribute.
           Therefore all we have to do to mock is to create the named attribute.
           In the same way, all we have to do to unmock is to delete our named
           attribute, and the original behavior will work automatically again."""

        def mockedGetDetailsByComputers(self, list_of_computer_numbers, lowerBoundStatus):
            results = []
            for computer_number in list_of_computer_numbers:
                try:
                    results.append(computer_detail[computer_number])
                except KeyError:
                    pass
            return results

        self.manuallyMockFakeAttribute(xmlrpclib.Server, 'getDetailsByComputers', mockedGetDetailsByComputers)

    def mockServerGetDetailsByAccounts(self):
        """Note: we are mocking an attribute that does not exist.  The normal behavior
           of xmlrpclib is to use __getattr__ to implement the fake attribute.
           Therefore all we have to do to mock is to create the named attribute.
           In the same way, all we have to do to unmock is to delete our named
           attribute, and the original behavior will work automatically again."""
        def mockedGetDetailsByAccounts(self, list_of_account_numbers, lower_status=None,
            page=0, limit=100, sort_field='number', exclude_items=()):
            results = []
            for account_number in list_of_account_numbers:
                matches = [computer_detail[computer_number] for computer_number in computer_detail if computer_detail[computer_number]['customer'] == unicode(account_number)]
                results.extend(matches)

            start_index = 0
            end_index = limit
            if page > 0:
                start_index = page * limit
                end_index = start_index + limit

            return results[start_index:end_index]

        self.manuallyMockFakeAttribute(xmlrpclib.Server, 'getDetailsByAccounts', mockedGetDetailsByAccounts)

    def mockTicketGetTicket(self):
        @classmethod
        def mockedGetTicket(cls, ticket_number):
            rdict = {}

            rdict['ticket_number'] = u''
            rdict['assignee'] = u''
            rdict['assignee_id'] = u''
            rdict['account_number'] = 11
            rdict['account_name']  = u''
            rdict['computers'] = u''
            rdict['queue_id'] = u''

            #rdict['ticket_number'] = ticket.number
            #rdict['assignee'] = str(ticket.assignee or '')
            #rdict['assignee_id'] = (ticket.assignee and ticket.assignee.id) or ''
            #rdict['account_number'] = (ticket.account and int(ticket.account.number)) or ''
            #rdict['account_name']  = (ticket.account and ticket.account.name) or ''
            #rdict['computers'] = [comp.number for comp in ticket.computers]
            #rdict['queue_id'] = ticket.queue.id 

            return rdict

        self.manuallyMockRealClassAttribute(core_xmlrpc.Ticket, 'getTicket', mockedGetTicket)

    def mockTicketAddMessage(self):
        @classmethod
        def mockedAddMessage(cls, ticket_number, body, contact_id, is_private, send_email):
            #core_ticket = xmlrpclib.Server("%s/Ticket/::session_id::%s" % (config.get('core.xmlrpc_url'), get_auth_token()))
            #return core_ticket.addMessage(ticket_number, body, contact_id, is_private, send_email)
            return True

        self.manuallyMockRealClassAttribute(core_xmlrpc.Ticket, 'addMessage', mockedAddMessage)

    def mockTicketCreateSubTicket(self):
        @classmethod
        def mockedCreateSubTicket(cls, *args):
            """
            Note: this should return a ticket number.
            """
            #core_ticket = xmlrpclib.Server("%s/Ticket/::session_id::%s" % (config.get('core.xmlrpc_url'), get_auth_token()))
            #return core_ticket.addMessage(ticket_number, body, contact_id, is_private, send_email)
            ticket_number = '12345-200901011201'
            return ticket_number

        self.manuallyMockRealClassAttribute(core_xmlrpc.Ticket, 'createSubTicket', mockedCreateSubTicket)


    def mockTicketSystemUpdateTicketStatusType(self):
        """System auth's as system"""
        @classmethod
        def mockedTicketSystemUpdateTicketStatusType(cls, ticket_number, status_type, unassign=True):
            #core_ticket = xmlrpclib.Server("%s/Ticket/::session_id::%s" % (config.get('core.xmlrpc_url'), get_auth_token()))
            #return core_ticket.addMessage(ticket_number, body, contact_id, is_private, send_email)
            return True
 
        self.manuallyMockRealClassAttribute(core_xmlrpc.Ticket, 'system_updateTicketStatusType', 
                mockedTicketSystemUpdateTicketStatusType)

    def broken_test(self):
        """Quick way to mark a test as disabled"""
        test_method_stack_frame = inspect.stack()[1]
        TestRunner.currentTestRunner.addDisabledTestWarning(test_method_stack_frame)

