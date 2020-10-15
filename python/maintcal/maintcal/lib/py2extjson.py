import simplejson
from paste.util.multidict import UnicodeMultiDict

class py2extjson(object):

    @classmethod
    def dumps(cls,l,id='id',echo_params=False):
            
        outie = {'metaData':{
                        'totalProperty':'results',
                        'root':'rows',
                        'id':id,
                        'fields':[]
                    },
                    'results':None,
                    'rows':[]
                }

        # output the request parameters back with the result.
        if echo_params and isinstance(echo_params,UnicodeMultiDict):
            outie['metaData'].update(echo_params.mixed())

        if isinstance(l,dict):
            l = [l]

        if isinstance(l,list):
            if len(l) == 0:
                return simplejson.dumps(outie)
            
            if isinstance(l[0],dict):
                outie['metaData']['fields'] = [{'name':i} for i in l[0].keys()]

            outie['results'] = len(l)
            outie['rows'] = [j for j in l]
            return simplejson.dumps(outie)

        else:
            raise TypeError, "Argument must be a List or a Dict"

