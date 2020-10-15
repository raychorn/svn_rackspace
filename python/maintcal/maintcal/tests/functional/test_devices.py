from maintcal.tests.lib import url_for, MaintcalFunctionalTest

import simplejson
from mocker import Mocker,KWARGS
from pylons import config

from maintcal.tests.data.data_helper import computer_detail
from maintcal.lib.core_xmlrpc import Computer, Ticket
from maintcal.controllers import devices

class TestDevicesController(MaintcalFunctionalTest):
    """We are testing the controller through the database back to the response."""

    def local_setup(self):
        self.mockAuthToken()
        self.mockServerGetDetailsByAccounts()
        self.mockServerGetDetailsByComputers()
        self.mocker.replay()
        return        
        sample_core_computer = [computer_detail['110912']]
        sample_core_multi_computer = [computer_detail['110914'],computer_detail['110912']]
        sample_core_ticket = {'account_name': u'CORE',
            'account_number': 654546,
            'computers': [110912],
            'queue_id': 1,
            'ticket_number': '080101-12345'}
        
        self.mocker = Mocker()
        self.mock_core = self.mocker.replace(Computer)
        self.mock_core.getServers(computer=110912)
        self.mocker.result(sample_core_computer)
        self.mock_core.getServers(account=654546)
        self.mocker.result(sample_core_multi_computer)
        self.mock_core.getServers(computers=[110912])
        self.mocker.result(sample_core_computer)
        self.mock_ticket = self.mocker.replace(Ticket)
        self.mock_ticket.getTicket(ticket_number='080101-12345')
        self.mocker.result(sample_core_ticket)
        self.mocker.count(0,2)
        self.mocker.replay()
    
    def local_teardown(self):
        self.mocker.reset()
    
    def test_index(self):
        response = self.app.get(url_for(controller='devices'))
        # Test response...
    
    def test_index_account_json_no_paging(self):
        """Calling index with an account parameter should return a list of servers for that account"""
        response = self.app.get('/devices.json', params={'account':654546})
        self.assertEqual(response.status, 200)
        
        servers = simplejson.loads(response.body)['rows']
        self.assert_(110912 in [s['id'] for s in servers], "Computer 110912  should be in account 654546")

    def test_index_account_json_paging(self):
        """Calling index with an account parameter should return a list of servers for that account"""
        response = self.app.get('/devices.json', params={'account':654546, 'page':1, 'limit':2})
        self.assertEqual(response.status, 200)
        servers = simplejson.loads(response.body)['rows']
        self.assertEqual([117783, 123549], [s['id'] for s in servers])

    def test_index_account_json_bad_page(self):
        response = self.app.get(url_for(controller='devices', format='json'), params={'account': 654546,'page':'bobob','limit':100},status=500)
        self.assertEqual(response.status,500)
        self.assertEqual(response.body, '500 Internal Server Error\r\nThe server has either erred or is incapable of performing\r\nthe requested operation.\r\n\r\nGot invalid page and or limit arguments for this request\r\n\r\n')

    def test_index_account_json_bad_limit(self):
        response = self.app.get(url_for(controller='devices', format='json'), params={'account':654546,'page':2,'limit':'janel'},status=500)
        self.assertEqual(response.status,500)
        self.assertEqual(response.body, '500 Internal Server Error\r\nThe server has either erred or is incapable of performing\r\nthe requested operation.\r\n\r\nGot invalid page and or limit arguments for this request\r\n\r\n')

    def test_index_account_no_devices(self):
        """Test an account with no devices attached to it."""
        response = self.app.get(url_for(controller='devices',format='json'),
            params={'account':87678},status=404)
        self.assertEqual(response.status,404)
        self.assert_("Account has no devices associated with it." in response.body)
 
    def test_show_json(self):
        """Fetch a valid device number from CORE that is cached
        
            In the case of these tests, a device is cached if it was inserted
            by tests/data/data_fixtures.py by the insert_data function.
        """
        response = self.app.get(url_for(controller='devices', action='show', id=110912, format='json'))
        self.assertEqual(response.status, 200)

        detail = computer_detail[110912]
        server = simplejson.loads(response.body)['rows'][0]
        self.assertEqual(server['os'], detail['os_group'])
        self.assertEqual(server['has_managed_storage'], detail['has_managed_storage'])
        self.assertEqual(server['datacenter'], detail['datacenter'])
        self.assertEqual(server['segment'], detail['segment'])
        self.assertEqual(server['icon'], config['core.url'] + '/' + detail['icon']) 
    
    def test_show_fetch_from_core(self):
        """Fetch a valid device number from CORE that is not cached

            In the case of these tests, a device is not cached if it was NOT inserted
            by tests/data/data_fixtures.py by the insert_data function.
        """
        response = self.app.get(url_for(controller='devices', action='show', id=241910, format='json'))
        self.assertEqual(response.status, 200)
        detail = computer_detail[241910]
        server = simplejson.loads(response.body)['rows'][0]
        self.assertEqual(server['os'], detail['os_group'])
        self.assertEqual(server['has_managed_storage'], detail['has_managed_storage'])
        self.assertEqual(server['datacenter'], detail['datacenter'])
        self.assertEqual(server['segment'], detail['segment'])
        self.assertEqual(server['icon'], config['core.url'] + '/' + detail['icon']) 

    # TODO: make a test for devices/shows


