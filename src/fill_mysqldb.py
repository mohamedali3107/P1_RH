import os
import openai
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import subprocess
import gradio as gr
import time
import vectorstore_lib
import call_to_llm
import treat_chunks
import mysql.connector
import subprocess
import getpass
import sql_queries as sql
import loading.load_pdf as load_pdf
import loading.load_from_csv as load_csv
import prompts.prompt_languages as pr_languages
import prompts.prompt_candidates as pr_candidates

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']

data_dir = "../data/"
table_prompts_path = "prompts/table_prompts.csv"


########## LLM Chain parameters ##########

persist_directory = '../chroma_single/'
loader_method = 'PyMuPDFLoader'
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100, 
    separators=["\n\n", "\n", " ", ""]
)
embedding = OpenAIEmbeddings()
llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

def add_one_cv(db_cursor, doc, force_refill=False, save=True, verbose=False, print_chunks=False):
    # todo : if already loaded and not force_refill, print and return accordingly
    if False :
        return
    else:
        filename = doc.metadata['source']
        if verbose:
            print("\nFilling the database with " + filename + "...\n")
        db_cursor.execute("SELECT FileName FROM candidates")
        known_files = db_cursor.fetchall()
        known_files = [file[0] for file in known_files]
        print("These files are known:", known_files)
        if filename in known_files :
            print("CV already parsed.")
            return

        ## Vectorstore and retriever creation
        subprocess.run('rm -rf ' + persist_directory, shell=True)
        chunks = vectorstore_lib.splitting_of_docs([doc], splitter)
        vectordb = vectorstore_lib.new_vectordb(chunks, 
                                embedding,
                                persist_directory
        )
        retriever_obj = vectordb
        # todo : call to auxiliary functions
        add_one_cv_candidate(db_cursor, filename, retriever_obj, retriever_type="vectordb", force_refill=force_refill, save=True, verbose=verbose, print_chunks=print_chunks)
        add_one_cv_language(db_cursor, filename, retriever_obj, retriever_type="vectordb", force_refill=force_refill, save=True, verbose=verbose, print_chunks=print_chunks)

def get_table_entry(retriever_obj, prompt, question, verbose=False, print_chunks=False, retriever_type="vectordb", llm='default'): 
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    
    chain = call_to_llm.create_chain(llm, prompt)

    ## Retrieving and calling the LLM
    sources = vectorstore_lib.retrieving(retriever_obj, question, retriever_type="vectordb", with_scores=True)
    context = treat_chunks.create_context_from_chunks(sources)
    answer = chain.predict(context=context)
    if verbose:
        print(f"Filling the {question} information... \n\n")
        print("Output of the LLM:", answer, "\n")
        if print_chunks:
            print("Here are the retrieved chunks with scores:")
            treat_chunks.print_chunks(sources)
    return answer

def add_one_cv_language(db_cursor, filename, retriever_obj, retriever_type="vectordb", force_refill=False, save=True, verbose=False, print_chunks=False):
    ## Prepare chain with prompt template
    prompt_template = pr_languages.template
    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    llm_output = get_table_entry(retriever_obj, prompt, "languages", verbose=verbose, print_chunks=print_chunks, retriever_type="vectordb", llm='default')
    languages_with_level = eval(llm_output)
    if save:
        db_cursor.execute("SELECT NameLanguage FROM languages")
        known_languages = [lang for sublist in db_cursor.fetchall() for lang in sublist]    # fetchall() returns a list of tuples (Language,)-like
        print("Known languages:", known_languages)
        for lang in languages_with_level:
            language, language_level = lang
            if language not in known_languages:
                db_cursor.execute(f"""INSERT INTO languages (NameLanguage) 
                                  VALUES ('{language}');""")
                known_languages.append(language)
            db_cursor.execute(f"""INSERT INTO speaks (NameLanguage, Candidate, LanguageLevel) VALUES ('{language}', '{filename}', '{language_level}');""")
    return

