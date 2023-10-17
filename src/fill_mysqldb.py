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

from langchain.document_loaders import PyMuPDFLoader
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
llm_name = 'gpt-3.5-turbo'
llm = ChatOpenAI(model_name=llm_name, temperature=0)

def add_one_cv(db_cursor, doc, table_prompts, force_refill=False, save=True, verbose=False):  
    # todo : plutôt prendre un doc déja loadé par un fichier de loading appelé depuis fill_whole_template
    """
    Inputs:
        ...
    """

    fields = list(table_prompts) 

    # if already loaded and not force_refill, print and return accordingly
    if False :
        return
    else:
        if verbose:
            print("Filling the template for " + doc.metadata['source'] + "...\n")
        data = [doc.metadata['source']] # First field is the filename

        ## Vectorstore and retriever creation
        subprocess.run('rm -rf ' + persist_directory, shell=True)
        chunks = vectorstore_lib.splitting_of_docs(doc, splitter)
        vectordb = vectorstore_lib.new_vectordb(chunks, 
                                embedding, 
                                persist_directory
        )
        retriever_obj = vectordb

        for field in fields[1:]:    # Omitting the first field (=filename)
            ## Prepare chain with prompt template
            prompt_template = prompts_df[field][0]
            prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
            chain = call_to_llm.create_chain(llm, prompt)

            ## Retrieving and calling the LLM
            sources = vectorstore_lib.retrieving(retriever_obj, field, retriever_type="vectordb", with_scores=True)
            context = call_to_llm.create_context_from_chunks(sources)
            answer = chain.predict(context=context, field=field)
            data.append(answer)
            if verbose:
                print(f"Filling the {field}... Here are the retrieved chunks with scores: \n\n")
                call_to_llm.print_chunks(sources)
                print(data)
        if save:  # todo : use mysql connector to update the database
            # if file in template_df["Filename"].unique():
            #     template_df.loc[template_df["Filename"] == file] = data
            # else:
            #     new_row = pd.DataFrame(columns=fields, data=[data])
            #     template_df = pd.concat([template_df, new_row], ignore_index=True)
            #     template_df.to_csv(template_path, index=False)
            print("to implement")
        return data

def fill_database(cursor, docs, table_prompts, print_time=True, force_refill=False):
    t0 = time.time()
    for doc in docs:
        try:
            add_one_cv(cursor, doc, table_prompts, force_refill=force_refill, save=True, verbose=True)
        except:
            print("Error filling the database for " + doc)
    if print_time:
        print("Time to fill the database with new CVs : {:.2f}s".format(time.time()-t0))

def initiate_database(database, verbose=True):
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
    initiate_database(mydb)
    prompts_df = load_csv.load_csv(table_prompts_path)
    docs = load_pdf.load_files(data_dir, persist_directory=persist_directory, loader_method='PyMuPDFLoader')

    cursor.close()
    mydb.close()