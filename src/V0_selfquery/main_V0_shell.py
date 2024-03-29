import subprocess
import sys
sys.path.append("..")
from langchain.text_splitter import RecursiveCharacterTextSplitter #TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.chains import LLMChain
# my modules
from loading import load_pdf
from loading import utils
import vectorstore_lib
import prompts.prompt_multi_cv as pr_multi
import call_to_llm_V0 as call_to_llm

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']

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
                                                                  enrich_with_name=True,
                                                                  llm=llm, # for enriching
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
prompt_multi = pr_multi.prompt  # generic multi CV, see external file
chain = LLMChain(llm=llm, prompt=prompt_multi)

######### Main loop #########

if __name__ == '__main__':
    while True :
        inpt = input("\nEnter your question or type quit :\n")
        if inpt == "quit" :
            break
        print('\n')
        sources = vectorstore_lib.retrieving(retriever_obj, inpt, retriever_type=retriever_type, with_scores=with_scores)
        print(call_to_llm.get_result(chain, sources, inpt, print_source_docs=True, print_scores=print_scores))

