import os
import openai
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import subprocess
import gradio as gr
import time
import vectorstore_lib
import call_to_llm

from langchain.document_loaders import PyMuPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']

template_path = "data_template_concise.csv"
cv_path = "data/"
complete_paths = [cv_path+file for file in os.listdir(cv_path) if 'pdf' in file]

# Loading the prompt templates (different for each field)
prompts_df = pd.read_csv("prompt_templates_concise.csv")


########## LLM Chain parameters ##########

persist_directory = './chroma_single/'
loader_method = 'PyMuPDFLoader'
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100, 
    separators=["\n\n", "\n", " ", ""]
)
embedding = OpenAIEmbeddings()
llm_name = 'gpt-3.5-turbo'
llm = ChatOpenAI(model_name=llm_name, temperature=0)

def fill_one_row(template_path, file, force_refill, save=False, verbose=False):

    template_df = pd.read_csv(template_path)
    fields = list(template_df) 

    if not force_refill and file in template_df["Filename"].unique():
        print("This CV has already been parsed")
        return template_df.loc[template_df["Filename"] == file].values.tolist()[0] # Returns the corresponding row
    
    else:
        if verbose:
            print("Filling the template for " + file + "...\n")
        loader = PyMuPDFLoader(file)
        cv = loader.load()
        data = [file] # First field is the filename

        ## Vectorstore and retriever creation
        subprocess.run('rm -rf ./chroma_single/', shell=True)
        chunks = vectorstore_lib.splitting_of_docs(cv, splitter)
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
        new_row = pd.DataFrame(columns=fields, data=[data])
        if save:
            template_df = pd.concat([template_df, new_row], ignore_index=True)
            template_df.to_csv(template_path, index=False)
        return list(new_row.iloc[0])

def fill_whole_template(template_path, complete_paths, print_time, force_refill=True):
    t0 = time.time()
    for file in complete_paths:
        try:
            fill_one_row(template_path, file, force_refill, save=True, verbose=True)
        except:
            print("Error filling the template for " + file)
    if print_time:
        print("Time to fill the template for all CVs: {:.2f}s".format(time.time()-t0))

# file = complete_paths[0]
# print(fill_one_row(template_path, file, verbose=True))

if __name__ == "__main__":
    fill_whole_template(template_path, complete_paths, print_time=True)