from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
import subprocess
from langchain.vectorstores import Chroma
# my modules
import enrich_metadata

def splitting_of_docs(documents, splitter) :
    return splitter.split_documents(documents)  # list of documents (attributs page_content, metadata)

def new_vectordb(chunks, embedding, persist_directory) :
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=persist_directory
    )
    return vectordb

def create_vectordb_single(doc, splitter='default', embedding='default', persist_directory='default'):
    ## Default parameters
    if splitter == 'default':
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100, 
            separators=["\n\n", "\n", " ", ""]
        )
    if embedding == 'default':
        embedding = OpenAIEmbeddings()
    if persist_directory == 'default':
        subprocess.run('mkdir ' + "../chroma", shell=True)  # may pre-exist
        filename = doc.metadata['source'].split('/')[-1]
        persist_directory = "../chroma/" + filename
        subprocess.run('mkdir ' + persist_directory, shell=True)  # may pre-exist
    chunks = splitting_of_docs([doc], splitter)  # todo : splitter.split_document(?)(doc)
    vectordb = new_vectordb(chunks, 
                            embedding, 
                            persist_directory
    )
    return vectordb

def create_vector_db(docs, data_dir, splitter, embedding, persist_directory, enrich_with_name=True, llm='default') :
    '''Create or recover the vectorstore, based on wether persist_directory already has content.
    Option to add the names of candidates as metadata (or recover it if possible).
    Along with the vectorstore, provide the list of names as a string (empty if names were not asked for or could not be recovered)
    Output: tuple (vectorstore, string)
    '''
    subprocess.run('mkdir ' + persist_directory, shell=True)  # pire des cas il existe deja
    list_of_names_as_str = ""
    if docs == [] :  # on avait deja load et cree la vectordb, donc on recharge tel quel
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding
        )
        list_of_names = []
        metadatas = vectordb.get(include=['metadatas'])['metadatas']
        if len(metadatas) == 0 :
            print('No metadata in the pre-indexed documents. Check this out')
        elif 'name' in metadatas[0] and enrich_with_name : # il y avait des noms dans les metadonnees
            for doc_meta in metadatas :
                name = doc_meta['name']
                if name not in list_of_names :
                    list_of_names.append(name)
        list_of_names_as_str = ", ".join(list_of_names)
    else :
        if enrich_with_name :
            docs, list_of_names_as_str = enrich_metadata.add_name_as_metadata(docs, data_dir, llm)
        chunks = splitting_of_docs(docs, splitter)
        vectordb = new_vectordb(chunks, 
                                embedding, 
                                persist_directory
        )
    vectordb.persist() # utile ?
    return vectordb, list_of_names_as_str

def retrieving(retriever_obj, question, retriever_type="vectordb", with_scores=True) :
    '''Retrieving based on either a vectorstore as retriever (similarity search) or a specified retriever.
    Option to print relevance scores (will only work with a vectorstore as of now)'''
    if retriever_type == "vectordb" :  # retriever_obj est un vectordb
        if with_scores == True :
            return retriever_obj.similarity_search_with_score(question, k=5)  # lower is better
        else :
            return retriever_obj.as_retriever(search_type="similarity").get_relevant_documents(question, k=5)
    else :                             # retriever_obj est un retriever
        return retriever_obj.get_relevant_documents(question, k=6, fetch_k = 6) # todo : equivalent a vectordb.similarity_search(question, k opt) ??
