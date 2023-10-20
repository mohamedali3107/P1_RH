import os

def list_of_files(data_dir) :
    return [file for file in os.listdir(data_dir) if '.pdf' in file]

def list_of_files_as_str(data_dir) :
    joint = ', ' + data_dir
    return data_dir + joint.join(list_of_files(data_dir))
