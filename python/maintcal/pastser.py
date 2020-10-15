#!/usr/bin/env python
import os,sys

isUsingWindows = (sys.platform.lower().find('win') > -1) and (os.name.lower() == 'nt')

def exists(target):
    for i in xrange(len(sys.path)):
        if (str(sys.path[i]).lower().find(target) > -1):
            return i
    return -1

if (isUsingWindows):
    __root__ = 'J:/#redacted/#source/site-packages/usr/lib/python2.4/site-packages'
    for root,dirs,files in os.walk(__root__):
        if (str(root).lower().endswith('.egg')):
            f = exists(os.path.split(root)[-1])
            if (f > -1):
                del sys.path[f]
            else:
                f = len(sys.path)
            sys.path.insert(f,root)

print 'BEGIN:'                
for f in sys.path:
    print f
print 'END!!!'

from paste.script.serve import ServeCommand
ServeCommand("serve").run(["--reload", "development-windows.ini"])
