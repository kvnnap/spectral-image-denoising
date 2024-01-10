from pathlib import Path

def extract_file_extension(file_path):
    return Path(file_path).suffix

def extract_file_name(file_path):
    return Path(file_path).stem
