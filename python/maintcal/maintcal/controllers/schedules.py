import logging

from maintcal.lib.base import *

log = logging.getLogger(__name__)

class SchedulesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('schedule', 'schedules')


    def index(self, format='html'):
        """GET /schedules: All items in the collection."""
        # url_for('schedules')
        pass

    def create(self):
        """POST /schedules: Create a new item."""
        # url_for('schedules')
        pass

    def new(self, format='html'):
        """GET /schedules/new: Form to create a new item."""
        # url_for('new_schedule')
        pass

    def update(self, id):
        """PUT /schedules/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('schedule', id=ID),
        #           method='put')
        # url_for('schedule', id=ID)
        pass

    def delete(self, id):
        """DELETE /schedules/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('schedule', id=ID),
        #           method='delete')
        # url_for('schedule', id=ID)
        pass

    def show(self, id, format='html'):
        """GET /schedules/id: Show a specific item."""
        # url_for('schedule', id=ID)
        pass

    def edit(self, id, format='html'):
        """GET /schedules/id;edit: Form to edit an existing item."""
        # url_for('edit_schedule', id=ID)
        pass
