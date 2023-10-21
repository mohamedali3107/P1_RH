from langchain.chains import LLMChain
import treat_query
import manage_transversal_query
import filtered_query
#import loading_preprocessing_multi
import loading.load_from_csv as load_from_csv
from langchain.chat_models import ChatOpenAI
import prompts.prompt_extract_names as prompt_extract_names
import prompts.prompt_format_name as prompt_format_name
import prompts.prompt_single_cv as prompt_single_cv
import get_db_info


def create_chain(llm, prompt) :  # le retrieving sera fait manuellement pour le 'context' du prompt
    return LLMChain(llm=llm, prompt=prompt)

def ask_question_multi(dict_db, query_multi, list_of_fields, chain='default', llm='default') :
    try :
        fields_involved = treat_query.extract_target_fields(query_multi, list_of_fields, llm=llm)
    except Exception as err :
        print(*err.args)
        fields_involved = ['unknown']  # todo : plutôt [] mais à gérer dans fonctions appelées
    operation = treat_query.detect_operation_from_query(query_multi, llm=llm)
    if operation == 'Condition' or operation == 'Comparison' :
        mono_query = treat_query.multi_to_mono(query_multi)
        outputs = manage_transversal_query.outputs_from_dict(dict_db, mono_query, fields_involved, chain=chain, llm=llm)
        selected_candidates = []
        for meta in outputs :
            if outputs[meta] == 'Yes' :
                selected_candidates.append(meta)
        if selected_candidates == [] :
            print('No candidates seem to meet the condition.')
        return ", ".join(selected_candidates)
    elif operation == 'All' :
        mono_query = treat_query.multi_to_mono(query_multi)
        outputs = manage_transversal_query.outputs_from_dict(dict_db, mono_query, fields_involved, chain=chain, llm=llm)
        global_output = ""
        for meta in outputs :
            global_output += meta + ' : ' + outputs[meta] + '\n'
        return global_output
    else :
        print('Type of tranversal question not supported yet')
        return ''

def ask_question(cursordb, csv_file, all_loaded, question, chain='default', llm='default') :
    '''Assumes all CVs to study have been loaded (ideally does not assume all fields and loads missing, todo)'''
    list_of_fields = get_db_info.list_of_fields(cursordb)
    try :
        mode = treat_query.detect_query_mode(question, llm=llm)
    except Exception as err :
        print(*err.args)
        mode = 'unknown'
    if mode == 'transverse' :
        return ask_question_multi(cursordb, question, list_of_fields, chain=chain, llm=llm)
    elif mode == 'single' :
        # todo : exceptions
        list_of_names = list(all_loaded.values())
        return ask_filtered(cursordb, question, list_of_names, list_of_fields, llm=llm)
    else :
        return('Mode transverse/single unclear')

def ask_filtered(cursordb, question, list_of_names, all_fields, llm='default') :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    # identify filter
    chain_extract_name = LLMChain(llm=llm, prompt=prompt_extract_names.prompt_name_in_query)
    name_approx = chain_extract_name.predict(context=question)
    chain_format_name = LLMChain(llm=llm, prompt=prompt_format_name.prompt_identify_name)
    name = chain_format_name.predict(context=list_of_names, name=name_approx)
    print('Candidate :', name)
    # identify field
    fields = treat_query.extract_target_fields(question, all_fields, llm=llm)
    # retrieve data
    data = []
    for field in fields :
        first, fam = name.split(" ")
        query = f"""SELECT {field} FROM candidates WHERE FirstName = '{first}' AND FamilyName = '{fam}';"""
        cursordb.execute(query)
        entry = cursordb.fetchall()[0][0]
        data.append(entry)
    chain = LLMChain(llm=llm, prompt=prompt_single_cv.prompt_from_field)
    return chain.predict(topic=fields, data=data, question=question)  # lists as inputs
