
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