def add_one_cv_candidate(db_cursor, filename, retriever_obj, retriever_type="vectordb", force_refill=False, save=True, verbose=False, print_chunks=False):
    data = {'FileName' : filename}
    prompts_candidates = pr_candidates.dict_candidates  # dictionary of prompts to fill candidates

    columns, values = ['Filename'], [filename]
    for field in prompts_candidates :  # field must be exactly the name of an attribute
        prompt_template = prompts_candidates[field]['prompt']
        prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
        answer = get_table_entry(retriever_obj, prompt, field, verbose=verbose, print_chunks=print_chunks, retriever_type="vectordb", llm='default')
        data[field] = answer
                
        # todo : fill the candidate table with each attribute (each field)
        columns.append(field)
        values.append(data[field])
    print(columns)
    print(filename)
    columns = ", ".join(columns)
    values = "'" + "', '".join(values) + "'"
    db_cursor.execute(f"""INSERT INTO candidates ({columns}) 
                                  VALUES ({values});""")
    return

def fill_database(cursor, docs, table_prompts, print_time=True, force_refill=False):
    t0 = time.time()
    for doc in docs:
        try:
            add_one_cv(cursor, doc, table_prompts, force_refill=force_refill, save=True, verbose=True)
        except:
            print("Error filling the database for " + doc)
    if print_time:
        print("Time to fill the database with new CVs : {:.2f}s".format(time.time()-t0))

def initialize_database(database, verbose=True):
    cursor = database.cursor()
    db_name = 'candidates_cv'
    # check if the database already exists
    query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'"
    cursor.execute(query)
    if len(cursor.fetchall()) == 0 :  # a second call fetchall() would return []
        print("Creating the database...")
        cursor.execute("CREATE DATABASE " + db_name)
        database.commit()
    database.database = db_name
    cursor.execute(sql.create_candidates)
    cursor.execute(sql.create_languages)
    cursor.execute(sql.create_speaks)
    if verbose :
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Database tables :")
        for table in tables:
            print(table[0])
            cursor.execute("DESCRIBE " + table[0])
            columns = cursor.fetchall()
            for col in columns :
                print("   ", col)

def test_filling(cursor):

    cursor.execute("SELECT FirstName, FamilyName, PhoneNumber, Email FROM candidates;")
    extract = cursor.fetchall()
    print("Excerpt from the candidates table:")
    for entry in extract :
        print(*entry)

    cursor.execute("SELECT NameLanguage FROM languages;")
    extract = cursor.fetchall()
    print("Excerpt from the languages table:")
    for entry in extract :
        print(*entry)

def test_prompt(doc, prompt, question, verbose=True, print_chunks=True):
    subprocess.run('rm -rf ' + persist_directory, shell=True)
    chunks = vectorstore_lib.splitting_of_docs([doc], splitter)
    vectordb = vectorstore_lib.new_vectordb(chunks, 
                                embedding,
                                persist_directory
        )
    retriever_obj = vectordb
    return get_table_entry(retriever_obj, prompt, question, verbose=verbose, print_chunks=print_chunks)

if __name__ == "__main__":
    ## Loading files
    docs, nb_files = load_pdf.load_files(data_dir, loader_method='PyMuPDFLoader')
    print("Files :", [doc.metadata['source'] for doc in docs])
    print("Done loading files")

    ## Testing the language prompt
#     prompt_template = pr_languages.template
#     prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
# #    test_prompt(docs[0], prompt, "languages")
#     for doc in docs:
#         test_prompt(doc, prompt, "languages", print_chunks=False)

    print("Creating/accessing the MySQL database...")
    password = getpass.getpass("Enter your MySQL password: ")
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
    )
    cursor = mydb.cursor()
    initialize_database(mydb)
    print("Done initializing")
    for doc in docs:
        add_one_cv(cursor, doc, verbose=True)
        mydb.commit()
    test_filling(cursor)
    cursor.close()
    mydb.close()