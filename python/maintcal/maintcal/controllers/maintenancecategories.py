import logging
import simplejson
from pylons import config

from maintcal.lib.base import *
from maintcal.model import db_sess, MaintenanceCategory

from authkit.authorize.pylons_adaptors import authorize
from authkit.permissions import And
from core_authkit.permissions import LoggedIn, DepartmentIn

log = logging.getLogger(__name__)

class MaintenancecategoriesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('maintenancecategory', 'maintenancecategories')
    
    @authorize(LoggedIn())
    def index(self, format='html'):
        """GET /maintenancecategories: All items in the collection."""
        # url_for('maintenancecategories')
        mcs = db_sess.query(MaintenanceCategory).all()
        if format=='json':
            return simplejson.dumps([self._maint_cat_vals(mc) for mc in mcs])
        return str([self._maint_cat_vals(mc) for mc in mcs])

    #@authorize(And(LoggedIn(), DepartmentIn(config['admin_departments'])))
    @authorize(LoggedIn())
    @authorize(DepartmentIn(config['admin_departments']))
    def create(self):
        """POST /maintenancecategories: Create a new item."""
        # url_for('maintenancecategories')
        mc_name = request.params.get('name')
        mc_desc = request.params.get('description')
        mc = MaintenanceCategory(name=mc_name, description=mc_desc)
        db_sess.begin_nested()
        db_sess.save(mc)
        db_sess.commit()
        return str(mc.id)

    @authorize(LoggedIn())
    def new(self, format='html'):
        """GET /maintenancecategories/new: Form to create a new item."""
        # url_for('new_maintenancecategory')
        pass

    #@authorize(And(LoggedIn(), DepartmentIn(config['admin_departments'])))
    @authorize(LoggedIn())
    @authorize(DepartmentIn(config['admin_departments']))
    def update(self, id):
        """PUT /maintenancecategories/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('maintenancecategory', id=ID),
        #           method='put')
        # url_for('maintenancecategory', id=ID)
        mc = db_sess.query(MaintenanceCategory).get(id)
        db_sess.begin_nested()
        if not mc:
            abort(404, "No such Maintenance Category with ID %s" % id)
        if request.params.get('name') != None:
            mc.name = request.params.get('name')
        if request.params.get('description') != None:
            mc.description = request.params.get('description')
        db_sess.commit()
        return str(mc.id)
    
    @authorize(LoggedIn())
    def delete(self, id):
        """DELETE /maintenancecategories/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('maintenancecategory', id=ID),
        #           method='delete')
        # url_for('maintenancecategory', id=ID)
        pass

    @authorize(LoggedIn())
    def show(self, id, format='html'):
        """GET /maintenancecategories/id: Show a specific item."""
        # url_for('maintenancecategory', id=ID)
        mc = db_sess.query(MaintenanceCategory).get(id)
        if not mc:
            abort(404, "No such Maintenance Category with ID '%s'" % id)
        
        if format=='json':
            return simplejson.dumps(self._maint_cat_vals(mc))
        return str(self._maint_cat_vals(mc))

    @authorize(LoggedIn())
    def edit(self, id, format='html'):
        """GET /maintenancecategories/id;edit: Form to edit an existing item."""
        # url_for('edit_maintenancecategory', id=ID)
        pass

    @authorize(LoggedIn())
    def _maint_cat_vals(self, maintcat):
        return {
            'id' : maintcat.id,
            'name' : maintcat.name,
            'description' : maintcat.description}
