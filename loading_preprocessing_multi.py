import os
from langchain.document_loaders import PyPDFDirectoryLoader  # tt un dossier, ms mm pb que PyPDFLoader
from langchain.document_loaders import PyPDFLoader  # probleme d'espaces intempestifs
from langchain.document_loaders import UnstructuredPDFLoader # ne preserve pas l'ordre du texte
from langchain.document_loaders import PyMuPDFLoader

def list_of_files(data_dir) :
    return os.listdir(data_dir)

def list_of_files_as_str(data_dir) :
    joint = ', ' + data_dir
    return data_dir+joint.join(list_of_files(data_dir))

def load_files(data_dir, persist_directory=None, loader_method='PyMuPDFLoader') :
    loader_method = eval(loader_method)
    docs = []
    files = list_of_files(data_dir) # list of strings
    if persist_directory is None :
        vectors = []
    else :
        try :
            vectors = os.listdir(persist_directory)
        except FileNotFoundError : # probably a first run, directory not created yet
            vectors = []
    if len(vectors) == 0 :  # remplissage initial de la data base
        loaders = []
        for f in files :
            loaders.append(loader_method(data_dir+f))
        for loader in loaders:
            docs.extend(loader.load())   # chaque doc a plusieurs pages, chacune a des metadonnées
            # extend recolle 2 listes en une, donc c'est une liste de toutes les pages
    return docs, len(files)  # all pages, nb_files

def load_files_all_at_once(data_dir, persist_directory) :
    vectors = os.listdir(persist_directory) # pour tester si c'est vide ou pas
    if len(vectors) == 0 :  # remplissage initial de la data base
        loader = PyPDFDirectoryLoader(data_dir)
        docs = loader.load()
    else :
        docs = []
    return docs

###########################

def list_of_fields_csv(csv_file) :
    # to implement
    return ['file name', 'first name', 'family name', 'gender', 'age', 'e-mail', 'phone number', 'current job']

def labels_from_csv(csv_file) :
    # to implement
    return ['cv1.pdf', 'cv2.pdf']

def meta_of_file_from_csv(csv_file, label) :
    '''Output metadata to be used as key in dict_db'''
    fields = list_of_fields_csv(csv_file)
    field_first_name, field_family_name = fields[1], fields[2]
    first_name= load_field_data_from_csv(csv_file, label, field_first_name)
    family_name = load_field_data_from_csv(csv_file, label, field_family_name)
    return first_name + ' ' + family_name

def load_field_data_from_csv(csv_file, label, field) :
    '''Read a specified value in a csv'''
    # to implement
    return 'value'

def update_dict_with_field_value(dict_db, field, value, meta) :  # keep tests ?
    '''Add a value from a structured CV to the corresponding field of the dictionary
    Ideally value_with_meta should contain a value and a metadata'''
    if field not in dict_db :
        dict_db[field] = {meta : value}
    else :
        if meta not in dict_db[field] :  # todo : test pas si utile, au pire on écrase avec la même valeur
            dict_db[field][meta] = value

def update_dict_with_field_from_csv(dict_db, csv_file, field, all_loaded_CV) :
    labels = labels_from_csv(csv_file)
    for label in labels :
        if label in all_loaded_CV :
            meta = all_loaded_CV[label]
        else :
            meta = meta_of_file_from_csv(csv_file, label)
            all_loaded_CV[label] = meta
        value = load_field_data_from_csv(csv_file, label, field)
        update_dict_with_field_value(dict_db, field, value, meta)

## il est possible que des cv qui apparaissent dans
## all_loaded_cv et qq part dans dict_db n'aient pas tous les mêmes champs
## uploadés dans dict_db 
## d'où la fonction suivante pour egaliser
## plus flexible mais un peu moche

def equalize_loaded_data(dict_db, all_loaded_CV, csv_file) :
    for label in all_loaded_CV :
        meta = all_loaded_CV[label]
        for field in dict_db :
            if meta not in dict_db[field] :
                value = load_field_data_from_csv(csv_file, label, field)
                update_dict_with_field_value(dict_db, field, value, meta) # redundant test...

def update_dict_with_CV(dict_db, label, csv_file, full=False) :
    '''If new CV added to the pool (csv file was updated)
    Update of already loaded fields with values from new CV
    If full, addition and/or update of all csv fields into dict'''
    meta = meta_of_file_from_csv(csv_file, label)
    if not full :
        for field in dict_db :
            data = load_field_data_from_csv(csv_file, meta, field)
            update_dict_with_field_value(dict_db, field, data)
    else :
        list_of_fields = list_of_fields_csv(csv_file)
        for field in list_of_fields :
            data = load_field_data_from_csv(csv_file, meta, field)
            update_dict_with_field_value(dict_db, field, data)

def update_pool_loaded_CV(all_loaded_CV, label, meta) :  # todo : meta ou label ?
    all_loaded_CV[label] = meta

def update_dict_from_csv(dict_db, csv_file, list_loaded_CV) :
    '''Update with several new CVs'''
    labels = labels_from_csv(csv_file)
    for label in labels :
        if label not in list_loaded_CV :
            update_dict_with_CV(dict_db, label, csv_file)
            update_pool_loaded_CV(label)

def load_full_csv_to_dict(csv_file, dict_db, all_loaded_CV) :
    labels = labels_from_csv(csv_file)
    for label in labels :
        update_dict_with_CV(dict_db, label, csv_file, full=True)
        meta = meta_of_file_from_csv(csv_file, label)
        update_pool_loaded_CV(all_loaded_CV, label, meta)