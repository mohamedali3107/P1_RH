from DBTable import DBTable
import call_to_llm
from prompts import prompt_languages as pr_languages
from langchain.prompts import PromptTemplate

class Languages():

    def __init__(self, database):
        self.dict = pr_languages.dict_languages
        self.database = database
        self.entity_name = 'languages'
        self.entity_primary_key = 'NameLanguage'
        self.relation_name = 'speaks'
        self.entity_table = DBTable(database, f"""CREATE TABLE IF NOT EXISTS {self.entity_name} (
        {self.entity_primary_key} varchar(30) primary key
        );""", is_entity=True)
        self.relation_table = DBTable(database, f"""CREATE TABLE IF NOT EXISTS {self.relation_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        NameLanguage varchar(30),
        Candidate varchar(50),
        FOREIGN KEY (NameLanguage) REFERENCES languages (NameLanguage),
        FOREIGN KEY (Candidate) REFERENCES candidates (FileName),
        LanguageLevel varchar(30)
        );""", is_entity=False)


    def fill(self, filename, retriever_obj, retriever_type="vectordb",
                            llm='default', print_chunks=False, verbose=True):

        for field in self.dict :
            prompt_template = self.dict[field]['prompt']
            prompt = PromptTemplate(template=prompt_template, input_variables=['context'])
            llm_output = call_to_llm.get_table_entry(retriever_obj, prompt, field,
                                                     retriever_type=retriever_type,
                                                     verbose=verbose, print_chunks=print_chunks,
                                                     llm=llm)
            languages_with_level = eval(llm_output)
            
            known_languages = self.database.select(columns=self.entity_primary_key,
                                                   table=self.entity_name)
            known_languages = [lang[0] for lang in known_languages]    # fetchall() returns a list of tuples (Language,)-like
            print("\nKnown languages:", known_languages)
            for lang in languages_with_level:
                language, language_level = lang
                if language not in known_languages:
                    self.entity_table.insert(self.entity_primary_key, language)
                    known_languages.append(language)
                self.relation_table.insert([self.entity_primary_key, 'Candidate', 'LanguageLevel'],
                                           [language, filename, language_level])
                #self.database.execute(f"""INSERT INTO speaks (NameLanguage, Candidate, LanguageLevel) VALUES ('{language}', '{filename}', '{language_level}');""")
