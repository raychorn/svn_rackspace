from maintcal.tests.data.generated_data import computer_detail

# This is a dict of machines that we want to preserve for our tests
# even if the machines are removed from core.
# We are preserving them here so that they will be preserved even 
# if computer_detail_data is recreated.
frozen_computers = {110912: {'account_manager': u'Heather Arrington',
          'account_manager_id': 69667,
          'attached_devices': [],
          'business_development': u'Steven Gillig',
          'business_development_id': 55217,
          'customer': u'654546',
          'customer_name': u'Oberon Media',
          'customer_type': u'External Customer',
          'datacenter': u'DFW1',
          'due_date': u'2007-02-13 13:24:43.000',
          'emergency_instructions': u'',
          'gateway': u'72.3.137.241/28',
          'has_managed_backup': False,
          'has_managed_storage': False,
          'icon': u'/img/minicon/product/hp_win.gif',
          'is_hypervisor': False,
          'is_virtual_machine': False,
          'is_uk_account' : False,
          'is_critical_sites_device' : False,
          'lead_tech': u'',
          'lead_tech_id': 0,
          'managed_storage_type': [],
          'non_networked_net_devices': [],
          'offline_date': u'None',
          'online_date': u'2007-02-01 17:19:12.000',
          'os': u'Windows Server 2003',
          'os_group': u'Microsoft Windows',
          'platform': u'HP DL385 WIN2K3',
          'platform_model': u'2U Case',
          'port': u'DFW1:<LocationManager.Port.dummy_switch object at 0xb614532c>[no port_num]',
          'primary_ip': u'72.3.137.249',
          'segment': u'Intensive',
          'server': 110912,
          'server_name': u'MPSVR07.pps.local',
          'status': u'Online/Complete',
          'status_number': 12,
          'team': u'Team C1'},
 110914: {'account_manager': u'Heather Arrington',
          'account_manager_id': 69667,
          'attached_devices': [],
          'business_development': u'Steven Gillig',
          'business_development_id': 55217,
          'customer': u'654546',
          'customer_name': u'Oberon Media',
          'customer_type': u'External Customer',
          'datacenter': u'DFW1',
          'due_date': u'2007-02-13 13:24:43.000',
          'emergency_instructions': u'',
          'gateway': u'72.3.137.241/28',
          'has_managed_backup': True,
          'has_managed_storage': False,
          'icon': u'/img/minicon/product/hp_win.gif',
          'is_hypervisor': False,
          'is_virtual_machine': False,
          'is_uk_account' : False,
          'is_critical_sites_device' : False,
          'lead_tech': u'',
          'lead_tech_id': 0,
          'managed_storage_type': [],
          'non_networked_net_devices': [],
          'offline_date': u'None',
          'online_date': u'2007-02-01 17:19:43.000',
          'os': u'Windows Server 2003',
          'os_group': u'Microsoft Windows',
          'platform': u'HP DL385 WIN2K3',
          'platform_model': u'2U Case',
          'port': u'DFW1:<LocationManager.Port.dummy_switch object at 0xb613c3ac>[no port_num]',
          'primary_ip': u'72.3.137.250',
          'segment': u'Intensive',
          'server': 110914,
          'server_name': u'domain1.pps.local',
          'status': u'Online/Complete',
          'status_number': 12,
          'team': u'Team C1'},
 110945: {'account_manager': u'Heather Arrington',
          'account_manager_id': 69667,
          'attached_devices': [],
          'business_development': u'Steven Gillig',
          'business_development_id': 55217,
          'customer': u'654546',
          'customer_name': u'Oberon Media',
          'customer_type': u'External Customer',
          'datacenter': u'SAT1',
          'due_date': u'2007-02-13 13:24:44.000',
          'emergency_instructions': u'',
          'gateway': u'',
          'has_managed_backup': False,
          'has_managed_storage': False,
          'icon': u'/img/minicon/product/managed_backup.gif',
          'is_hypervisor': False,
          'is_virtual_machine': False,
          'is_uk_account' : False,
          'is_critical_sites_device' : False,
          'lead_tech': u'',
          'lead_tech_id': 0,
          'managed_storage_type': ['DAS'],
          'non_networked_net_devices': [],
          'offline_date': u'None',
          'online_date': u'2007-02-01 17:26:33.000',
          'os': u'Red Hat Enterprise Linux 5 - 64 bit',
          'os_group': u'Linux',
          'platform': u'HP ProLiant DL380 G5 Linux',
          'platform_model': u'HP ProLiant DL380 G5 Linux Required',
          'port': u'DFW1:<LocationManager.Port.dummy_switch object at 0xb62ef0ac>[no port_num]',
          'primary_ip': u'',
          'segment': u'Managed',
          'server': 110945,
          'server_name': u'mbu.pps.local',
          'status': u'Online/Complete',
          'status_number': 12,
          'team': u'Team C1'}
}

# combine our frozen data with the generated data
computer_detail.update(frozen_computers)

class NamedServers(object):
    """ This class provides an easy way to write tests in terms of the names
        of the servers instead of specific ids."""

    well_known_servers = dict(
            sat1_managed_linux_managed_storage_one=110945, # in SAT1, managed segment
            managed_backup_device_one=112412,
            managed_linux_one=220587                # this should trigger the managed unix calendar
    )

    def __getattr__(self, machine_name):
        """Get the dict of info for the given machine."""
        return computer_detail[self.well_known_servers[machine_name]]
    
# For more informative testing
calendars_by_name = {} 

test_calendars = {}

def calendar_names_to_ids(*args):
    """Clean way to specify some calendars by their names and get a list
    of their ids."""
    ids = []
    for name in args:
        ids.append(calendars_by_name[name])
    return ids

def server_names_to_ids(*args):
    """Clean way to specify some servers by their names and get a list
    of their ids."""
    ids = []
    for name in args:
        ids.append(getattr(named_servers, name)['server'])
    return ids

# provide one well-known instance
named_servers = NamedServers()
