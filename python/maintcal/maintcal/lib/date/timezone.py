"""
Modified by Derrick J Wippler <thrawn01@gmail.com>

Original code from dateutil by Gustavo Niemeyer <gustavo@niemeyer.net>

        self._utc_trans_list :: [ timestamps_from_epoch_utc ]
            timestamps are seconds from jan 1, 1970 utc time
        self._local_trans_list :: [ timestamps_from_epoch_local ]
            timestamps are seconds from 

            that is, 0 in UTC is 1970 jan 1 UTC
            but in local time, 0 UTC might be 1969 dec 31 23:00:00 or something
            so the start of the local epoch might not be jan 1, 1970

    We are going to have two lists:

        1) in utc 
        
        2) in local time


        self._utc_trans_list = ( 1234234241 , 12345423434, 2345345234, 2345345342 )
        self._local_trans_list = ( 1234234241 , 12345423434, 2345345234, 2345345342 )

        when we ask for timezone information, we receive back a timezoneinfo object.

        self._trans_idx = ( TimezoneType( offset = -68300, timedelta( -1, 685000 ), isdst=1, abbr=CST, isstd=False, isgmt=False ) ,
                            TimezoneType( offset = -18000, timedelta( -1, 646000 ), isdst=0, abbr=CST, isstd=False, isgmt=False ) )

"""

from maintcal.lib.date.maintcal_datetime import MaintcalDatetime
from tarfile import TarFile
import datetime
import struct
import time
import sys
import os

ZERO = datetime.timedelta(0)
EPOCHORDINAL = datetime.datetime.utcfromtimestamp(0).toordinal()

CACHE = {}
CACHESIZE = 10
ZONE_INFO_DIR = "/usr/share/zoneinfo/"

def get_timezone_type(timezone_name):
    tzinfo = None

    # If the zoneinfo directory exists
    if not os.path.exists( ZONE_INFO_DIR ):
        raise ValueError( "'" + ZONE_INFO_DIR + "' doesn't exist!")
    
    # Have we already pulled tzinfo for this zone?
    if timezone_name in CACHE:
        return CACHE[timezone_name]

    zone_file_name = ZONE_INFO_DIR + timezone_name 
    if not os.path.exists( zone_file_name ):
        raise ValueError("No such timezone name '" + timezone_name + "'" )

    # Open the file and give it to TimezoneFile()
    zone_file = open( zone_file_name )

    tzinfo = TimezoneFile(zone_file)
    CACHE[timezone_name] = tzinfo

    return tzinfo

# Timezone Classes 
# -------------------------------

class tzutc(datetime.tzinfo):
    """
        This class is used to pass to python_datetime objects so that
        we can use the python_datetime to do UTC conversions.
    """

    def utcoffset(self, dt):
        return ZERO
     
    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def __eq__(self, other):
        return (isinstance(other, tzutc) and other._offset == ZERO)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    __reduce__ = object.__reduce__


class TimezoneType(object):
    """
        A generic timezoneinfo superclass.
    """

    __slots__ = ["offset", "delta", "isdst", "abbr", "isstd", "isgmt"]

    # DJW: Added the following for testing
    def __init__(self, **kwargs):
        for attr in self.__slots__:
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])
            else:
                setattr(self, attr, None)

    def __repr__(self):
        l = []
        for attr in self.__slots__:
            value = getattr(self, attr)
            if value is not None:
                l.append("%s=%s" % (attr, `value`))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(l))

    def __eq__(self, other):
        if not isinstance(other, TimezoneType):
            return False
        return (self.offset == other.offset and
                self.delta == other.delta and
                self.isdst == other.isdst and
                self.abbr == other.abbr and
                self.isstd == other.isstd and
                self.isgmt == other.isgmt)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getstate__(self):
        state = {}
        for name in self.__slots__:
            state[name] = getattr(self, name, None)
        return state

    def __setstate__(self, state):
        for name in self.__slots__:
            if name in state:
                setattr(self, name, state[name])

