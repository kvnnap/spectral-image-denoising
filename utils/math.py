import numpy as np

def euclidean_distance(arr1, arr2):
    if len(arr1) != len(arr2):
        raise ValueError("Arrays must have the same length")
    
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)
    squared_diff = (arr1 - arr2) ** 2
    sum_squared_diff = np.sum(squared_diff)
    distance = np.sqrt(sum_squared_diff)
    return distance

def get_threshold_max(arr):
    return np.std(arr)
