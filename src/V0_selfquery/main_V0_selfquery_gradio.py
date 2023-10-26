import subprocess
import sys
sys.path.append("..")
from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
import gradio as gr
from itertools import chain as chain_list
from langchain.chains import LLMChain
# my modules
import vectorstore_lib
import prompts.prompt_multi_cv as pr_multi
import call_to_llm_V0 as call_to_llm
import gradio_lib
import loading.load_pdf as load_pdf
import loading.utils as utils

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']

########## QA V0 (FROM THE DOCS) ##########

########## Parameters ##########

data_dir = '../../data/'
persist_directory = '../../chroma_multi/'

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
docs, nb_files = load_pdf.load_files(data_dir, 
                                     check_directory=persist_directory, 
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
        description="The source CV the document is from, should be one of " + utils.list_of_files_as_str(data_dir),
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
prompt = pr_multi.prompt  # generic multi CV, see external file

def fn_gradio_QA(question, with_source, print_prompt) :
    '''Assumes : retriever_obj, prompt, llm (kinda dirty)'''
    chain = LLMChain(llm=llm, prompt=prompt)
    chunks = vectorstore_lib.retrieving(retriever_obj, question, retriever_type=retriever_type, with_scores=False)
    answer = call_to_llm.get_result(chain, chunks, question, print_source_docs=False, print_scores=False)
    return gradio_lib.format_for_gradio(prompt, question, answer, with_source=with_source, print_prompt=print_prompt, chunks=chunks)

demoGradioQA_MultipleCV = gr.Interface(
    fn = fn_gradio_QA,
    inputs = [gr.Textbox(label = 'Question', placeholder = 'Type your question here...'), gr.Checkbox(label = 'Print source'), gr.Checkbox(label = 'Print exact prompt fed to the LLM')],
    outputs = [gr.Textbox(label = 'Answer')] + list(chain_list.from_iterable((gr.Textbox(label = f'Chunk #{i+1}'), gr.Textbox(label = f'Metadata #{i+1}')) for i in range(nb_chunks))) + [gr.Textbox(label = 'Exact prompt')]
)

demoGradioQA_MultipleCV.launch(inbrowser=True)