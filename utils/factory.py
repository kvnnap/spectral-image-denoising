import itertools
import copy

def unpack_config(obj):
    obj = copy.deepcopy(obj)
    objConfig = {}

    if ('name' in obj):
        objConfig = obj
    else:
        objConfig['name'] = obj

    name = objConfig.pop('name').strip().lower()
    
    keys = objConfig.keys()
    values = objConfig.values()
    combinations = list(itertools.product(*values))
    configs = [{key: value for key, value in zip(keys, combination)} for combination in combinations]
    for config in configs:
        config['name'] = name
    return configs

def unpack_list_config(configs):
    return [u for c in configs for u in unpack_config(c)]
