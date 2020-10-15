"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *

def file_logger(txt):
    fh = open('/home/core/var/log/maintcal-calendar.log','a')
    fh.write(txt)
    fh.close()
