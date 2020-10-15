"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
import logging
import traceback

from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render
from sqlalchemy.exceptions import InvalidRequestError
import maintcal.lib.helpers as h
import maintcal.model as model

log = logging.getLogger(__name__)

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            rollback_in_subtransaction = False
            try:
                return WSGIController.__call__(self, environ, start_response)
            except InvalidRequestError, e:
                log.error("SQLALCHEMY ERROR line 33: %s" % (repr(e)))
                rollback_in_subtransaction = True
                # This appears to happen sometimes, so we fix it.
                model.db_sess.rollback()

                # This might not be necessary
                model.db_sess.remove()

        # Uncommenting the "except" block should work in Python 2.5 for logging
        #except Exception, err:
        #    log.error("%s\n%s" % (err,traceback.format_exc()))
        #    model.db_sess.remove()
        #    raise
        finally:
            if config['test_mode'].lower() == 'false':
                if rollback_in_subtransaction:
                    model.db_sess.rollback()
                    model.db_sess.close()
                else:
                    # Do the actual top-level commit
                    try:
                        model.db_sess.commit()
                        # Make sure sessions from previous page hits don't effect newer sessions
                        model.db_sess.remove()
                    except InvalidRequestError, e:
                        log.error("SQLALCHEMY ERROR line 58: %s" % (repr(e)))
                        model.db_sess.rollback()
                        model.db_sess.close()
                    except:
                        log.error(traceback.format_exc())
                        model.db_sess.rollback()
                        model.db_sess.close()
            else:
                # In test mode, we do not automatically commit at the end of the page hit.
                pass 

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
