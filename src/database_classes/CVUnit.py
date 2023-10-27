import sys
sys.path.append('..')
from database_classes.DBTable import DBTable
from llm_calling import call_to_llm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# todo : implement

class CVUnit():
    '''Entities education, experience, skills'''

    def __init__(self, database, sql_query: str, config_dict: dict, sql_query_relation: str = ''):
        self.database = database
        self.dict = config_dict  # contains columns except primary and foreign key Candidate
        self.entity_table = DBTable(self.database, sql_query, is_entity=True)
        self.entity_name = self.entity_table.name
        self.has_relation = bool(sql_query_relation)
        if self.has_relation:
            self.relation_table = DBTable(self.database, sql_query_relation, is_entity=False)
            self.entity_name = self.relation_table.name
        else:
            self.relation_table = ''
            self.relation_name = ''

    def fill(self, filename, retriever_obj,
                        retriever_type="vectordb", llm='default', verbose=True):
        if llm == 'default':
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        field = self.entity_name
        if verbose:
            print(f"Filling the {self.entity_name} information... \n\n")
        ## Retrieving and calling the LLM
        outputs = []
        for col in self.dict:
            prompt = PromptTemplate(template=self.dict[col]['prompt'], input_variables=['context'])
            answer = call_to_llm.get_table_entry(retriever_obj, prompt, field+' '+col,
                                                 verbose=verbose, print_chunks=True,
                                                 retriever_type=retriever_type, llm=llm)
            outputs.append(answer)
        cols = self.entity_table.columns(include_primary=False)  # includes foreign key Candidate
        self.entity_table.insert(cols, outputs + [filename])

    def attributes(self, include_relation=False):
        '''Return columns except for numeric id and foreign key'''
        attrib = self.entity_table.columns(include_primary=False)
        if self.has_relation and include_relation:
            attrib.extend(self.relation_table.columns(include_primary=False))
        return attrib
    
    def delete(self, filename):
        self.entity_table.delete(filename)
        if self.has_relation:
            self.relation_table.delete(filename)
