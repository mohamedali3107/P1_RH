from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import treat_chunks
import vectorstore_lib


def create_chain(llm, prompt) :
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
    
def get_table_entry(retriever_obj, prompt, topic, verbose=False, 
                            print_chunks=False, retriever_type="vectordb", llm='default'):
    '''Input topic is used to retrieve the chunks on which to call the LLM
    The question is typically contained in the provided prompt
    '''
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt)
    ## Retrieving and calling the LLM
    sources = vectorstore_lib.retrieving(retriever_obj, topic,
                                         retriever_type=retriever_type, with_scores=True)
    context = treat_chunks.create_context_from_chunks(sources)
    answer = chain.predict(context=context)
    if verbose:
        print(f"Asking the LLM about {topic}... \n\n")
        print("Output of the LLM:", answer, "\n")
        if print_chunks:
            print("Here are the retrieved chunks with scores:")
            treat_chunks.print_chunks(sources)
    return answer

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
