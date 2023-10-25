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

    def __init__(self, database, sql_query: str, config_dict: dict):
        self.database = database
        self.dict = config_dict  # contains columns except primary and foreign key Candidate
        self.entity = DBTable(self.database, sql_query, is_entity=True)
        self.name = self.entity.name

    def fill(self, filename, retriever_obj,
                        retriever_type="vectordb", llm='default', verbose=True):
        if llm == 'default':
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        field = self.name
        if verbose:
            print(f"Filling the {self.name} information... \n\n")
        ## Retrieving and calling the LLM
        outputs = []
        for col in self.dict:
            prompt = PromptTemplate(template=self.dict[col]['prompt'], input_variables=['context'])
            answer = call_to_llm.get_table_entry(retriever_obj, prompt, field+' '+col,
                                                 verbose=verbose, print_chunks=True,
                                                 retriever_type=retriever_type, llm=llm)
            outputs.append(answer)
        cols = self.entity.columns(include_primary=False)  # includes foreign key Candidate
        self.entity.insert(cols, outputs + [filename])
