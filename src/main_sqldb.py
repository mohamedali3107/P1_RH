import subprocess
import sys
from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
# my modules 
#import loading_preprocessing_multi
import vectorstore_lib
import prompts.prompt_multi_cv as pr_multi
import call_to_llm
import loading.load_pdf as load_pdf
import loading.utils as utils
import getpass
import sql_queries as sql
import mysql.connector
import fill_mysqldb as fill
import loading.load_pdf as load_pdf
import prompts.prompt_languages as pr_languages
import prompts.prompt_candidates as pr_candidates
import call_llm_on_db

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']


# todo : faire autrement !
all_fields = ["FileName"
"FirstName",
"FamilyName",
"Gender",
"Email",
"PhoneNumber",
"LinkedIn",
"Webpage",
"Country",
"City"
]

list_of_names = ["Leo SOUQUET", "Justine Falque", "Robert VESOUL", "Aymeric Bernard"]

########## QA V0 (FROM THE DOCS) ##########

########## Parameters ##########

data_dir = '../data/'
persist_directory = '../chroma_multi/'

## Loader :
loader_method = 'PyMuPDFLoader'

## Splitter :
r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40, 
    separators=["\n\n", "\n", " ", ""]
)
splitter = r_splitter

## Embedding :
embedding = OpenAIEmbeddings()

## Retriever options :
retriever_type = 'retriever'  # should be one of vectordb or retriever
nb_chunks = 4 #nb_files
with_scores = True  # if possible
print_scores = with_scores and (retriever_type=='vectordb')

## LLM :
llm_name = 'gpt-3.5-turbo'
llm = ChatOpenAI(model_name=llm_name, temperature=0)

if __name__ == "__main__":
    docs, nb_files = load_pdf.load_files(data_dir, loader_method='PyMuPDFLoader')
    print("Files :", [doc.metadata['source'] for doc in docs])
    print("Done loading files")
    print("Creating/accessing the MySQL database...")
    #username = input("Enter your username : ")
    password = getpass.getpass("Enter your MySQL password: ")
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
    )
    cursor = mydb.cursor()
    fill.initialize_database(mydb)
    print("Done initializing")
    for doc in docs:
        fill.add_one_cv(cursor, doc, verbose=True)
        mydb.commit()
    cursor.execute("SELECT FirstName, FamilyName, PhoneNumber, Email FROM candidates")
    extract = cursor.fetchall()
    print('\nSome selected columns from the database :\n')
    for entry in extract :
        print(*entry)
    print('\n')
    query = input("query ? ")
    res = call_llm_on_db.ask_filtered_query(cursor, query, list_of_names, all_fields, llm='default')
    print(res)
    cursor.close()
    mydb.close()