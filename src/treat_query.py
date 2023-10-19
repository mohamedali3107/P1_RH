from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import sys
sys.path.append('prompts/')
import prompts.prompt_mono_from_multi
import prompts.prompt_interrogate_field
import prompts.prompt_detect_mode
import prompts.prompt_extract_names
import prompts.prompt_format_name

def multi_to_mono(query_multi, llm='default', verbose=False) :
    '''Turn a question on all CV's into an individual question to be run on each CV'''
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    prompt_multi_to_mono = prompt_mono_from_multi.prompt_template
    chain_to_mono_query = LLMChain(llm=llm, prompt=prompt_multi_to_mono)
    return chain_to_mono_query.predict(question=query_multi)

def extract_target_fields(query, list_of_fields, llm='default', verbose=True) :
    '''Determine what field is targeted by a query, among a list of possible fields'''
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    chain_fields = LLMChain(llm=llm, prompt=prompt_interrogate_field.prompt_extract_fields)
    fields = ", ".join(list_of_fields)
    identified_fields = chain_fields.predict(topics=fields, question=query)
    identified_fields = identified_fields.split(', ')
    if identified_fields == ['unknown'] :
        print('Error : target field(s) could not be identified')
    if identified_fields[0] not in list_of_fields :  # todo : sublist
        raise Exception('extract_target_fields output is none of expected', list_of_fields, 
                        '\ninput = "' + query + '"', '\noutput = "' + identified_fields + '"')
    if verbose :
        print("Identified field(s) :", *identified_fields)
    return identified_fields

def detect_query_mode(question, llm='default', verbose=True) :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_detect_mode.prompt_english, llm=llm)
    mode = llm_chain.predict(question=question)
    if mode not in ["single", "transverse", "unknown"] :
        raise Exception('detect_query_mode did not provide expected output', 
                        '\nquery = "' + question + '"', '\noutput = "' + mode + '"')
    else :
        if verbose :
            print("Identified mode of query :", mode)
        return mode

def detect_operation_from_query(question, llm='default', verbose=True) :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_detect_mode.prompt_predict_operation, llm=llm)
    operation = llm_chain.predict(question=question)
    if operation not in ["Sort", "Comparison", "MinMax", "Condition", "All", "Unknown"] :
        raise Exception('detect_operation_from_query did not provide expected output', 
                        '\nquery = "' + question + '"', '\noutput = "' + operation + '"')
    else:
        if verbose :
            print("Identified type of transverse query :", operation)
        return operation
    
def extract_name(query, llm='default', verbose=False) :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_extract_names.prompt_name_in_query, llm=llm)
    name = llm_chain.predict(context=query)
    if verbose :
        print("Name as extracted :", name)
    return name
    
def identify_name(name_approx, list_names, llm='default', verbose=True) :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_format_name.prompt_identify_name, llm=llm)
    name = llm_chain.predict(context=list_names, name=name_approx)
    if name not in list_names :
        raise Exception('identify_name output is none of expected', list_names, 
                        '\ninput = "' + name_approx + '"', '\noutput = "' + name + '"')
    else:
        if verbose :
            print("Identified candidate :", name)
        return name
