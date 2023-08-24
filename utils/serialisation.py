import jsonpickle

def save(file_name, obj, make_refs=True):
        with open(file_name, 'w') as fp:
            fp.write(jsonpickle.encode(obj, indent=4, make_refs=make_refs)) # use , make_refs=False to avoid the py/id stuff. or unpicklable=False (extreme)
    
def load(file_name):
    with open(file_name, 'r') as fp:
        return jsonpickle.decode(fp.read())
