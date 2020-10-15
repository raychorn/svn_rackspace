from maintcal.model import db_sess
import logging

log = logging.getLogger(__name__)

class MaintcalModel(object):
    """This is a common superclass for all maintenance calendar model objects.

    Note: We are defining classmethods so that they will be inherited by the subclasses.
          staticmethods are not inherited.
    """

    @classmethod
    def find_and_call(cls, finder, method_name):
        """Call a given finder on an sqlalchemy model and call method_name on all of the found objects.
        Return a list of ids of the found objects."""

        id_list = []
        #db_sess.begin_nested()
        for model_instance in getattr(cls, finder)():
            getattr(model_instance, method_name)()
            id_list.append(model_instance.id)
        db_sess.commit()
        id_list_for_log = ",".join([str(record_id) for record_id in id_list])
        log.info("[REAPER] Model %s Finder %s records %s had method %s called." % (cls, finder, id_list_for_log, method_name))
        return id_list


    @classmethod
    def print_all(cls):
        """Load and print all objects of this type to stdout."""
        all_objects = db_sess.query(cls).all()
        for obj in all_objects:
            print obj

    def toDict(self):
        output = {}
        keys = self.__dict__.keys()
        for k in keys:
            if not k.startswith("_"):
                output[k] = self.__dict__[k]
        return output 

    def __str__(self):
        output = ''
        keys = self.__dict__.keys()
        keys.sort()
        for k in keys:
            v = self.__dict__[k]
            output += str(k) + ':'
            output += str(v) + '\n'
        return output
