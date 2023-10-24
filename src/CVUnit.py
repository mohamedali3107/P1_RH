from DBTable import DBTable
from prompts import prompt_candidates as pr_candidates
import treat_chunks
import vectorstore_lib
import call_to_llm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# todo : implement
# Will not work in current state

class CVUnit():

    def __init__(self, database, entity_name: str, sql_query: str):
        self.database = database
        self.name = entity_name
        self.entity = DBTable(self.name, sql_query)

    def fill(self, filename, retriever_obj, prompt_template, 
                        retriever_type="vectordb", llm='default', verbose=True):
        if llm == 'default':
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        field = self.name
        prompt = PromptTemplate(template=prompt_template, input_variables=['context'])
        chain = call_to_llm.create_chain(llm, prompt)   # call_to_llm un peu useless
        ## Retrieving and calling the LLM
        sources = vectorstore_lib.retrieving(retriever_obj, field, retriever_type=retriever_type, with_scores=True)
        context = treat_chunks.create_context_from_chunks(sources)
        answer = chain.predict(context=context)
        if verbose:
            print(f"Filling the {self.name} information... \n\n")
            treat_chunks.print_chunks(sources)
            print(answer, "\n")
        cols = self.table.columns(include_primary=False)
        # todo: generalize for when there will be more columns
        self.table.insert(cols, [answer, filename])
