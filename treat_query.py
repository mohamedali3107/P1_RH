from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import prompt_mono_from_multi
import prompt_interrogate_field
import prompt_detect_mode
import prompt_format_name
import prompt_extract_names

def multi_to_mono(query_multi, llm='default') :
    '''Turn a question on all CV's into an individual question to be run on each CV'''
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    prompt_multi_to_mono = prompt_mono_from_multi.prompt_template
    chain_to_mono_query = LLMChain(llm=llm, prompt=prompt_multi_to_mono)
    return chain_to_mono_query.predict(question=query_multi)

def extract_target_field(query, list_of_fields, llm='default') :
    '''Determine what field is targeted by a query, among a list of possible fields'''
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    print(query)
    chain_field = LLMChain(llm=llm, prompt=prompt_interrogate_field.prompt_extract_field)
    fields = ", ".join(list_of_fields)
    return chain_field.predict(topics=fields, question=query)

def detect_query_type(question, llm='default') :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_detect_mode.prompt_english, llm=llm)
    answer = llm_chain.predict(question=question)
    # todo : Mettre une petite exception mieux que ça 
    if answer not in ["single", "transverse", "unknown"] :
         print("Question : " + question + "\nAnswer of detect_query_type :", answer)
         return "Error"
    else:
        return answer

def detect_operation_from_query(question, llm='default') :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_detect_mode.prompt_predict_operation, llm=llm)
    answer = llm_chain.predict(question=question)
    # todo : Mettre une petite exception mieux que ça 
    if answer not in ["Sort", "Comparison", "MinMax", "Condition", "All", "Unknown"] :
         print("Question : " + question + "\nAnswer from detect_operation_from_query :", answer)
         return "Error"
    else:
        return answer
    
def extract_name(query, llm='default'):
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_extract_names.prompt_name_in_query, llm=llm)
    return llm_chain.predict(context=query)
    
def identify_name(name_approx, list_names, llm='default'):
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_format_name.prompt_identify_name, llm=llm)
    answer = llm_chain.predict(context=list_names, name=name_approx)
    if answer not in list_names :
        print("Received name : " + name_approx + "\nAnswer from identify_name :", answer)
        return "Error"
    else:
        return answer
