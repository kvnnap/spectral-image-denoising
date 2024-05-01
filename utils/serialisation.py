import jsonpickle

def save(file_name, obj, make_refs=True, write_mode='w'):
        with open(file_name, write_mode) as fp:
            fp.write(jsonpickle.encode(obj, indent=4, make_refs=make_refs)) # use , make_refs=False to avoid the py/id stuff. or unpicklable=False (extreme)
    
def load(file_name):
    with open(file_name, 'r') as fp:
        return jsonpickle.decode(fp.read())
    
def print_obj(obj):
    print(f"{jsonpickle.encode(obj, unpicklable=False)}")

def to_string_obj(obj):
    return f"{jsonpickle.encode(obj, unpicklable=False)}"

def save_text(file_name, text, write_mode='w'):
    with open(file_name, write_mode) as fp:
        fp.write(text)
