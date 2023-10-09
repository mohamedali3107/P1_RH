from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import prompt_mono_from_multi
import prompt_interrogate_field
import prompt_detect_mode

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
    chain_field = LLMChain(llm=llm, prompt=prompt_interrogate_field.prompt_extract_field)
    fields = ", ".join(list_of_fields)
    return chain_field.predict(topics=fields, question=query)

def detect_query_type(question, llm='default'):
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    llm_chain = LLMChain(prompt=prompt_detect_mode.prompt, llm=llm)
    answer = llm_chain.predict(question=question)
    # todo : Mettre une petite exception mieux que ça 
    if answer not in ["single", "transverse", "unknown"]:
         print("Question : " + question + "\nRéponse de detect_query_type :", answer)
         return "Error"
    else:
        return answer