
from langchain.document_loaders import PyPDFDirectoryLoader  # tt un dossier, ms mm pb que PyPDFLoader
from langchain.document_loaders import PyPDFLoader  # probleme d'espaces intempestifs
#from langchain.document_loaders import UnstructuredPDFLoader # ne preserve pas l'ordre du texte
from langchain.document_loaders import PyMuPDFLoader
import utils

def load_files(data_dir, persist_directory=None, loader_method='PyMuPDFLoader') :
    loader_method = eval(loader_method)
    docs = []
    files = utils.list_of_files(data_dir) # list of strings
    if persist_directory is None :
        vectors = []
    else :
        try :
            vectors = utils.list_of_files(persist_directory)
        except FileNotFoundError : # probably a first run, directory not created yet
            vectors = []
    if len(vectors) == 0 :  # initial filling of database
        loaders = []
        for f in files :
            loaders.append(loader_method(data_dir+f))
        for loader in loaders:
            docs.extend(loader.load())   # chaque doc a plusieurs pages, chacune a des metadonnées
            # extend recolle 2 listes en une, donc c'est une liste de toutes les pages
    return docs, len(files)  # all pages, nb_files

def load_files_all_at_once(data_dir, persist_directory) :
    vectors = utils.list_of_files(persist_directory) # to check if empty
    if len(vectors) == 0 :  # initial filling of database
        loader = PyPDFDirectoryLoader(data_dir)
        docs = loader.load()
    else :
        docs = []
    return docs
