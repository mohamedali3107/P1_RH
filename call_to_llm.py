from langchain.chains import LLMChain
import treat_query
import manage_transversal_query

def create_context_from_chunks(docs) :
    '''Concatenate the content of retrieved documents as a context to be fed to the llm
    Input: a list of documents
    Output: a string
    '''
    context = ""
    if len(docs) != 0 :
        i = 1
        if type(docs[0]) == tuple :  # case if scores have been attached (doc[1]=score)
            for doc in docs :
                context += "[ [source " + str(i) + " from " + doc[0].metadata['source'] + "] ] :  " + doc[0].page_content + "\n\n"
                i += 1
                # todo : idéalement ce serait mieux d'indiquer les noms que la source
        else :  # without scores, docs = list of documents
            for doc in docs :
                context += "[ [source " + str(i) + " from " + doc.metadata['source'] + "] ]   " + doc.page_content + "\n\n"
                i += 1
    else :
        print("No information retreived, vector data base could be empty or need recomputing.")
    return context

def create_chain(llm, prompt) :  # le retrieving sera fait manuellement pour le 'context' du prompt
    return LLMChain(llm=llm, prompt=prompt)

def print_chunks(chunks, with_scores=True) :
    if with_scores :
        try :  # doc = tuple (document, score)
            i = 1
            for doc in chunks :
                print("[ [source", i, "from " + doc[0].metadata['source'] + "] ] :  " + doc[0].page_content,"\nscore :", round(1-doc[1], 4), "\n")  # higher is better
                i += 1
        except TypeError :  # en fait on n'a pas calculé les scores donc doc est juste un Document
            print("No scores computed with this retrieving method.")
            print(create_context_from_chunks(chunks))  # sans scores
    else :
        print(create_context_from_chunks(chunks))

def get_result(chain, sources, question, print_source_docs=True, print_scores=True, multi_inputs=False) :
    '''Call the llm on retrieved chunks with the provided question.
    Options to print source chunks and scores.
    Scores will only be printed if they were provided with the source chunks (as an output of the retriever)
    Sources are automatically printed if scores were asked for.
    Output: string, or list of results [{'text': '...'},...] if multi_inputs
    '''
    if print_source_docs :
        print_chunks(sources, with_scores=print_scores)
    context = create_context_from_chunks(sources)
    # partie affichage avec les arguments optionnels
    if not multi_inputs :
        return chain.predict(context=context, question=question)
    else :
        inputs = [{"context" : context, "question" : question}]
        return chain.apply(inputs)  # list of results [{'text': '...'},...]

def print_multi_result(inputs, results, print_context=False) :
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

def create_context_from_dict(dict_db, field) :
    '''Just in case (typically for non quantitative questions)'''
    context = field + ' of candidates : \n\n'
    for meta in dict_db[field] :
        context += '  <' + meta + '>:  ' + dict_db[field][meta] + '\n\n'
    return context

def ask_question_multi(dict_db, query_multi, list_of_fields, chain='default', llm='default') :
    fields = treat_query.extract_target_field(query_multi, list_of_fields, llm=llm)
    print('detected field(s) :', fields)
    fields_as_list = fields.split(', ')
    operation = treat_query.detect_operation_from_query(query_multi, llm=llm)
    if operation == 'Condition' :
        mono_query = treat_query.multi_to_mono(query_multi)
        outputs = manage_transversal_query.outputs_from_dict(dict_db, mono_query, fields_as_list, chain=chain, llm=llm)
        selected_candidates = []
        for meta in outputs :
            if outputs[meta] == 'Yes' :
                selected_candidates.append(meta)
        if selected_candidates == [] :
            print('No candidates seem to meet the condition.')
        return ", ".join(selected_candidates)
    elif operation == 'All' :
        mono_query = treat_query.multi_to_mono(query_multi)
        outputs = manage_transversal_query.outputs_from_dict(dict_db, mono_query, fields_as_list, chain=chain, llm=llm)
        global_output = ""
        for meta in outputs :
            global_output += meta + ' : ' + outputs[meta] + '\n'
        return global_output
    else :
        print('Type of tranversal question not supported yet')
        return ''

def ask_question_dict(dict_db, question, list_of_fields, chain='default', llm='default') :
    mode = treat_query.detect_query_type(question, llm=llm)
    if mode == 'transverse' :
        return ask_question_multi(dict_db, question, list_of_fields, chain=chain, llm=llm)
    elif mode == 'single' :
        print('Not implemented yet')
    else :
        print('Mode transverse/single unclear')
    return ''
    

def query_apply_condition(dict_db, question, field) :
    return