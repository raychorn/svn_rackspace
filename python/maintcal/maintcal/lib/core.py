#!/usr/bin/env python

# CORE configuration helper
def parse_config(app_conf, prefix='core'):
    DEFAULT_ACCOUNT_PAGE = '/py/core/#/account/'
    DEFAULT_SERVER_PAGE = '/py/core/#/device/'
    DEFAULT_TICKET_PAGE = '/py/ticket/view.pt?ref_no='
    DEFAULT_XMLRPC_PAGE = '/xmlrpc'
    
    if not prefix.endswith('.'):
        prefix = "%s." % prefix
    core_dict = {}
    for conf in app_conf.keys():
        if conf.startswith(prefix):
            core_dict[conf[len(prefix):]] = app_conf[conf]
    
    if 'url' in core_dict.keys():
        core_url = core_dict['url']
    else:
        core_url = 'https://core.redacted.com'
        core_dict['url'] = core_url
    
    if 'account_url' not in core_dict.keys():
        core_dict['account_url'] = "%s%s" % (core_url, (core_dict.get('account_page') or DEFAULT_ACCOUNT_PAGE))
    
    if 'server_url' not in core_dict.keys():
        core_dict['server_url'] =  "%s%s" % (core_url, (core_dict.get('server_page') or DEFAULT_SERVER_PAGE))
    
    if 'ticket_url' not in core_dict.keys():
        core_dict['ticket_url'] =  "%s%s" % (core_url, (core_dict.get('ticket_page') or DEFAULT_TICKET_PAGE))
    
    if 'xmlrpc_url' not in core_dict.keys():
        core_dict['xmlrpc_url'] = "%s%s" % (core_url, (core_dict.get('xmlrpc_page') or DEFAULT_XMLRPC_PAGE))
    
    if 'cookie_name' not in core_dict.keys():
        core_dict['cookie_name'] = "redacted_admin_session"
    
    for k in core_dict.keys():
        app_conf['%s%s' % (prefix, k)] = core_dict[k]
