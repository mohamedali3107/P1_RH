from langchain.chains import LLMChain
import treat_query
import manage_transversal_query
import filtered_query
#import loading_preprocessing_multi
import loading.load_from_csv as load_from_csv
import treat_chunks

def create_chain(llm, prompt) :  # le retrieving sera fait manuellement pour le 'context' du prompt
    return LLMChain(llm=llm, prompt=prompt)

def get_result(chain, chunks, question, print_source_docs=True, print_scores=True, multi_inputs=False) :
    '''Call the llm on retrieved chunks with the provided question.
    Options to print source chunks and scores.
    Scores will only be printed if they were provided with the source chunks (as an output of the retriever)
    Sources are automatically printed if scores were asked for.
    Output: string, or list of results [{'text': '...'},...] if multi_inputs
    '''
    if print_source_docs :
        treat_chunks.print_chunks(chunks, with_scores=print_scores)
    context = treat_chunks.create_context_from_chunks(chunks)
    # partie affichage avec les arguments optionnels
    if not multi_inputs :
        return chain.predict(context=context, question=question)
    else :
        inputs = [{"context" : context, "question" : question}]
        return chain.apply(inputs)  # list of results [{'text': '...'},...]

def print_multi_result(inputs, results, print_context : bool =False) :
    '''Input : 
            inputs  : (list of) dictionaries having a 'question' key
            results : (list of) results [{'text': '...'},...]
    '''
    if type(results) == list :
        for i in range(len(results)) :
            print("  question : ", inputs[i]['question'])
            print("    answer : ", results[i]['text'], "\n")
            if print_context :
                print("    source : ", inputs[i]['context'])
    else :
        print(results['text'])

######## On structured CVs #########

def create_context_from_dict(dict_db : dict, field : str) :
    '''Just in case (typically for non quantitative questions)'''
    context = field + ' of candidates : \n\n'
    for meta in dict_db[field] :
        context += '  <' + meta + '>:  ' + dict_db[field][meta] + '\n\n'
    return context

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

def ask_question(dict_db, csv_file, all_loaded, question, chain='default', llm='default') :
    '''Assumes all CVs to study have been loaded (ideally does not assume all fields and loads missing, todo)'''
    print("call to ask_question")
    list_of_fields = load_from_csv.list_of_fields_csv(csv_file)
    print("fields recovered")
    try :
        mode = treat_query.detect_query_mode(question, llm=llm)
    except Exception as err :
        print(*err.args)
        mode = 'unknown'
    if mode == 'transverse' :
        return ask_question_multi(dict_db, question, list_of_fields, chain=chain, llm=llm)
    elif mode == 'single' :
        # todo : exceptions
        list_of_names = list(all_loaded.values())
        return filtered_query.ask_filtered_query(dict_db, question, list_of_names, list_of_fields, llm=llm)
    else :
        return('Mode transverse/single unclear')
    
def test_question_dico() :
    csv_file = load_from_csv.load_csv("data_template_concise_no_double.csv")
    dict_db = {}
    loaded = {}
    load_from_csv.load_full_csv_to_dict(csv_file, dict_db, loaded)
    print(list(loaded.values()))
    question = input("query ? ")
    res = ask_question(dict_db, csv_file, loaded, question, chain='default', llm='default')
    print(res)