class TimezoneFile(object):
    """
        http://www.twinsun.com/tz/tz-link.htm
        ftp://elsie.nci.nih.gov/pub/tz*.tar.gz

    """
    
    def __init__(self, fileobj):

        self._filename = fileobj.name

        # From tzfile(5):
        #
        # The time zone information files used by tzset(3)
        # begin with the magic characters "TZif" to identify
        # them as time zone information files, followed by
        # sixteen bytes reserved for future use, followed by
        # six four-byte values of type long, written in a
        # ``standard'' byte order (the high-order  byte
        # of the value is written first).

        if fileobj.read(4) != "TZif":
            raise ValueError, "magic not found"

        fileobj.read(16)

        (
         # The number of UTC/local indicators stored in the file.
         # This information describes the "local time types"
         ttisgmtcnt,

         # The number of standard/wall indicators stored in the file.
         # This information describes the "local time types"
         ttisstdcnt,
         
         # The number of leap seconds for which data is
         # stored in the file.
         # The current algorithm is reading in and then ignoring this information.
         leapcnt,

         # The number of "transition times" for which data
         # is stored in the file.
         # This is the when the daylight savings transitions occur!
         timecnt,

         # The number of "local time types" for which data
         # is stored in the file (must not be zero).
         # Each transition is associated with one of these types.
         # More than one transition may use the same type.
         typecnt,

         # The  number  of  characters  of "time zone
         # abbreviation strings" stored in the file.
         charcnt,

        ) = struct.unpack(">6l", fileobj.read(24))

        # The above header is followed by tzh_timecnt four-byte
        # values  of  type long,  sorted  in ascending order.
        # These values are written in ``standard'' byte order.
        # Each is used as a transition time (as  returned  by
        # time(2)) at which the rules for computing local time
        # change.

        if timecnt:
            self._utc_trans_list = struct.unpack(">%dl" % timecnt,
                                             fileobj.read(timecnt*4))
        else:
            self._utc_trans_list = []

        # Next come tzh_timecnt one-byte values of type unsigned
        # char; each one tells which of the different types of
        # ``local time'' types described in the file is associated
        # with the same-indexed transition time. These values
        # serve as indices into an array of ttinfo structures that
        # appears next in the file.
        
        if timecnt:
            self._trans_idx = struct.unpack(">%dB" % timecnt,
                                            fileobj.read(timecnt))
        else:
            self._trans_idx = []
        
        # Each ttinfo structure is written as a four-byte value
        # for tt_gmtoff  of  type long,  in  a  standard  byte
        # order, followed  by a one-byte value for tt_isdst
        # and a one-byte  value  for  tt_abbrind.   In  each
        # structure, tt_gmtoff  gives  the  number  of
        # seconds to be added to UTC, tt_isdst tells whether
        # tm_isdst should be set by  localtime(3),  and
        # tt_abbrind serves  as an index into the array of
        # time zone abbreviation characters that follow the
        # ttinfo structure(s) in the file.

        ttinfo = []

        for i in range(typecnt):
            ttinfo.append(struct.unpack(">lbb", fileobj.read(6)))

        abbr = fileobj.read(charcnt)

        # Then there are tzh_leapcnt pairs of four-byte
        # values, written in  standard byte  order;  the
        # first  value  of  each pair gives the time (as
        # returned by time(2)) at which a leap second
        # occurs;  the  second  gives the  total  number of
        # leap seconds to be applied after the given time.
        # The pairs of values are sorted in ascending order
        # by time.

        # Not used, for now
        if leapcnt:
            leap = struct.unpack(">%dl" % (leapcnt*2),
                                 fileobj.read(leapcnt*8))

        # Then there are tzh_ttisstdcnt standard/wall
        # indicators, each stored as a one-byte value;
        # they tell whether the transition times associated
        # with local time types were specified as standard
        # time or wall clock time, and are used when
        # a time zone file is used in handling POSIX-style
        # time zone environment variables.

        if ttisstdcnt:
            isstd = struct.unpack(">%db" % ttisstdcnt,
                                  fileobj.read(ttisstdcnt))

        # Finally, there are tzh_ttisgmtcnt UTC/local
        # indicators, each stored as a one-byte value;
        # they tell whether the transition times associated
        # with local time types were specified as UTC or
        # local time, and are used when a time zone file
        # is used in handling POSIX-style time zone envi-
        # ronment variables.

        if ttisgmtcnt:
            isgmt = struct.unpack(">%db" % ttisgmtcnt,
                                  fileobj.read(ttisgmtcnt))

        # ** Everything has been read **

        # Build ttinfo list
        # This list describes each "local time" type.
        self._ttinfo_list = []
        for i in range(typecnt):
            gmtoff, isdst, abbrind =  ttinfo[i]
            # Round to full-minutes if that's not the case. Python's
            # datetime doesn't accept sub-minute timezones. Check
            # http://python.org/sf/1447945 for some information.

            # We don't need to round off because we are not using python date time
            #gmtoff = (gmtoff+30)//60*60
            tti = TimezoneType()
            tti.offset = gmtoff
            tti.delta = datetime.timedelta(seconds=gmtoff)
            tti.isdst = isdst
            tti.abbr = abbr[abbrind:abbr.find('\x00', abbrind)]
            tti.isstd = (ttisstdcnt > i and isstd[i] != 0)
            tti.isgmt = (ttisgmtcnt > i and isgmt[i] != 0)
            self._ttinfo_list.append(tti)

        # Replace ttinfo indexes with the corresponding ttinfo objects.
        trans_idx = []
        for idx in self._trans_idx:
            trans_idx.append(self._ttinfo_list[idx])
        self._trans_idx = tuple(trans_idx)

        # Set standard, dst, and before ttinfos. before will be
        # used when a given time is before any transitions,
        # and will be set to the first non-dst ttinfo, or to
        # the first dst, if all of them are dst.
        self._ttinfo_std = None
        self._ttinfo_dst = None
        self._ttinfo_before = None
        if self._ttinfo_list:
            # If there are no transition points, we use the first ttinfo for everything
            if not self._utc_trans_list:
                self._ttinfo_std = self._ttinfo_first = self._ttinfo_list[0]
            else:
                #
                #   Compute the "std" and "dst" ttinfos
                #

                # Basically, we grab the last ttinfo that is dst
                # and the last ttinfo that is is std, and then we stop

                # Iterate from timecnt-1 to zero, step = -1
                for i in range(timecnt-1,-1,-1):
                    tti = self._trans_idx[i]

                    if not self._ttinfo_std and not tti.isdst:
                        self._ttinfo_std = tti
                    elif not self._ttinfo_dst and tti.isdst:
                        self._ttinfo_dst = tti

                    if self._ttinfo_std and self._ttinfo_dst:
                        break
                else:
                    # if we have a dst, and no std, then use the dst as the std
                    if self._ttinfo_dst and not self._ttinfo_std:
                        self._ttinfo_std = self._ttinfo_dst

                #
                #   Compute the "before" ttinfo
                #

                # The "before" ttinfo is the first nondst ttinfo
                for tti in self._ttinfo_list:
                    if not tti.isdst:
                        self._ttinfo_before = tti
                        break
                else:
                    # If no ttinfos are nondst, then use the first ttinfo
                    self._ttinfo_before = self._ttinfo_list[0]

        #
        #   Compute the local_trans_list
        #

        laststdoffset = 0
        self._local_trans_list = list(self._utc_trans_list)

        # Iterate over the utc_trans_list
        for i in range(len(self._utc_trans_list)):
            tti = self._trans_idx[i]

            if not tti.isdst:
                self._local_trans_list[i] += tti.offset
                #print" This is std time. i = ", i, "  ", MaintcalDatetime.from_timestamp( self._local_trans_list[i] )
                #print " offset: ", tti.offset
                laststdoffset = tti.offset
            else:
                #print " This is dst time. Convert to std. ", MaintcalDatetime.from_timestamp( self._local_trans_list[i] )
                #print " offset: ",laststdoffset 
                self._local_trans_list[i] += laststdoffset
            #print "trans_list[", i ,"] = ", self._local_trans_list[i]

        self._local_trans_list = tuple(self._local_trans_list)

    # Derrick's implementation of converting from Localtime to UTC, feel free to remove if not needed ( untested )
    def find_timezone_info_local(self, maintcal_datetime, is_dst=None):
        timestamp = maintcal_datetime.to_timestamp()
        idx = 0
        for trans in self._local_trans_list:
            if timestamp < trans:
                break
            idx += 1
        else:
            return self._ttinfo_std

        if idx == 0:
            return self._ttinfo_before

        idx = idx -1

        if self.ambiguous(idx, timestamp):
            if is_dst:
                idx = idx - 1

        if self.non_existent(idx, timestamp):
            raise Exception( "Specified time is non existent" )

        return self._trans_idx[idx]
    
    def get_dst_offset(self, idx ):
        start_offset = time_delta_to_total_seconds( self._local_trans_list[idx].delta )
        end_offset = time_delta_to_total_seconds( self._local_trans_list[idx+1].delta )
        return abs( start_offset - end_offset )

    def ambiguous(self, idx, timestamp ):
        start = self._local_trans_list[idx]
        end = start + self.get_dst_offset( idx )
        if start <= timestamp < end :
            return True
        return False

    def non_existent(self, idx, timestamp ):
        # If we think this is not DST
        if not self._trans_idx[idx].is_dst:
            return False

        end = self._local_trans_list[idx]
        start = end - self.get_dst_offset( idx )
        if start <= timestamp < end :
            return True
        return False
            

    def find_previous_transition_point(self, maintcal_datetime):
        """
        Assuming a datetime that is already in UTC, 
        return the corresponding transition point in UTC that occurs before this datetime.
        """

        timestamp = maintcal_datetime.to_timestamp()

        trans_list = self._utc_trans_list

        #local = datetime.fromtimestamp( timestamp, tz=tzutc() )
        #print "find_timezone_info_utc: (", timestamp, local, ")"

        # Find the most relevant timezone_info for this timestamp

        idx = 0
        # iterate from the start of the datetimes forward
        prev_trans = None
        for trans in trans_list:

            #print "timestamp: ", datetime.fromtimestamp( timestamp, tz=tzutc() ) 
            #print" trans: ", datetime.fromtimestamp( trans ), " ", self._trans_idx[idx].abbr

            # If the current transition point is greater than the timestamp,
            # then we know which time type to use
            if timestamp < trans:
            #    print "break"
                return prev_trans
                break
            prev_trans = trans
            idx += 1

        else:
            # Nothing was found
            return None

        #if idx == 0:
        #    #print "idx == 0"
        #    return self._ttinfo_before

        # If is_dst is not None, then we compare the given is_dst with
        # the timezone_info object that we found.
        # If they do not match, then we need to adjust the index

        # Note: we must do an explicit "is not None", because 0 is false in python
        # and we want to run the conditional code if is_dst is 0.
        #if is_dst is not None:


        #print "self._utc_trans_list ", self._utc_trans_list[ idx-1 ], datetime.fromtimestamp( self._utc_trans_list[ idx-1 ], tz=tzutc())
        #print "self._utc_trans_list ", self._utc_trans_list[ idx ], datetime.fromtimestamp( self._utc_trans_list[ idx ], tz=tzutc())
        #print "self._trans_idx", idx-1 , " = " , self._trans_idx[idx-1]
        #return self._trans_idx[idx-1]



    def find_timezone_info_utc(self, maintcal_datetime):
        """
        Assuming a datetime that is already in UTC, 
        return the corresponding TimezoneInfo object for this datetime.
        """
        return self._find_timezone_info( maintcal_datetime, self._utc_trans_list )

    def _find_timezone_info(self, maintcal_datetime, trans_list, is_dst=None ):
        """

        """
        timestamp = maintcal_datetime.to_timestamp()

        #local = datetime.fromtimestamp( timestamp, tz=tzutc() )
        #print "find_timezone_info_utc: (", timestamp, local, ")"

        # Find the most relevant timezone_info for this timestamp

        idx = 0
        for trans in trans_list:
            #print "timestamp: ", datetime.fromtimestamp( timestamp, tz=tzutc() ), " trans: ", datetime.fromtimestamp( trans ), " ", self._trans_idx[idx].abbr
            if timestamp < trans:
            #    print "break"
                break
            idx += 1
        else:
            #print "not in trans_list"
            return self._ttinfo_std

        if idx == 0:
            #print "idx == 0"
            return self._ttinfo_before

        # If is_dst is not None, then we compare the given is_dst with
        # the timezone_info object that we found.
        # If they do not match, then we need to adjust the index

        # Note: we must do an explicit "is not None", because 0 is false in python
        # and we want to run the conditional code if is_dst is 0.
        #if is_dst is not None:


        #print "self._utc_trans_list ", self._utc_trans_list[ idx-1 ], datetime.fromtimestamp( self._utc_trans_list[ idx-1 ], tz=tzutc())
        #print "self._utc_trans_list ", self._utc_trans_list[ idx ], datetime.fromtimestamp( self._utc_trans_list[ idx ], tz=tzutc())
        #print "self._trans_idx", idx-1 , " = " , self._trans_idx[idx-1]
        return self._trans_idx[idx-1]

    def __eq__(self, other):
        if not isinstance(other, TimezoneFile):
            return False
        return (self._utc_trans_list == other._utc_trans_list and
                self._local_trans_list == other._local_trans_list and
                self._trans_idx == other._trans_idx and
                self._ttinfo_list == other._ttinfo_list)

    def __ne__(self, other):
        return not self.__eq__(other)


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, `self._filename`)

    # Used by Pickle to serialize the class, this is an un-serializable class
    def __reduce__(self):
        if not os.path.isfile(self._filename):
            raise ValueError, "Unpickable %s class" % self.__class__.__name__
        return (self.__class__, (self._filename,))


