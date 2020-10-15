import logging
import simplejson
import traceback
from datetime import timedelta
import decimal
from pylons import config
from sqlalchemy.orm import eagerload

from maintcal.lib.py2extjson import py2extjson
from maintcal.lib.base import *
from maintcal.lib.normalize import normalize_boolean
from maintcal.model import db_sess, ServiceType, ChangeLog

from authkit.authorize.pylons_adaptors import authorize
from authkit.permissions import And
from core_authkit.permissions import LoggedIn, DepartmentIn

log = logging.getLogger(__name__)

class ServicetypesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('servicetype', 'servicetypes')

    @authorize(LoggedIn())
    def index(self, format='html'):
        """GET /servicetypes: All items in the collection."""
        # url_for('servicetypes')
        fetch_active = normalize_boolean(request.params.get('active'))
        is_admin = normalize_boolean(request.params.get('admin'))
        stypes_query = db_sess.query(ServiceType).options(
                eagerload("maintenance_category"))
        # If this request is from the admin then add the modification
        # contact to the result
        if is_admin:
            changes = db_sess.query(ChangeLog).\
                filter(ChangeLog.table_id=='t').\
                filter(ChangeLog.row_id.in_(db_sess.query(ServiceType.id))).\
                order_by(ChangeLog.row_id,ChangeLog.creation_date.desc()).all()

            changes.sort(lambda x,y: cmp(x.creation_date,y.creation_date))
            changes_map = dict(tuple([(cs.row_id,cs.contact) for cs in changes]))
        if fetch_active:
            stypes_query = stypes_query.filter_by(active=True)

        stypes = stypes_query.all() 
        r_list = []
        if is_admin: 
            for stype in stypes:
                r_dict = stype.toDict()
                r_dict['modification_contact'] = changes_map.get(stype.id,'') 
                r_list.append(r_dict)
        else:
            r_list = [stype.toDict() for stype in stypes]

        #for stype in stypes:
        #    r_dict = stype.toDict()
        #    r_dict['modification_contact'] = self._find_last_mod_contact(stype.id)
        #    r_list.append(r_dict)
        if format=='json':
            return py2extjson.dumps(r_list)
        return str(r_list)

    @authorize(LoggedIn())
    @authorize(DepartmentIn(config['admin_departments']))
    def create(self):
        """POST /servicetypes: Create a new item."""
        # url_for('servicetypes')
        
        db_sess.begin_nested()    
        try:
            maint_cat = int(request.params.get('maintenance_category_id'))
        except (TypeError, ValueError):
            abort(400, "Missing maintenance category ID")

        # a possible param coming from a ui based call. 
        # uiid = request.params.get('uiid')

        st_name = request.params.get('name')
        if not st_name:
            abort(400, "A name is required")
        
        service_type = ServiceType(
            name = st_name,
            description = request.params.get('description'),
            maintenance_category = maint_cat)
        if request.params.get('active'):
            service_type.active = normalize_boolean(request.params.get('active'))
        
        try:
            length_hours = decimal.Decimal(request.params.get('length_hours'))
        except (TypeError, ValueError, decimal.InvalidOperation):
            length_hours = 0
        service_type.length = timedelta(hours=float(length_hours))
        
        try:
            lead_time_hours = decimal.Decimal(request.params.get('lead_time_hours'))
        except (TypeError, ValueError, decimal.InvalidOperation):
            lead_time_hours = 0
        service_type.lead_time = timedelta(hours=float(lead_time_hours))
        
        try:
            db_sess.save(service_type)
            db_sess.commit()
        except:
            log.error(traceback.format_exc())
            abort(500,"Error saving data to the database")

        
        return str(service_type.id)
    
    @authorize(LoggedIn())
    @authorize(DepartmentIn(config['admin_departments']))
    def new(self, format='html'):
        """GET /servicetypes/new: Form to create a new item."""
        # url_for('new_servicetype')
        pass
    
    @authorize(LoggedIn())
    @authorize(DepartmentIn(config['admin_departments']))
    def update(self, id, format='html'):
        """PUT /servicetypes/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('servicetype', id=ID),
        #           method='put')
        # url_for('servicetype', id=ID)
        db_sess.begin_nested()    
        service_type = db_sess.query(ServiceType).get(id)
        if not service_type:
            abort(404, "No such Service Type with ID %s" % id)

        if request.params.get('name') != None:
            service_type.name = request.params.get('name')
        if request.params.get('description') != None:
            service_type.description = request.params.get('description')
        if request.params.get('active') != None:
            service_type.active = normalize_boolean(request.params.get('active'))
        if request.params.get('length_hours') != None:
            try:
                service_type.length = timedelta(hours=float(decimal.Decimal(request.params.get('length_hours'))))
            except (TypeError, ValueError, decimal.InvalidOperation):
                abort(400, "Bad value for 'length': %s" % request.params.get('length_hours'))
        if request.params.get('lead_time_hours') != None:
            try:
                service_type.lead_time = timedelta(hours=float(decimal.Decimal(request.params.get('lead_time_hours'))))
            except (TypeError, ValueError, decimal.InvalidOperation):
                abort(400, "Bad value for 'lead_time': %s" % request.params.get('lead_time_hours'))
        if request.params.get('maintenance_category_id') != None:
            try:
                service_type.maintenance_category_id = int(request.params.get('maintenance_category_id'))
            except (TypeError, ValueError):
                abort(400, "Bad value for 'maintenance_category_id': %s" % request.params.get('maintenance_category_id'))
        
        db_sess.commit()
        return str(service_type.id)
    
    @authorize(LoggedIn())
    def delete(self, id):
        """DELETE /servicetypes/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('servicetype', id=ID),
        #           method='delete')
        # url_for('servicetype', id=ID)
        pass
    
    @authorize(LoggedIn())
    def show(self, id, format='html'):
        """GET /servicetypes/id: Show a specific item."""
        # url_for('servicetype', id=ID)
        stype = db_sess.query(ServiceType).get(id)
        if not stype:
            abort(404, "No such Service Type with ID %s " % id)
        
        if format == 'json':
            r_dict = stype.toDict()
            r_dict['modification_contact'] = self._find_last_mod_contact(stype.id)
            return py2extjson.dumps(r_dict)

        return str(stype.toDict())
    
    @authorize(LoggedIn())
    def edit(self, id, format='html'):
        """GET /servicetypes/id;edit: Form to edit an existing item."""
        # url_for('edit_servicetype', id=ID)
        pass
    
    def _find_last_mod_contact(self, service_type_id):
        """ DEPRECATED """
        last_contact = db_sess.query(ChangeLog).\
                        filter_by(table_id='t').\
                        filter_by(row_id=service_type_id).\
                        order_by(ChangeLog.date.desc()).\
                        limit(1).all()
        if last_contact:
            return last_contact[0].contact
        return ''
