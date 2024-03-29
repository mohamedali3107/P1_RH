
import sys
sys.path.append("..")
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
# my modules
import prompts.prompt_single_cv as pr_single

#data_dir = 'data/' # todo : faire en sorte que pas besoin
# def list_of_outputs_from_vectorstore(vectordb, metadata_ids, query_multi, llm='default') :
#     if llm == 'default' :
#         llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
#     mono_query = treat_query.multi_to_mono(query_multi, llm=llm)
#     res = {}
#     for meta in metadata_ids :   # typiquement liste des noms
#         filtered_chunks = vectordb.similarity_search(
#             mono_query,
#             k=3,
#             filter={"source":data_dir+meta}  # todo : modifier pour généraliser (pas que fichier)
#         )
#         context = call_to_llm.create_context_from_retrieved_chunks(filtered_chunks)
#         template = prompt_single_cv.template_concise
#         PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])
#         chain = call_to_llm.create_chain(llm,  PROMPT)
#         inputs = [{"context" : context, "question" : mono_query}]
#         output = chain.apply(inputs)
#         res[meta] = output
#     return res

def outputs_from_dict(dict_db, question, fields, chain='default', llm='default', verbose=False) :
    if llm == 'default' :
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
    if chain == 'default' :
        chain = LLMChain(llm=llm, prompt=pr_single.prompt_from_field)
    outputs = {}
    # todo : exception
    for meta in dict_db[fields[0]] :
        data = []
        for field in fields :
            data.append(dict_db[field][meta])
        output = chain.predict(topic=fields, data=data, question=question) # lists
        outputs[meta] = output
        if verbose :
            print('Output of LLM for', meta, 'on field values', data, ':', output)
    return outputs