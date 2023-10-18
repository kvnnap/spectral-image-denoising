import os

def extract_file_name(input_string):
    base_filename = os.path.basename(input_string)  # Get the base filename
    filename_without_extension, _ = os.path.splitext(base_filename)  # Remove the file extension
    return filename_without_extension
