from maintcal.tests.lib import MaintcalUnitTest, ANY, ARGS, KWARGS
from mocker import Mocker

import xmlrpclib
from maintcal.lib import core_xmlrpc

class TestCoreXMLRPC(MaintcalUnitTest):
    
    def test_ticket_get_ticket(self):
        mocker = Mocker()
        mock_xmlrpc_ticket = mocker.mock()
        mock_xmlrpc_ticket.getTicketInfo('080111-12345')
        mocker.result({'key1':'value1', 'key2':'value2'})
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_ticket)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.replay()
        
        data = core_xmlrpc.Ticket.getTicket('080111-12345')
        self.assertEqual(data, {'key1':'value1', 'key2':'value2'})
        
        mocker.restore()
    
    def test_ticket_get_roles(self):
        mocker = Mocker()
        mock_xmlrpc_ticket = mocker.mock()
        mock_xmlrpc_ticket.getQueueRoles(1)
        mocker.result(['Admin', 'Reader'])
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_ticket)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.replay()
        
        data = core_xmlrpc.Ticket.getRoles(1)
        self.assertEqual(data, ['Admin', 'Reader'])
        
        mocker.restore()
    
    def test_ticket_create_subticket(self):
        mocker = Mocker()
        mock_xmlrpc_ticket = mocker.mock()
        mock_xmlrpc_ticket.createSubTicket(ARGS)
        mocker.result('success')
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_ticket)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.replay()
        
        data = core_xmlrpc.Ticket.createSubTicket('hi', 'bye', 2)
        self.assertEqual(data, 'success')
        
        mocker.restore()
    
    def test_ticket_add_message(self):
        mocker = Mocker()
        mock_xmlrpc_ticket = mocker.mock()
        mock_xmlrpc_ticket.addMessage(ARGS)
        mocker.result('success')
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_ticket)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.replay()
        
        data = core_xmlrpc.Ticket.addMessage('080111-12345', 'hi', 1, False, False)
        self.assertEqual(data, 'success')
        
        mocker.restore()
    
    def test_ticket_system_getTicketsStatusTypes(self):
        mocker = Mocker()
        mock_xmlrpc_system = mocker.mock()
        mock_xmlrpc_system.run('waffles', 'Ticket', 'getTicketsStatusTypes', ARGS)
        mocker.result(['Closed', 'Dormant'])
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_system)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.replay()
        
        data = core_xmlrpc.Ticket.system_getTicketsStatusTypes('080111-12345')
        self.assertEqual(data, ['Closed', 'Dormant'])
        
        mocker.restore()
    
    def test_ticket_system_updateTicketStatusTypes(self):
        mocker = Mocker()
        mock_xmlrpc_system = mocker.mock()
        mock_xmlrpc_system.run('waffles', 'Ticket', 'updateTicketStatusType', ARGS)
        mocker.result('success')
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_system)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.replay()
        
        data = core_xmlrpc.Ticket.system_updateTicketStatusType('080111-12345', 5)
        self.assertEqual(data, 'success')
        
        mocker.restore()
    
    def test_computer_getservers_one_account(self):
        mocker = Mocker()
        mock_xmlrpc_comp = mocker.mock()
        mock_xmlrpc_comp.getDetailsByAccounts([11], 1)
        mocker.result({'key1':'value1', 'key2':'value2'})
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_comp)
        mocker.count(2)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.count(2)
        mocker.replay()
        
        #data = core_xmlrpc.Computer.getServers(account=11)
        #self.assertRaises(TypeError, core_xmlrpc.Computer.getServers, account=[11])
        
        mocker.restore()
    
    def test_computer_getservers_many_accounts(self):
        mocker = Mocker()
        mock_xmlrpc_comp = mocker.mock()
        mock_xmlrpc_comp.getDetailsByAccounts([11, 12], 1)
        mocker.result([{'key1':'value1', 'key2':'value2'}, {'key1':'value1', 'key2':'value2'}])
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_comp)
        mocker.count(2)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.count(2)
        mocker.replay()
        
        #data = core_xmlrpc.Computer.getServers(accounts=[11,12])
        #self.assertRaises(TypeError, core_xmlrpc.Computer.getServers, accounts=11)
        
        mocker.restore()
    
    def test_computer_getservers_one_computer(self):
        mocker = Mocker()
        mock_xmlrpc_comp = mocker.mock()
        mock_xmlrpc_comp.getDetailsByComputers([31667], 1)
        mocker.result({'key1':'value1', 'key2':'value2'})
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_comp)
        mocker.count(2)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.count(2)
        mocker.replay()
        
        #data = core_xmlrpc.Computer.getServers(computer=31667)
        #self.assertRaises(TypeError, core_xmlrpc.Computer.getServers, computer=[31667])
        
        mocker.restore()
    
    def test_computer_getservers_many_computers(self):
        mocker = Mocker()
        mock_xmlrpc_comp = mocker.mock()
        mock_xmlrpc_comp.getDetailsByComputers([31667,31668], 1)
        mocker.result({'key1':'value1', 'key2':'value2'})
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(mock_xmlrpc_comp)
        mocker.count(2)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.count(2)
        mocker.replay()
        
        #data = core_xmlrpc.Computer.getServers(computers=[31667,31668])
        #self.assertRaises(TypeError, core_xmlrpc.Computer.getServers, computers=31668)
        
        mocker.restore()
    
    def test_computer_getservers_none(self):
        mocker = Mocker()
        mock_xmlrpclib = mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        mocker.result(None)
        mock_getauth = mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        mocker.result('ABCDEFG12345')
        mocker.replay()
        
        #data = core_xmlrpc.Computer.getServers()
        #self.assertEqual(None, data)
        
        mocker.restore()
