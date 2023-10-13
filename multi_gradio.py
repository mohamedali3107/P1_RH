import subprocess
import sys
from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
import gradio as gr
from itertools import chain as chain_list
# my modules 
import loading_preprocessing_multi
import vectorstore_lib
import prompt_multi_cv
import call_to_llm
import gradio_lib
import fill_template

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']

########## QA V0 (FROM THE DOCS) ##########

########## Parameters ##########

data_dir = 'data/'
persist_directory = './chroma_multi/'

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

######### Initialization ######

## Cleaning of old data, if shell query at launching
if len(sys.argv) > 1 and sys.argv[1] == 'clean' :
    subprocess.run('rm -rf ' + persist_directory + '*', shell=True)

## Vectorstore creation
docs, nb_files = loading_preprocessing_multi.load_files(data_dir, 
                                                        persist_directory=persist_directory, 
                                                        loader_method=loader_method
                                                        )
vectordb, list_of_names_as_str = vectorstore_lib.create_vector_db(docs, 
                                                                  data_dir, 
                                                                  splitter, 
                                                                  embedding, 
                                                                  persist_directory,
                                                                  enrich_with_name=False
                                                                  )
## Filter infrastructure with self query retriever
metadata_field_info = [
    AttributeInfo(
        name="source",
        description="The source CV the document is from, should be one of " + loading_preprocessing_multi.list_of_files_as_str(data_dir),
        type="string",
     ),
    AttributeInfo(
        name="name",
        description="The full name of the candidate, should be one of" + list_of_names_as_str,
        type="string",
     ),
]
print("Names of candidates :", list_of_names_as_str)
document_content_description = "The Curriculum Vitae of the candidates"
retriever_with_filter = SelfQueryRetriever.from_llm(
    llm,
    vectordb,
    document_content_description,
    metadata_field_info,
    search_kwargs = {'k': nb_chunks},
    verbose=True,
    #search_type="mmr"  # marche moins bien, pour les noms en tout cas
)
retriever_obj = retriever_with_filter

## Prepare chain with prompt template
prompt = prompt_multi_cv.prompt  # generic multi CV, see external file

def fn_gradio_QA(question, with_source, print_prompt) :
    '''Assumes : retriever_obj, prompt, llm (kinda dirty)'''
    chain = call_to_llm.create_chain(llm, prompt)
    chunks = vectorstore_lib.retrieving(retriever_obj, question, retriever_type=retriever_type, with_scores=False)
    answer = call_to_llm.get_result(chain, chunks, question, print_source_docs=False, print_scores=False)
    return gradio_lib.format_for_gradio(prompt, question, answer, with_source=with_source, print_prompt=print_prompt, chunks=chunks)

demoGradioQA_MultipleCV = gr.Interface(
    fn = fn_gradio_QA,
    inputs = [gr.Textbox(label = 'Question', placeholder = 'Type your question here...'), gr.Checkbox(label = 'Print source'), gr.Checkbox(label = 'Print exact prompt fed to the LLM')],
    outputs = [gr.Textbox(label = 'Answer')] + list(chain_list.from_iterable((gr.Textbox(label = f'Chunk #{i+1}'), gr.Textbox(label = f'Metadata #{i+1}')) for i in range(nb_chunks))) + [gr.Textbox(label = 'Exact prompt')]
)

#demoGradioQA_MultipleCV.launch(inbrowser=True)

########## QA V1 (FROM THE FILLED CSV) ##########

def fn_gradio_QA_from_csv(question):
    """Double pdfs should be removed from the data folder"""
    fill_template.fill_whole_template(fill_template.template_path, fill_template.complete_paths, print_time=False, force_refill=False)
    csv_file = loading_preprocessing_multi.load_csv(fill_template.template_path)
    dict_db = {}
    loaded = {}
    loading_preprocessing_multi.load_full_csv_to_dict(csv_file, dict_db, loaded)
    return call_to_llm.ask_question_dict(dict_db, csv_file, loaded, question, chain='default', llm='default')

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