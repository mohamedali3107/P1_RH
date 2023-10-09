from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import prompt_mono_from_multi
import prompt_interrogate_field

def multi_to_mono(query_multi, llm='default') :
    '''Turn a question on all CV's into an individual question to be run on each CV'''
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    prompt_multi_to_mono = prompt_mono_from_multi.prompt_template
    chain_to_mono_query = LLMChain(llm=llm, prompt=prompt_multi_to_mono)
    inputs = [{"question" : query_multi}]
    return chain_to_mono_query.apply(inputs)[0]['text']

def extract_target_field(query, list_of_fields, llm='default') :
    '''Determine what field is targeted by a query, among a list of possible fields'''
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    chain_field = LLMChain(llm=llm, prompt=prompt_interrogate_field.prompt_extract_field)
    fields = ", ".join(list_of_fields)
    inputs = [{"question" : query, "topics" : fields}]
    return chain_field.apply(inputs)[0]['text']