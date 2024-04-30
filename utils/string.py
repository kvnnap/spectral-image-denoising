from pathlib import Path

def extract_file_extension(file_path):
    return Path(file_path).suffix

def extract_file_name(file_path):
    return Path(file_path).stem

def concat_paths(a, b):
    return str(Path(a).joinpath(b))

def comma_to_list(str):
    str = str.strip().lower()
    return list(map(lambda x: x.strip(), str.split(','))) if str else []
