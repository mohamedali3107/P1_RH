from langchain.chains import LLMChain

def create_context_from_retrieved_chunks(docs) :
    context = ""
    if len(docs) != 0 :
        if type(docs[0]) == tuple :  # case if scores have been attached (doc[1]=score)
            for doc in docs :
                context += "[[from " + doc[0].metadata['source'] + "]] :  " + doc[0].page_content + "\n\n"
                # todo : idéalement ce serait mieux d'indiquer les noms que la source
        else :  # without scores, docs = list of documents
            for doc in docs :
                context += "[ [from " + doc.metadata['source'] + "] ]   " + doc.page_content + "\n\n"
    else :
        print("No information retreived, vector data base could be empty or need recomputing.")
    return context

def create_chain(llm, prompt) :  # le retrieving sera fait manuellement pour le 'context' du prompt
    return LLMChain(llm=llm, prompt=prompt)

def get_result(chain, sources, question, print_source_docs=True, print_scores=True) :
    context = create_context_from_retrieved_chunks(sources)
    inputs = [{"context" : context, "question" : question}]
    # partie affichage avec les arguments optionnels
    if print_scores == True :
        i = 1
        for doc in sources :
            try :  # doc = tuple (document, score)
                print("[[source", i, "]]  ", doc[0].page_content,"\nscore :", round(1-doc[1], 4), "\n")  # higher is better
                i += 1
            except TypeError :  # en fait on n'a pas calculé les scores donc doc est juste un Document
                print("No scores computed with this retrieving method")
                break  # on affichera les sources sans scores
    elif print_source_docs == True :
        print("\n** source chunks **\n" + context)
    return chain.apply(inputs)   # liste de résultats de type {'text': '...'}, mm taille que inputs
    # todo : voir comment on pourrait passer un seul input plutôt qu'une liste