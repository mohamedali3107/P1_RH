from DBTable import DBTable
from config_database_mysql import config_candidates
import call_to_llm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

class Candidates() :
    
    def __init__(self, database):
        self.dict = config_candidates.dict_candidates  # could/should be a class attribute (or just a global)
        self.database = database
        self.primary_key = config_candidates.primary_key  # 'FileName'
        self.table = DBTable(database, sql_query=config_candidates.sql_query, is_entity=True)
        self.name = self.table.name  # 'candidates'
        self.files_names = {}

    def filenames(self):
        return list(self.files_names.keys())
    
    def candidates_names(self):
        return list(self.files_names.values())
    
    def related_file(self, name):
        for filename in self.files_names:
            if self.files_names[filename] == name:
                return filename
        # todo : exception
        return "unknown"

    def fill(self, filename, retriever_obj, retriever_type="vectordb", 
                        print_chunks=True, llm='default', verbose=True):
        columns, values = [config_candidates.primary_key], [filename]
        name = []
        for field in self.dict :
            prompt_template = self.dict[field]['prompt']
            prompt = PromptTemplate(template=prompt_template, input_variables=['context'])
            # todo: pass print_chunks as an argument of fill
            answer = call_to_llm.get_table_entry(retriever_obj, prompt, field,
                                                 verbose=verbose, print_chunks=print_chunks,
                                                 retriever_type=retriever_type,
                                                 llm=llm)
            if field == config_candidates.first_name :
                name = [answer] + name
            if field == config_candidates.family_name :
                name = name + [answer]
            columns.append(field)
            values.append(answer)
        name = " ".join(name)
        self.files_names[filename] = name
        self.table.insert(columns, values)

    def attributes(self):
        return self.table.columns()
