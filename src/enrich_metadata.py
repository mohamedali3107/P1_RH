from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import loading_preprocessing_multi
import prompts.prompt_extract_names as pr_names
import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key  = os.environ['OPENAI_API_KEY']

def add_name_as_metadata(docs, data_dir, llm='default') :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    list_of_names_as_str = ""
    files = loading_preprocessing_multi.list_of_files(data_dir)
    prompt_names = pr_names.prompt_file_name  # asks for list of lists [bool, "name" or None]
    chain = LLMChain(llm=llm, prompt=prompt_names)
    inputs = []
    for file in files :
        inputs.append({"file" : file})
    list_of_outputs = chain.apply(inputs)
    list_of_res = [eval(output['text']) for output in list_of_outputs] # list of [bool, "name" or None]
    # one res per file (or per several documents (pages))
    i = 0  # index in files or list_of_res (same length)
    j = 0  # index in docs; more j values than i values if several pages per file
    if len(files) > 0 :
        # first values
        file_prec = data_dir + files[0]    # first file, will be used for comparison
        if list_of_res[0][0] == True :     # full name was found in file name
            name = list_of_res[0][1]  # name of first candidate
        else :
            name = find_name_in_CV(docs[0], llm)  # we assume the name appears on the first page
        list_of_names_as_str = name
        # following values
        while i < len(files) :
            while j < len(docs) and docs[j].metadata['source'] == file_prec :  # new page of same CV
                docs[j].metadata['name'] = name  # add field
                j += 1
            if j == len(docs) :  # done
                break
            # else docs[j] belongs to new CV (hence a new CV exists so i may safely be incremented)
            i += 1
            if list_of_res[i][0] == True :  # full name was found in file name
                name = list_of_res[i][1]
            else :
                name = find_name_in_CV(docs[j], llm)  # we assume the name appears on the first page
            file_prec = data_dir + files[i]
            list_of_names_as_str += ", " +  name
    return docs, list_of_names_as_str

def find_name_in_CV(doc, llm='default') :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    prompt_name_in_text = prompt_extract_names.prompt_name_in_text  # asks for list of lists [bool, "name" or None]
    chain = LLMChain(llm=llm, prompt=prompt_name_in_text)
    context = doc.page_content
    if len(context) >= 2000 :
        context = context[:2000]
    inputs = [{"context" : context}]
    output = chain.apply(inputs)[0]['text']
    return output

def add_metadata(docs, query) :
    return