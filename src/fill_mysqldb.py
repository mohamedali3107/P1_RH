import os
import openai
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import subprocess
import gradio as gr
import time
import vectorstore_lib
import call_to_llm
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

def add_one_cv(db_cursor, doc, force_refill=False, save=True, verbose=False):
    # if already loaded and not force_refill, print and return accordingly
    if False :
        return
    else:
        filename = doc.metadata['source']
        if verbose:
            print("Filling the database with " + filename + "...\n")
        db_cursor.execute("SELECT NameFile FROM candidates")
        known_files = db_cursor.fetchall()
        if filename in known_files :
            print("CV already parsed.")
            return

        ## Vectorstore and retriever creation
        subprocess.run('rm -rf ' + persist_directory, shell=True)
        chunks = vectorstore_lib.splitting_of_docs(doc, splitter)
        vectordb = vectorstore_lib.new_vectordb(chunks, 
                                embedding,
                                persist_directory
        )
        retriever_obj = vectordb
        # todo : call to auxiliary functions
        add_one_cv_candidate(db_cursor, filename, retriever_obj, retriever_type="vectordb", force_refill=force_refill, save=True, verbose=verbose)
        # ...
        add_one_cv_language(db_cursor, retriever_obj, retriever_type="vectordb", save=True)
    
def format_languages(spoken_languages_str): # format the output of the llm
    # todo : implement depending of llm answer shape
    # eval(spoken_languages_str)   # <- typically, if already well formated by the llm
    return [("lang1", "niv1"), ("lang2, niv2")]

def get_table_entry(retriever_obj, prompt, retriever_type="vectordb", llm='default'):  # retrieving et llm
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

def add_one_cv_language(db_cursor, retriever_obj, retriever_type="vectordb", force_refill=False, save=True, verbose=False):
    ## Prepare chain with prompt template
    prompt_template = pr_languages.template
    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    chain = call_to_llm.create_chain(llm, prompt)

    ## Retrieving and calling the LLM
    question = "what is said about languages ?"
    sources = vectorstore_lib.retrieving(retriever_obj, question, retriever_type="vectordb", with_scores=True)
    context = call_to_llm.create_context_from_chunks(sources)
    answer = chain.predict(context=context)
    languages_with_level = format_languages(answer)
    if verbose:
        print(f"Filling the languages information... Here are the retrieved chunks with scores: \n\n")
        call_to_llm.print_chunks(sources)
        print(answer, "\n")
    if save:
        db_cursor.execute("SELECT NameLanguage FROM languages")
        known_languages = db_cursor.fetchall()
        for lang in languages_with_level:
            if lang not in known_languages:
                db_cursor.execute(f"""INSERT INTO languages (NameLanguage) 
                                  VALUES ('{lang}');""")
                
        # todo : fill the speaks table
        print("to implement")
    return

def add_one_cv_candidate(db_cursor, filename, retriever_obj, retriever_type="vectordb", force_refill=False, save=True, verbose=False):
    data = [filename]
    prompts_candidates = pr_candidates.dict  # dictionary of prompts to fill candidates

    for field in prompts_candidates :  # field must be exactly the name of an attribute
        prompt_template = prompts_candidates[field]
        prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
        chain = call_to_llm.create_chain(llm, prompt)

        ## Retrieving and calling the LLM
        sources = vectorstore_lib.retrieving(retriever_obj, field, retriever_type="vectordb", with_scores=True)
        context = call_to_llm.create_context_from_chunks(sources)
        answer = chain.predict(context=context)
        if verbose:
            print(f"Filling the {field} information... Here are the retrieved chunks with scores: \n\n")
            call_to_llm.print_chunks(sources)
            print(answer, "\n")
                
        # todo : fill the candidate table with each attribute (each field)
        # INSERT INTO customers (customer_name, email, address) VALUES ('John Doe', 'johndoe@example.com', '123 Main St');
        print("to implement")
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


if __name__ == "__main__":
    print("Creating/accessing the MySQL database...")
    #username = input("Enter your username : ")
    password = getpass.getpass("Enter your MySQL password: ")
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
    )
    cursor = mydb.cursor()
    initialize_database(mydb)
    prompts_df = load_csv.load_csv(table_prompts_path)
    docs = load_pdf.load_files(data_dir, persist_directory=persist_directory, loader_method='PyMuPDFLoader')

    cursor.close()
    mydb.close()