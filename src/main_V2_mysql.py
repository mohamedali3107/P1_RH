from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
# my modules 
import loading.utils as utils
import getpass
import mysql.connector
import fill_mysqldb as fill
import loading.load_pdf as load
import call_llm_on_db
from CVDataBase import CVDataBase
import gradio as gr

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']


# todo : faire autrement !
# par exemple : all_fields = db.select('column_name', 'information_schema.columns', condition=f"WHERE table_schema='{db.name}' AND table_name='{db.candidates.name}'")
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

def test_classes():
    db = CVDataBase()
    db.initialize()
    print(db.list_tables())
    docs, nb_files = load.load_files(data_dir)
    doc = docs[0]
    # One CV
    db.add_cv(doc)
    print(db.list_tables())
    select_cols = ['FirstName', 'FamilyName', 'PhoneNumber', 'Email']
    extract = db.select(select_cols, db.candidates.name)
    print('\nSome selected columns from the database :\n')
    for entry in extract :
        print(*entry)
    print('\n')
    # All CVs
    db.fill_all_cv(docs)
    extract = db.select(select_cols, db.candidates.name)
    print('\nSome selected columns from the database :\n')
    for entry in extract :
        print(*entry)
    print('\n')
    while True:
        query = input('\nquery (or quit) :  ')
        if query == 'quit':
            break
        print(db.ask_question(query))
    db.cursor.close()
    db.db.close()

def demo_fill(db, data_dir, filename) -> tuple:
    docs = load.load_single_pdf(data_dir, filename)
    doc = docs[0]
    db.add_cv(doc)
    values = db.select('*', db.candidates.name, condition=f"WHERE {db.candidates.primary_key}='{data_dir+filename}'")
    return values[0]

def run_demo(data_dir):
    filenames = utils.list_of_pdf_files(data_dir)
    db = CVDataBase()
    db.initialize()
    column_names = [res[0] for res in db.select('column_name', 'information_schema.columns', condition=f"WHERE table_schema='{db.name}' AND table_name='{db.candidates.name}'")]
    demo = gr.Interface(
        fn = lambda filename: demo_fill(db, data_dir, filename),
        inputs =
        [
            gr.Dropdown(
                filenames, label="File", info="Select the file you want to analyze"
            )
        ],
        outputs=
        [
            gr.Textbox(label = column) for column in column_names
        ],
        description = "Analyzes a file according to the given template"
    )
    demo.launch(inbrowser=True)
    db.cursor.close()
    db.db.close()
    return

if __name__ == "__main__":
    test_classes()

    ## running the gradio demo
    #run_demo(data_dir)

    ## todo: trash the following?
    # docs, nb_files = load.load_files(data_dir, loader_method='PyMuPDFLoader')
    # print("Files :", [doc.metadata['source'] for doc in docs])
    # print("Done loading files")
    # print("Creating/accessing the MySQL database...")
    # #username = input("Enter your username : ")
    # password = getpass.getpass("Enter your MySQL password: ")
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password=password,
    # )
    # cursor = mydb.cursor()
    # fill.initialize_database(mydb)
    # print("Done initializing")
    # for doc in docs:
    #     fill.add_one_cv(cursor, doc, verbose=True)
    #     mydb.commit()
    # cursor.execute("SELECT FirstName, FamilyName, PhoneNumber, Email FROM candidates;")
    # extract = cursor.fetchall()
    # print('\nSome selected columns from the database :\n')
    # for entry in extract :
    #     print(*entry)
    # print('\n')
    #query = input("query ? ")
    #res = call_llm_on_db.ask_filtered_query(cursor, query, list_of_names, all_fields, llm='default')
    #print(res)
    # cursor.execute("DESC candidates;")
    # cols = cursor.fetchall()
    # for col in cols :
    #    print(col[0])
    # cursor.close()
    # mydb.close()