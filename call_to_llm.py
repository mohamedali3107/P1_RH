from langchain.chains import LLMChain

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
