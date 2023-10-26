
from langchain.document_loaders import PyPDFDirectoryLoader  # tt un dossier, ms mm pb que PyPDFLoader
from langchain.document_loaders import PyPDFLoader  # probleme d'espaces intempestifs
#from langchain.document_loaders import UnstructuredPDFLoader # ne preserve pas l'ordre du texte
from langchain.document_loaders import PyMuPDFLoader
import loading.utils as utils

def load_files(data_dir, check_directory=None, loader_method='PyMuPDFLoader') :
    # return [] if persist_directory already contains loaded data
    # One should then create the vectorstore using create_vectordb on the empty docs
    # in order to recover the embeddings from persist_directory (rather than recomputing them)
    # To load anyway, check_directory should be set to None
    # todo: re organize this into two separated functions
    loader_method = eval(loader_method)
    docs = []
    files = utils.list_of_pdf_files(data_dir) # list of strings
    if check_directory is None :
        vectors = []
    else :
        try :
            vectors = utils.list_of_files(check_directory)
        except FileNotFoundError : # probably a first run, directory not created yet
            vectors = []
    if len(vectors) == 0 :  # initial filling of database
        loaders = []
        for f in files :
            loaders.append(loader_method(data_dir+f))
        for loader in loaders:
            docs.extend(loader.load())   # docs = list of all pages as disctinct documents
    if len(docs) > 0 :
        docs = merge_doubles_in_list_docs(docs) # affectation is not actually necessary
        assert len(docs) == len(files)  # tout moche
    return docs, len(files)  # all pages, nb_files

def load_single_pdf(data_dir, filename, check_directory=None, loader_method='PyMuPDFLoader') :
    # adapted from the above load_files function
    loader_method = eval(loader_method)
    docs = []
    if check_directory is None :
        vectors = []
    else :
        try :
            vectors = utils.list_of_files(check_directory)
        except FileNotFoundError : # probably a first run, directory not created yet
            vectors = []
    if len(vectors) == 0 :  # initial filling of database
        loaders = [loader_method(data_dir+filename)]
        for loader in loaders:
            docs.extend(loader.load())   # chaque doc a plusieurs pages, chacune a des metadonnées
            # extend recolle 2 listes en une, donc c'est une liste de toutes les pages
    docs = merge_doubles_in_list_docs(docs) # affectation is not actually necessary
    return docs

def merge_doubles_in_list_docs(docs) :
    if len(docs) > 0 :
        prec = docs[0]
    i = 1
    while i < len(docs) :
        suiv = docs[i]
        if suiv.metadata['source'] == prec.metadata['source'] :
            prec.page_content += '\n\n' + suiv.page_content
            print(prec.page_content)
            docs.pop(i)
        else :
            prec = suiv
            i += 1
    return docs


def load_files_all_at_once(data_dir, persist_directory):
    vectors = utils.list_of_files(persist_directory) # to check if empty
    if len(vectors) == 0 :  # initial filling of database
        loader = PyPDFDirectoryLoader(data_dir)
        docs = loader.load()
    else :
        docs = []
    return docs
