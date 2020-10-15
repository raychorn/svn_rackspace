import logging
import xmlrpclib

from maintcal.lib.base import *
from maintcal.lib import core_xmlrpc, py2extjson

log = logging.getLogger(__name__)

class AccountsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('account', 'accounts')


    def index(self, format='html'):
        """GET /accounts: All items in the collection."""
        # url_for('accounts')
        if request.params.get('ticket_number'):
            try:
                ticket_info = core_xmlrpc.Ticket.getTicket(request.params['ticket_number'])
            except core_xmlrpc.NotAuthenticatedException:
                abort(401, "Please log into CORE")
            except xmlrpclib.Fault:
                abort(404,"Could not get ticket information")

            rdict = { 'number' : ticket_info['account_number'], 'name' : ticket_info['account_name']}
            if format=='json':
                return py2extjson(rdict)
            return str(rdict)
        
        return ''

    def create(self):
        """POST /accounts: Create a new item."""
        # url_for('accounts')
        pass

    def new(self, format='html'):
        """GET /accounts/new: Form to create a new item."""
        # url_for('new_account')
        pass

    def update(self, id):
        """PUT /accounts/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('account', id=ID),
        #           method='put')
        # url_for('account', id=ID)
        pass

    def delete(self, id):
        """DELETE /accounts/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('account', id=ID),
        #           method='delete')
        # url_for('account', id=ID)
        pass

    def show(self, id, format='html'):
        """GET /accounts/id: Show a specific item."""
        # url_for('account', id=ID)
        pass

    def edit(self, id, format='html'):
        """GET /accounts/id;edit: Form to edit an existing item."""
        # url_for('edit_account', id=ID)
        pass
