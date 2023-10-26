from DBTable import DBTable
from CVUnit import CVUnit
import call_to_llm
from prompts import prompt_languages as pr_languages
from config_database_mysql import config_languages as languages
from langchain.prompts import PromptTemplate

class Languages(CVUnit):

    def __init__(self, database):
        #self.dict = pr_languages.dict_languages
        self.database = database
        self.entity_name = languages.entity_name
        self.entity_primary_key = languages.entity_primary_key
        self.entity_table = DBTable(database, languages.sql_create_languages, is_entity=True)
        self.relation_name = languages.relation_name
        self.relation_table = DBTable(database, languages.sql_create_speaks, is_entity=False)
        self.has_relation = True

    def fill(self, filename, retriever_obj, retriever_type="vectordb",
                            llm='default', print_chunks=False, verbose=True):

        #for field in self.dict :
        prompt_template = languages.prompt_languages
        prompt = PromptTemplate(template=prompt_template, input_variables=['context'])
        llm_output = call_to_llm.get_table_entry(retriever_obj, prompt, self.entity_name,
                                                    retriever_type=retriever_type,
                                                    verbose=verbose, print_chunks=print_chunks,
                                                    llm=llm)
        languages_with_level = eval(llm_output)
        known_languages = self.database.select(columns=self.entity_primary_key,
                                                table=self.entity_name)
        known_languages = [lang[0] for lang in known_languages]
        for lang in languages_with_level:
            language, language_level = lang
            if language not in known_languages:
                self.entity_table.insert(self.entity_primary_key, language)
                known_languages.append(language)
            self.relation_table.insert([self.entity_primary_key,
                                                self.database.candidates.primary_key,
                                                languages.relation_col],
                                       [language, filename, language_level]
                                       )
    # todo: plutôt faire hériter de CVUnits, mais régler le sort du dict avant
    def attributes(self, include_relation=False):
        '''Return columns except for numeric id and foreign key'''
        attrib = self.entity_table.columns(include_primary=False)
        if self.has_relation and include_relation:
            attrib_rel = self.relation_table.columns(include_primary=False)
            attrib.extend([col for col in attrib_rel if col != self.entity_primary_key])
        return attrib
