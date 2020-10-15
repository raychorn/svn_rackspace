from maintcal.tests.lib import MaintcalUnitTest, ANY, ARGS, KWARGS

import xmlrpclib
from maintcal.lib import core_xmlrpc

class TestCoreXMLRPC(MaintcalUnitTest):

    #########################################################################################################################
    ### These two methods have been reworked. They're a lot different from yours. Check them out.                         ###
    ### The problem is almost certainly with test.ini. I can run this suite of tests with nostests and get no problem.    ###
    ### Things only start exploding when running nosetests against multiple suites, including one that requires test.ini. ###
    #########################################################################################################################
    def test_ticket_system_getTicketsStatusTypes(self):
        mock_core_xmlrpc_system = self.mocker.replace(core_xmlrpc.System)
        self.mocker.on(mock_core_xmlrpc_system.run('Ticket', 'getTicketsStatusTypes', '080111-12345')).result(['Closed', 'Dormant'])

        self.mocker.replay()
        
        data = core_xmlrpc.Ticket.system_getTicketsStatusTypes('080111-12345')
        self.assertEqual(data, ['Closed', 'Dormant'])
        self.mocker.reset()

    
    def test_ticket_system_updateTicketStatusTypes(self):
        mock_core_xmlrpc_system = self.mocker.replace(core_xmlrpc.System)
        self.mocker.on(mock_core_xmlrpc_system.run('Ticket', 'updateTicketStatusType', '080111-12345', 5, True)).result('success')
        
        self.mocker.replay()
        
        data = core_xmlrpc.Ticket.system_updateTicketStatusType('080111-12345', 5)
        self.assertEqual(data, 'success')




    def test_ticket_get_ticket(self):
        mock_xmlrpc_ticket = self.mocker.mock()
        mock_xmlrpc_ticket.getTicketInfo('080111-12345')
        self.mocker.result({'key1':'value1', 'key2':'value2'})
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_ticket)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.replay()
        
        data = core_xmlrpc.Ticket.getTicket('080111-12345')
        self.assertEqual(data, {'key1':'value1', 'key2':'value2'})
            
    def test_ticket_get_roles(self):
        
        mock_xmlrpc_ticket = self.mocker.mock()
        mock_xmlrpc_ticket.getQueueRoles(1)
        self.mocker.result(['Admin', 'Reader'])
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_ticket)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.replay()
        
        data = core_xmlrpc.Ticket.getRoles(1)
        self.assertEqual(data, ['Admin', 'Reader'])
        
        
    
    def test_ticket_create_subticket(self):
        
        mock_xmlrpc_ticket = self.mocker.mock()
        mock_xmlrpc_ticket.createSubTicket(ARGS)
        self.mocker.result('success')
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_ticket)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.replay()
        
        data = core_xmlrpc.Ticket.createSubTicket('hi', 'bye', 2)
        self.assertEqual(data, 'success')
        
        
    
    def test_ticket_add_message(self):
        
        mock_xmlrpc_ticket = self.mocker.mock()
        mock_xmlrpc_ticket.addMessage(ARGS)
        self.mocker.result('success')
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_ticket)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.replay()
        
        data = core_xmlrpc.Ticket.addMessage('080111-12345', 'hi', 1, False, False)
        self.assertEqual(data, 'success')        
        
    
    def test_computer_getservers_one_account(self):
        
        mock_xmlrpc_comp = self.mocker.mock()
        mock_xmlrpc_comp.getDetailsByAccounts([11], 1)
        self.mocker.result({'key1':'value1', 'key2':'value2'})
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_comp)
        self.mocker.count(2)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.count(2)
        self.mocker.replay()
        
        data = core_xmlrpc.Computer.getServers(account=11)
        self.assertRaises(TypeError, core_xmlrpc.Computer.getServers, account=[11])
        
        
    
    def test_computer_getservers_many_accounts(self):
        
        mock_xmlrpc_comp = self.mocker.mock()
        mock_xmlrpc_comp.getDetailsByAccounts([11, 12], 1)
        self.mocker.result([{'key1':'value1', 'key2':'value2'}, {'key1':'value1', 'key2':'value2'}])
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_comp)
        self.mocker.count(2)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.count(2)
        self.mocker.replay()
        
        data = core_xmlrpc.Computer.getServers(accounts=[11,12])
        self.assertRaises(TypeError, core_xmlrpc.Computer.getServers, accounts=11)
        
        
    
    def test_computer_getservers_one_computer(self):
        
        mock_xmlrpc_comp = self.mocker.mock()
        mock_xmlrpc_comp.getDetailsByComputers([31667], 1)
        self.mocker.result({'key1':'value1', 'key2':'value2'})
        self.mocker.count(1)
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_comp)
        self.mocker.count(2)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.count(2)
        self.mocker.replay()
        
        data = core_xmlrpc.Computer.getServers(computer=31667)
        self.assertRaises(TypeError, core_xmlrpc.Computer.getServers,computer='foo')
        
    def blah(self):
        raise TypeError()
        
    
    def test_computer_getservers_many_computers(self):
        
        mock_xmlrpc_comp = self.mocker.mock()
        mock_xmlrpc_comp.getDetailsByComputers([31667,31668], 1)
        self.mocker.result({'key1':'value1', 'key2':'value2'})
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(mock_xmlrpc_comp)
        self.mocker.count(2)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.count(2)
        self.mocker.replay()
        
        data = core_xmlrpc.Computer.getServers(computers=[31667,31668])
        self.assertRaises(TypeError, core_xmlrpc.Computer.getServers, computers=31668)
        
        
    
    def test_computer_getservers_none(self):
        mock_xmlrpclib = self.mocker.replace(xmlrpclib)
        mock_xmlrpclib.Server(ARGS)
        self.mocker.result(None)
        self.mocker.count(0,None)
        mock_getauth = self.mocker.replace('maintcal.lib.core_xmlrpc.get_auth_token')
        mock_getauth()
        self.mocker.result('ABCDEFG12345')
        self.mocker.count(0,None)
        self.mocker.replay()
        
        data = core_xmlrpc.Computer.getServers()
        self.assertEqual(None, data)
