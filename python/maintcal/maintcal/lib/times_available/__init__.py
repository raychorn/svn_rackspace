"""
This package contains the times_available logic for the maintenance calendar.

This is the heart and soul of maintcal!!!!

Be careful!!!!

=== Terminology of Times Available ===

Work Unit:

    This is currently arbitrarily defined as an hour.
    How many hours of work can be done in the period.
    A work unit is a man hour.

Duration:

    Length of a specific amount of time.  Duration is time-specific, length is more general.

Period:
        
    A Period is an arbitrary length of time in which an arbitrary number of "work units" can be done.

Quanta:

    A block of time used to evenly divide a day.
    The size of this block is known as the granularity.

Quanta Offset:  

    For a specific day, this number uniquely identifies a specific quanta for that day.
    It is basically an index.

Period Depth:

    The number of masks in a period. 

    The higher the index of the mask in the list, the deeper the depth.
    The shallowest depth layer is depth layer zero.  

    Masks
    [0] 1111 # shallowest
    [1] 1100
    [2] 1100 # deepest

Depth Layer:

    If a period has a depth of 1, then it will only contain quanta in depth layer zero.

Granularity:

    The size of a quanta in minutes.


"""
from pylons import config

from maintcal.lib.date import assertDatetime

# NOTE: The following things should only be used inside of lib/times_available/

def granularity_in_minutes():
    """Gives the granularity in minutes."""
    return int(config['calendar_granularity_seconds']) / 60

# The number of the maximum quanta offset
MAX_QUANTA_OFFSET = (24 * 60) / granularity_in_minutes()

# Strings for constucting the bitmasks
AVAIL_BIT = "1"
UNAVAIL_BIT = "0"

def work_units_to_quanta(work_units):
    """Convert work_units into quanta"""
    return float(work_units * 60) / granularity_in_minutes()

def binaryStringToInt(binary_string):
    """Convert a string of ones and zeros to an integer."""
    return int(binary_string, 2)

def generate_bitmask_int(start_quanta_offset, duration_in_quanta):
    """ Generate a bitmask that is the size of an entire day blocking out the time during the specified quanta.

        It will consist of available bits for each quanta up to the offset, 
        followed by 'quanta' unavailable bits, with enough
        available bits to bring the total length to MAX_QUANTA_OFFSET. 

        # Create a bit string with 'available' bits before the start of the service, 
        # unavailable bits for the duration of the service. 
        # Then pad the string with available bits to the total length of the day.

        Return the integer value of the bitmask.
    """
    mask = (AVAIL_BIT * start_quanta_offset) + (UNAVAIL_BIT * duration_in_quanta)
    expanded_mask = expand_mask_to_length_of_day(mask)
    mask_as_int = binaryStringToInt(expanded_mask)
    return mask_as_int

def strbits(intval):
    ret = ""
    intToBin = {"0": "000", "1": "001", "2": "010", "3": "011", 
        "4": "100", "5": "101", "6": "110", "7": "111","L": ""}
    for char in oct(intval)[1:]:
        ret += intToBin[char]
    return ret.rjust(MAX_QUANTA_OFFSET, "0")

def expand_mask_to_length_of_day(mask):
    """Expand a mask to the length of a day, by padding it to the right with 1s."""
    return mask.ljust(MAX_QUANTA_OFFSET, AVAIL_BIT)

def bitstring_and(val1, val2):
    mask = ""
    for place, bit in enumerate(val1):
        if bit == val2[place]:
            mask += bit
        else:
            mask += "0"
    return mask

    #if isinstance(val1, basestring):
    #    val1 = binaryStringToInt(val1)
    #if isinstance(val2, basestring):
    #    val2 = binaryStringToInt(val2)
    #return strbits(val1 & val2)

def bitstring_or(val1, val2):
    mask = ""
    for place, bit in enumerate(val1):
        if bit == val2[place]:
            mask += bit
        else:
            mask += "1"
    return mask


def datetime_to_quanta_offset(a_datetime):
    """ Given a datetime, caculate the quanta_offset."""
    assertDatetime(a_datetime)
    minutes_for_hour = 60 * a_datetime.hour
    minute_of_day = minutes_for_hour + a_datetime.minute
    return minute_of_day / granularity_in_minutes()
