
def create_context_from_chunks(docs : list) :
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

def print_chunks(chunks : list, with_scores : bool = True) :
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