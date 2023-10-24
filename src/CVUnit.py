from DBTable import DBTable
from prompts import prompt_candidates as pr_candidates
import treat_chunks
import vectorstore_lib
import call_to_llm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# todo : implement

class CVUnit():
    '''Entities education, experience, skills'''

    def __init__(self, database, entity_name: str, sql_query: str):
        self.database = database
        self.name = entity_name
        self.entity = DBTable(self.name, sql_query)

    def fill(self, filename, retriever_obj, prompt_template, 
                        retriever_type="vectordb", llm='default', verbose=True):
        if llm == 'default':
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        field = self.name
        if verbose:
            print(f"Filling the {self.name} information... \n\n")
        ## Retrieving and calling the LLM
        prompt = PromptTemplate(template=prompt_template, input_variables=['context'])
        answer = call_to_llm.get_table_entry(retriever_obj, prompt, field,
                                             verbose=verbose, print_chunks=True,
                                             retriever_type=retriever_type, llm=llm)
        cols = self.table.columns(include_primary=False)
        # todo: generalize for when there will be more columns
        self.table.insert(cols, [answer, filename])
