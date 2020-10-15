from maintcal.tests.lib import url_for, MaintcalFunctionalTest

from mocker import Mocker
import simplejson
from pylons import config
from maintcal.lib import core_xmlrpc
from maintcal.lib.py2extjson import py2extjson

class TestTicketsController(MaintcalFunctionalTest):

    def local_setup(self):
        sample_core_ticket = {'account_name': 'CORE',
            'account_number': 34931,
            'computers': [86964],
            'queue_id': 1,
            'ticket_number': '080101-12345'}
        self.mocker = Mocker()
        self.mock_ticket = self.mocker.replace(core_xmlrpc.Ticket)
        self.mock_ticket.getTicket('080101-12345')
        self.mocker.result(sample_core_ticket)
        self.mocker.replay()
    
    def local_teardown(self):
        self.mocker.restore()
        
    
    def testShow(self):
        response = self.app.get(url_for(controller='tickets', action='show', id='080101-12345',format='json'))
        ticket = simplejson.loads(response.body)['rows'][0]
        
        self.assertEqual(ticket['account_name'], 'CORE')
        self.assertEqual(ticket['account_number'], 34931)
        self.assertEqual(ticket['account_url'], '%s/py/core/#/account/34931' % config['core.url'])
        self.assertEqual(ticket['ticket_number'], '080101-12345')
        self.assertEqual(ticket['ticket_url'], '%s/py/ticket/view.pt?ref_no=080101-12345' % config['core.url'])
