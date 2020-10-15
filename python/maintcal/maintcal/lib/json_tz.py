import simplejson
import os
import os.path
from datetime import datetime
import re
from pylons import config
import time

#from logging import Logger

ZONETAB_FILE = '/usr/share/zoneinfo/zone.tab'
JSFILE = 'zonenames.js'

class file_util:
    @classmethod
    def load_zonetab_file(cls, file):
        if os.path.exists(file):
            try:
                zonefile = open(file, 'r')
            except:
                #TODO log error
                return None
            else:
                return zonefile.read()
        else:
            #TODO log error
            return None
    
class JsonTz(object):
    
    def __init__(self):
        self.tzmatch = re.compile('[A-Z][A-Z]\t(\-|\+)[0-9]+(\-|\+)[0-9]+\t[A-z]+/[A-z]+')
        self.tzdict = {}
        
    def parse_file(self, file=ZONETAB_FILE):
        tzdata_str = file_util.load_zonetab_file(file)
        if tzdata_str:
            #do stuff
            tz_list = tzdata_str.split('\n')
            for line in tz_list:
                #print line
                if self.tzmatch.match(line):
                    #print line
                    zonename = line.split('\t')[2]
                    zonelinelist = zonename.split('/')
                    continent = zonelinelist[0]
                    location = '/'.join(zonelinelist[1:])
                    if self.tzdict.has_key(continent):
                        self.tzdict[continent].append(location)
                    else:
                        self.tzdict[continent] = [location,]

            # add in a 'keys' value to the dict. IMPORTANT !
            self.tzdict['keys'] = self.tzdict.keys();
    
    def to_json(self):
        return "var tznames = %s; " % simplejson.dumps(self.tzdict)
    
    def export(self, path2file, format='json'):
        if format=='json':
            text = self.to_json()
            filename = os.path.join(path2file, JSFILE)
        else:
            raise ValueError, "'%s' format not supported" % format
        
        f_handle = open(filename, 'w')
        f_handle.write(text)
        f_handle.close()
        
    def get_abbr_dict(self):
        my_environ_tz = os.environ.get('TZ')
        abbr_dict = {}
        for cont in self.tzdict.keys():
            for loc in self.tzdict[cont]:
                zname = "%s/%s" % (cont, loc)
                os.environ['TZ'] = zname
                time.tzset()
                for tzabbr in time.tzname:
                    abbr_dict[tzabbr] = zname
        if my_environ_tz:
            os.environ['TZ'] = my_environ_tz
        elif (os.environ.has_key('TZ')):
            del os.environ['TZ']
        time.tzset()
        return abbr_dict

tzfile = JsonTz()
def gen_zonenamesjs():
    tzfile.parse_file()
    if not os.access(config['cache.dir'], os.F_OK):
        os.makedirs(config['cache.dir'])
    tzfile.export(config['cache.dir'])
