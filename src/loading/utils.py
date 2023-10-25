import os

def list_of_files(data_dir) :
    print(data_dir)
    print(os.listdir(data_dir))
    return os.listdir(data_dir)

def list_of_pdf_files(data_dir) :
    return [f for f in list_of_files(data_dir) if "pdf" in f]

def list_of_files_as_str(data_dir) :
    joint = ', ' + data_dir
    return data_dir + joint.join(list_of_files(data_dir))
