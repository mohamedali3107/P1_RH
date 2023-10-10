import os
import openai
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import numpy as np
import subprocess
import gradio as gr
import vectorstore_lib
import call_to_llm

from langchain.document_loaders import PyMuPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']

cv_path = "data/cv/"
complete_paths = [cv_path+file for file in os.listdir(cv_path) if 'pdf' in file]

## Loading the info template
template_df = pd.read_csv("dataTemplateConcise.csv")
fields = list(template_df.iloc[:,1:]) # Avoiding the index field
## Choice of the prompt template to feed the LLM

# Prompt asking to directly fill a template
prompt_global = """ The texts provided to you are the resumes of the candidates.
Your task is to answer the user question in a structured way as in the following format.

<Desired format>

Please extract the first name in the resume
First name:
Please extract the last name in the resume
Last name:
Please extract the phone number in the resume
Phone number:
Please extract the email contact in the resume
Email adress:
Please extract the language skills mentioned in the resume
Languages :
Please extract the technical skills mentioned in the resume
Technical skills:
Please extract the last experience of the candidate
Last experience:

</Desired format>

Take your time to read carrefuly the pieces in the context to answer the question.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Keep the answer as concise as possible. 

Always say "thanks for asking!" at the end of the answer.
{context}
"""

# Generic prompt
prompt_generic = """You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the {field} of the person in this CV.
Your output should be only the {field}, do not make a sentence.
Do not provide answer out of the context pieces. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
{field} of the person :
"""

# Different prompt for each field
prompts_df = pd.read_csv("promptTemplatesConcise.csv")

########## LLM Chain parameters ##########

persist_directory = './chroma_single/'
loader_method = 'PyMuPDFLoader'
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40, 
    separators=["\n\n", "\n", " ", ""]
)
embedding = OpenAIEmbeddings()
nb_chunks = 4 
llm_name = 'gpt-3.5-turbo'
llm = ChatOpenAI(model_name=llm_name, temperature=0)

def fill_template(file, save=False):
    
    loader = PyMuPDFLoader(file)
    cv = loader.load()
    data = [file] # First field is the filename

    ## Vectorstore creation

    subprocess.run('rm -rf ./chroma_single/', shell=True)
    chunks = vectorstore_lib.splitting_of_docs(cv, splitter)
    vectordb = vectorstore_lib.new_vectordb(chunks, 
                            embedding, 
                            persist_directory
    )    

    for field in fields[1:]:    # Omitting the first field which corresponds to the filename

        ## Prepare chain with prompt template

        # prompt_template = prompts_df[field][0]
        # prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
        prompt = PromptTemplate(template=prompt_generic, input_variables=["context","field"])
        chain = call_to_llm.create_chain(llm, prompt)

        ## Retrieving and calling the LLM
        sources = vectordb.similarity_search(field, k=nb_chunks)
        context = call_to_llm.create_context_from_retrieved_chunks(sources)
        answer = chain.predict(context=context, field=field)
        data.append(answer)
        #data.append(singleCV_Extraction.gradioQA(cv, "What is the " + field + " of the candidate ?", with_source=False, print_prompt=False)[0])
    df = pd.DataFrame(columns=fields, data=[data])
    if save:
        template_df.append(df)
#    return df
    return list(df.iloc[0])

demo = gr.Interface(
    fn = lambda file: fill_template(file),
    inputs =
    [
        gr.Dropdown(
            complete_paths, label="File", info="Select the file you want to analyze"
        )
    ],
    outputs=
    [
        #gr.Dataframe(label="Candidate Information")
        gr.Textbox(label = field) for field in fields
    ],
    description = "Analyzes a file according to the given template"
)

if __name__ == "__main__":
    demo.launch(inbrowser=True)


# file = complete_paths[0]
# print(fill_template(file, save=True))