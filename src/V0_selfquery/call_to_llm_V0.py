import sys
sys.path.append("..")
from langchain.chains import LLMChain
import treat_chunks


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