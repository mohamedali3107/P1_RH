import sys
sys.path.append("..")
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import prompts.prompt_extract_names as prompt_extract_names
import prompts.prompt_format_name as prompt_format_name
import prompts.prompt_single_cv as prompt_single_cv
import treat_query

def ask_filtered_query(dict_db, question, list_of_names, list_of_fields, llm='default') :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    # identify filter
    chain_extract_name = LLMChain(llm=llm, prompt=prompt_extract_names.prompt_name_in_query)
    name_approx = chain_extract_name.predict(context=question)
    chain_format_name = LLMChain(llm=llm, prompt=prompt_format_name.prompt_identify_name)
    name = chain_format_name.predict(context=list_of_names, name=name_approx)
    print('Candidate :', name)
    # identify field
    fields = treat_query.extract_target_fields(question, list_of_fields, llm=llm)
    # retrieve data
    data = []
    for field in fields :
        data.append(dict_db[field][name])
    chain = LLMChain(llm=llm, prompt=prompt_single_cv.prompt_from_field)
    return chain.predict(topic=fields, data=data, question=question)  # lists as inputs