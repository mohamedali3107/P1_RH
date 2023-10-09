import call_to_llm
from itertools import chain

def format_for_gradio(prompt, question, answer, with_source=True, print_prompt=True, chunks=[]): 
    '''Input: A natural (non prompt-engineered) question and a boolean indicating whether or not to print the source
    
    Output: the answer furnished by the LLM followed by the source chunks content, metadata and similarity scores

    (source = relevant)
    '''

    nb_chunks = len(chunks)

    # Stacking the relevant chunks into a context string
    context = call_to_llm.create_context_from_chunks(chunks)

    # Building the prompt
    exact_prompt = prompt.format(context=context, question=question)

    # Building the output
    data_to_print = [answer]
    if with_source :
          data_to_print += list(chain.from_iterable((chunks[i].page_content, chunks[i].metadata) for i in range(nb_chunks)))
    else :  # useful ? means that we provided chunks but did not ask to print them
          data_to_print += list(chain.from_iterable(('N/A', 'N/A') for i in range(nb_chunks)))
    if print_prompt :
          data_to_print += [exact_prompt]
    return data_to_print