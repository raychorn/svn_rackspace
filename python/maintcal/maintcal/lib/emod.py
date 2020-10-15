# emod.py
# Interval overlap detector
# Used for merging sets of intervals into a smaller set of larger intervals
# based on the determination of overlapping intervals

def condense_overlap(intervals):
    """
    Parameters:
        intervals : a list of tuples, each consisting of a start and end value.
    """
    
    starts = [i[0] for i in intervals]
    starts.sort()
    ends = [i[1] for i in intervals]
    ends.sort()
    new_intervals = []
    counter = 0

    while starts:
        if counter == 0:
            begin = starts.pop(0)
            counter += 1
        else:
            if starts[0] <= ends[0]:
                starts.pop(0)
                counter += 1
            else:
                end = ends.pop(0)
                counter -= 1
                if counter == 0:
                    new_intervals.append((begin,end))
    
    if ends:
        end = ends.pop(-1)
        new_intervals.append((begin,end))
    
    return new_intervals
