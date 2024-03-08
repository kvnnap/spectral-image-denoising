import itertools
import copy

def unpack_config(obj):
    obj = copy.deepcopy(obj)
    objConfig = obj if 'name' in obj else { 'name': obj }

    name = objConfig.pop('name').strip().lower()
    
    keys = objConfig.keys()
    values = objConfig.values()
    combinations = list(itertools.product(*values))
    configs = [{ 'name': name, **{ key: value for key, value in zip(keys, combination) } } for combination in combinations]
    return configs

def unpack_list_config(configs):
    return [u for c in configs for u in unpack_config(c)]
