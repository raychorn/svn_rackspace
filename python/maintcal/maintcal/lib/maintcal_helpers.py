# module to contain various functions to ease bad looping tasks and other stuff
# Nathen Hinson 03/17/2009 MCAL-66 performance.

from maintcal.model import db_sess,Server
from maintcal.lib import core_xmlrpc

class NoCOREDevice(Exception): pass

def sortByDeviceId(a,b):
    if not isinstance(a,Server) or not isinstance(b,Server):
        raise TypeError, "Invalid input to device sort"

    return cmp(a.id,b.id)

def updateDeviceCache(devices_to_update,implicit_commit=True):
    
    # a couple of sanity checks
    if '__iter__' not in dir(devices_to_update):
        raise TypeError, "First argument must iterable."
    
    if [device for device in devices_to_update \
        if not isinstance(device,int) and not isinstance(device,Server)]:
        raise TypeError, "First argument must be either Maintcal Server " +\
                        "instances or integers representing devices."

    cached_devices = {}
    remote_devices = []
    all_devices = []
    not_devices = []
    all_device_objects = []
    for single_device in devices_to_update:
        if isinstance(single_device,Server):
            cached_devices[single_device.id] = single_device
            all_devices.append(single_device.id)
        else:
            remote_devices.append(single_device)
            all_devices.append(single_device)


    try:
        core_devices = core_xmlrpc.Computer.getServers(computers=all_devices)
    except core_xmlrpc.NotAuthenticatedException:
        raise

    if not core_devices:
        raise NoCOREDevice, "No active devices."

    if implicit_commit:
        db_sess.begin_nested()

    core_device_ids_only = [s['server'] for s in core_devices]

    non_active_devices_set = set(all_devices) - set(core_device_ids_only)

    if non_active_devices_set:
        raise NoCOREDevice, "No active device with id(s) %s" % non_active_devices_set

    for core_device in core_devices:
        if core_device['server'] in cached_devices.keys():
            cached_devices[core_device['server']].updateFromDict(core_device)
            all_device_objects.append(cached_devices[core_device['server']])
            
        if core_device['server'] in remote_devices:
            new_cached_device = Server.fromDict(core_device)
            db_sess.save(new_cached_device)
            all_device_objects.append(new_cached_device)
            
    # Save everything we can
    if implicit_commit:
        db_sess.commit()

    return all_device_objects





 
