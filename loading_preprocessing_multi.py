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

def load_field_value_from_csv(file, field) :
    '''Output : a tuple as of now -- could be a document too'''
    return 'field value', 'meta' 

def get_value_and_meta(field_value_with_meta) :
    '''Encapsulate the extraction of value and metadata from loaded data
    so the rest is non assuming of chosen type.
    Output : tuple'''
    return field_value_with_meta[0], field_value_with_meta[1]

def update_dict_with_field_value(dict_db, field, value_with_meta) :
    '''Add a value from a structured CV to the corresponding field of the dictionary
    Ideally value_with_meta should contain a value and a metadata'''
    value, meta = get_value_and_meta(value_with_meta)
    if field not in dict_db :
        dict_db[field] = {meta : value}
    else :
        if meta not in dict_db[field] :
            dict_db[field][meta] = value

def create_context_from_dict(dict_db, field) :
    '''Just in case (typically for non quantitative questions)'''
    context = field + ' of candidates : \n\n'
    for meta in dict_db[field] :
        context += '  <' + meta + '>:  ' + dict_db[field][meta] + '\n\n'
    return context
