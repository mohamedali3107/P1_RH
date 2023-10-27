from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
# my modules 
import loading.utils as utils
import loading.load_pdf as load
from database_classes.CVDataBase import CVDataBase
import gradio as gr

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']


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
    # candidates_values and languages_values are lists corresponding to a single row, hence the [0]
    candidates_values = db.select('*', db.candidates.name, condition=f"WHERE {db.candidates.primary_key}='{data_dir+filename}'")[0] 
    languages_values = db.select(['NameLanguage, LanguageLevel'], db.entities['languages'].relation_name, condition=f"WHERE Candidate='{data_dir+filename}'")[0]
    return candidates_values

def run_demo(data_dir, demo_questions):
    filenames = utils.list_of_pdf_files(data_dir)
    db = CVDataBase()
    db.initialize()
    column_names = [res[0] for res in db.select('column_name', 'information_schema.columns', condition=f"WHERE table_schema='{db.name}' AND table_name='{db.candidates.name}'")]
    

    with gr.Blocks() as demo:
        gr.Markdown(
            f"""
            # Curriculum Vitae Parser
            Using {llm_name}.
            """)
        with gr.Tab("Info Extraction"):
            selected_filename = gr.Dropdown(
                    filenames, label="File", info="Select the file you want to analyze"
                )
            filled_template = [gr.Textbox(label = column) for column in column_names]
            selected_filename.change(lambda filename: demo_fill(db, data_dir, filename), selected_filename, filled_template)
        with gr.Tab("Q&A"):
            gr.Markdown(
            """
            This Q&A engine uses the information extracted beforehand from the following CVs:
            """)
            gr.Dropdown(
                            filenames, label="List of CVs"
                        )
            with gr.Row():
                with gr.Column():
                    question_from_sample = gr.Dropdown(
                            demo_questions, label="Choose a preselected question:"
                        )
                    answer_to_question_from_sample = gr.Textbox(label = "Answer:")
                    question_from_sample.change(lambda query: db.ask_question(query), question_from_sample, answer_to_question_from_sample)
                with gr.Column():
                    user_question = gr.Textbox(
                            label="Ask your own question:"
                        )
                    answer_to_user_question = gr.Textbox(label = "Answer:")
                    question_from_sample.change(lambda query: db.ask_question(query), user_question, answer_to_user_question)

    # query = demo_questions[0]
    # print(db.ask_question(query))
    demo.launch(inbrowser=True)
    db.cursor.close()
    db.db.close()
    return

if __name__ == "__main__":
    #test_classes()

    ## running the gradio demo
    demo_questions = [
    "List the phone numbers of all the candidates.",
    "What candidates are proficient in Python?",
    "What is the education of Léo?",
    "What are the skills of sebastien?",
    "What candidates speak English?"
    ]
    run_demo(data_dir, demo_questions=demo_questions)