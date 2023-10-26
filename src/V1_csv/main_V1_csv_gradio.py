import subprocess
import sys
sys.path.append("..")
from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
import gradio as gr
# my modules
import call_to_llm
import fill_csv
import loading.load_from_csv as load_from_csv

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']


########## Parameters ##########

data_dir = '../data/'
persist_directory = '../chroma_multi/'
template_path = "../data_template_concise.csv"
complete_paths = [data_dir+file for file in os.listdir(data_dir) if '.pdf' in file]

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

########## QA V1 (FROM THE FILLED CSV) ##########

def fn_gradio_QA_from_csv(question : str):
    """Double pdfs should be removed from the data folder"""
    fill_csv.fill_whole_template(fill_csv.template_path, fill_csv.complete_paths, print_time=False, force_refill=False)
    csv_file = load_from_csv.load_csv(fill_csv.template_path)
    dict_db = {}
    loaded = {}
    load_from_csv.load_full_csv_to_dict(csv_file, dict_db, loaded)
    return call_to_llm.ask_question(dict_db, csv_file, loaded, question, chain='default', llm='default')

demo_questions = [
"List the phone numbers of all the candidates.",
"What candidates are proficient in Python?",
"What is the education of Léo?",
"What are the skills of sebastien?",
"What candidates speak English?"
]

with gr.Blocks() as demoGradioQA_FromCSV:
    gr.Markdown(
    """
    # Multi-CV Q&A Demo
    ## From a given sample of questions
    Select below the question you want to ask over the pool of candidates:
    """)
    question_from_sample = gr.Dropdown(
            demo_questions, label="Question:"
        )
    answer_from_sample = gr.Textbox(label = "Answer:")
    question_from_sample.change(fn_gradio_QA_from_csv, question_from_sample, answer_from_sample)
    # gr.Markdown(
    # """
    # ## From a user input question
    # Type the question you want to ask over the pool of candidates:
    # """)
    # question_from_input = gr.Textbox(label = "Question:")
    # answer_from_input = gr.Textbox(label = "Answer:")
    # with gr.Row():
    #     submit_btn = gr.Button("Submit")
    #     submit_btn.click(fn=fn_gradio_QA_from_csv, inputs=question_from_input, outputs=answer_from_input, api_name="multiQA_FromCSV")
    #     clear_btn = gr.ClearButton(value="Clear")
    #     clear_btn.click(fn=fn_gradio_QA_from_csv, inputs=question_from_input, outputs=answer_from_input)
    

demoGradioQA_FromCSV.launch(inbrowser=True)