import jsonpickle

def save(file_name, obj):
        with open(file_name, 'w') as fp:
            fp.write(jsonpickle.encode(obj, indent=4)) # use , make_refs=False to avoid the py/id stuff. or unpicklable=False (extreme)
    
def load(file_name):
    with open(file_name, 'r') as fp:
        return jsonpickle.decode(fp.read())
