import numpy as np

# Partitions 'count' items in 'den' sections. 
# 'start' and 'length' can be used to weigh differently
# Returns (startIndex, length) of the partition in the array
# having 'count' items
def partition_array(count, den, start, length):
    numItems = count // den
    leftOver = count % den
    startIndex = numItems * start + min(leftOver, start)
    totalItems = numItems * length + min(max(leftOver - start, 0), length)
    return (startIndex, totalItems)

def split_partition_array(arr, den, start, length):
    pa = partition_array(len(arr), den, start, length)
    return arr[pa[0]:pa[0] + pa[1]]

def apply_sliding_predicate(arr, predicate):
    return True if len(arr) < 2 else all(predicate(arr[i], arr[i+1]) for i in range(len(arr)-1))

def is_sorted_ascending(arr):
    return apply_sliding_predicate(arr, lambda a, b: a <= b)

def are_items_unique(arr):
    return len(arr) == len(set(arr))

def is_not_finite(x):
    return not np.isfinite(x).all()

def sanitise(x):
    return np.clip(np.nan_to_num(x), 0, None)
