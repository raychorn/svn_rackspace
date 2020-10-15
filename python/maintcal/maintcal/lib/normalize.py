# Library for normalizing values
import decimal 
from datetime import timedelta

def drop_controls():
    # This function returns a hard-coded list of control characters 
    # (ex. ^K ... the ascii representation of a vertical tab character )
    # that are not supported in XML. 
    drop_controls = [None] * 0x20
    for c in'\t\r\n':
        drop_controls[ord(c)] = unichr(ord(c))

    return drop_controls

def normalize_boolean(value):
    """Converts strings into booleans by intelligently parsing the content."""
    if isinstance(value, str) or isinstance(value, unicode):
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        if value.isdigit():
            return bool(int(value))
    return bool(value)

def normalize_interval(value):
    """Converts strings into intervals."""
    if not isinstance(value, str) and  not isinstance(value, unicode):
        raise ValueError, "Only accepts strings"
    try:
        return timedelta(hours=float(decimal.Decimal(value)))
    except (TypeError, ValueError, decimal.InvalidOperation), err:
        raise ValueError, err
