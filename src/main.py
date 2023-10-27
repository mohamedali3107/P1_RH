from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
# my modules 
import loading.utils as utils
import loading.load_pdf as load
from database_classes.CVDataBase import CVDataBase
from config_database_mysql import config_experience as experience
from config_database_mysql import config_education as education
from config_database_mysql import config_skills as skills
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

def demo_fill(db, data_dir, filename, force_refill) -> tuple:
    docs = load.load_single_pdf(data_dir, filename)
    doc = docs[0]
    db.add_cv(doc, force_refill)
    # below, db.select returns lists corresponding to a single row, hence the [0]
    candidates_values = db.select('*', db.candidates.name, condition=f"WHERE {db.candidates.primary_key}='{data_dir+filename}'")[0] 
    output = candidates_values
    # languages_values = db.select(['NameLanguage, LanguageLevel'], db.entities['languages'].relation_name, condition=f"WHERE Candidate='{data_dir+filename}'")[0]
    # output += languages_values
    # for unit in db.entities:
    #     if unit != 'languages':
    columns = list(education.config_dict.keys())
    output += db.select(columns, db.entities['education'].entity_name, condition=f"WHERE {db.candidates.primary_key}='{data_dir+filename}'")[0]
    columns = list(experience.config_dict.keys())
    output += db.select(columns, db.entities['experience'].entity_name, condition=f"WHERE {db.candidates.primary_key}='{data_dir+filename}'")[0]
    columns = list(skills.config_dict.keys())
    output += db.select(columns, db.entities['skills'].entity_name, condition=f"WHERE {db.candidates.primary_key}='{data_dir+filename}'")[0]
    
    return output

def fill_and_ask(db, data_dir, query, force_refill):
    docs, nb_files = load.load_files(data_dir)
    db.fill_all_cv(docs, force_refill)
    return db.ask_question(query)

def display_list(filenames, bool):
    if bool:
        return filenames

def run_demo(data_dir, demo_questions, with_gradio=True):
    filenames = utils.list_of_pdf_files(data_dir)
    db = CVDataBase()
    db.initialize()

    if with_gradio:
        candidates_column_names = [column for (column,) in db.select('column_name', 'information_schema.columns', condition=f"WHERE table_schema='{db.name}' AND table_name='{db.candidates.name}'")]
        with gr.Blocks() as demo:
            gr.Markdown(
                f"""
                # Curriculum Vitae Parser
                Using {llm_name}.
                """)
            with gr.Tab("Info Extraction"):
                with gr.Row():
                    with gr.Column():
                        filled_template = [gr.Textbox(label = column) for column in candidates_column_names] + [gr.Textbox(label = 'Education'), gr.Textbox(label = 'Experience'), gr.Textbox(label = 'Skills')]
                    with gr.Column():
                        selected_filename = gr.Dropdown(
                                filenames, label="File", info="Select the file you want to analyze"
                            )
                        check_force_refill = gr.Checkbox(label="Refill database with this CV")
                        launch_btn = gr.Button("Launch")
                        launch_btn.click(fn=lambda filename, force_refill: demo_fill(db, data_dir, filename, force_refill), inputs = [selected_filename, check_force_refill], outputs=filled_template, api_name="CV Extractor")
            with gr.Tab("Q&A"):
                gr.Markdown(
                """
                This Q&A engine uses the information extracted beforehand from the following CVs:
                """)
                with gr.Row():

                    display_list_of_cvs = gr.Checkbox(label = "Display the list of CVs")
                    list_of_cvs = gr.Textbox(
                                    label="List of CVs:"
                            )
                    list_of_cvs.change(lambda bool: display_list(filenames, bool), display_list_of_cvs, list_of_cvs)
                with gr.Row():
                    with gr.Column():
                        question_from_sample = gr.Dropdown(demo_questions, label="Choose a question:")
                        check_force_refill_question_from_sample = gr.Checkbox(label="Refill the database before generating an answer")
                        submit_btn_question_from_sample = gr.Button("Generate answer")
                        answer_to_question_from_sample = gr.Textbox(label = "Answer:")
                        submit_btn_question_from_sample.click(fn=lambda query, force_refill: fill_and_ask(db, data_dir, query, force_refill), inputs=[question_from_sample, check_force_refill_question_from_sample], outputs=answer_to_question_from_sample, api_name="Answer to question from sample")
                    with gr.Column():
                        user_question = gr.Textbox(label="Ask your own question:") 
                        check_force_refill_user_question = gr.Checkbox(label="Refill the database before generating an answer")
                        submit_btn_user_question = gr.Button("Generate answer")
                        answer_to_user_question = gr.Textbox(label = "Answer:")
                        submit_btn_user_question.click(fn=lambda query, force_refill: fill_and_ask(db, data_dir, query, force_refill), inputs=[user_question, check_force_refill_user_question], outputs=answer_to_user_question, api_name="Answer from user question")
        demo.launch(inbrowser=True)
    
    else:
        filename = filenames[0]
        print('File to be analyzed', filename)
        print(demo_fill(db, data_dir, filename))

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