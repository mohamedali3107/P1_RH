import sys
sys.path.append('..')
import time
import getpass
import mysql.connector
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from database_classes.Candidates import Candidates
from database_classes.CVUnit import CVUnit
from database_classes.Languages import Languages
from config_database_mysql import config_experience as experience
from config_database_mysql import config_education as education
from config_database_mysql import config_skills as skills
from config_database_mysql import config_candidates
import prompts.prompt_single_cv as pr_single
from vectorstore_managing import vectorstore_lib
from llm_calling import treat_query

class CVDataBase():

    def __init__(self):
        password = getpass.getpass("Enter your MySQL password: ")
        self.db = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password=password,
                            )
        self.cursor = self.db.cursor()
        self.name = 'candidates_cv'
        self.candidates = None  # Candidates object
        self.entities = {}  # contains CVUnit objects, keys = fields = entity names

    def initialize(self, verbose: bool = True):
        '''Build database and (empty) tables with relevant columns, if they do not already exist'''
        ## Check if the database already exists
        query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{self.name}'"
        self.execute(query)
        if len(self.cursor.fetchall()) == 0:  # a second call to fetchall() would return []
            if verbose:
                print("Creating the database...")
            self.execute("CREATE DATABASE " + self.name)
            self.db.commit()
        self.db.database = self.name
        self.candidates = Candidates(self)  # table creation
        self.entities['languages'] = Languages(self)
        self.entities[education.table_name] = CVUnit(self, education.sql_create,
                                                     education.config_dict)
        self.entities[experience.table_name] = CVUnit(self, experience.sql_create,
                                                      experience.config_dict)
        self.entities[skills.table_name] = CVUnit(self, skills.sql_create,
                                                  skills.config_dict)
        # todo : other calls to other constructors 
        if verbose:
            tables = self.list_tables()
            print("Database tables :")
            for table in tables:
                print(table)
                self.execute("DESCRIBE " + table)
                columns = self.cursor.fetchall()
                for col in columns:
                    print("   ", col)

    def execute(self, sql_query: str):
        self.cursor.execute(sql_query)

    def list_tables(self, except_candidates=False, except_relations=False):
        if not except_candidates and not except_relations:
            self.execute("SHOW TABLES")
            return [table[0] for table in self.cursor.fetchall()]
        tables = [entity.entity_name for entity in self.entities.values()]
        if not except_candidates:
            tables.append(self.candidates.name)
        if not except_relations:
            tables.extend([entity.relation_name for entity in self.entities.values()])
        return tables

    def all_fields(self, fusion=True):
        candidates_attributes = self.candidates.attributes()
        other_fields = self.list_tables(except_candidates=True, except_relations=True)
        if fusion:
            return candidates_attributes + other_fields
        else:
            return candidates_attributes, other_fields

    def select(self, columns: list, table: str, condition: str = '') :
        '''Input condition: str that specifies optional ending to the select query (ex: "where...")
        Output: list of tuples of strings'''
        cols_str = ", ".join(columns) if type(columns) == list else columns
        query = f"SELECT {cols_str} FROM {table}" + " " + condition
        self.execute(query)
        return self.cursor.fetchall()

    def fill_all_cv(self, docs, force_refill=False, verbose=True):
        t0 = time.time()
        for doc in docs:
            try:
                self.add_cv(doc, force_refill=force_refill, verbose=verbose)
            except Exception as e:
                print("Error filling the database for " + doc.metadata['source'])
                print(e)
        if verbose:
            print("Time to fill the database with new CVs : {:.2f}s".format(time.time()-t0))
            print("Names : ", self.candidates.candidates_names)

    def add_cv(self, doc, force_refill=False, verbose=True):
        # todo : handle force_refill
        filename = doc.metadata['source']
        if verbose:
            print("\nFilling the database with " + filename +" ...\n")
        ## names of files already in the database (but not yet recorded in the CVDataBase object):
        known_files = self.select(columns=self.candidates.primary_key, table=self.candidates.name)
        known_files = [file[0] for file in known_files]
        if filename in known_files:
            print("CV already parsed.")
            ## recover the candidate's name
            if filename not in self.candidates.files_names:
                first_name_label = config_candidates.first_name
                family_name_label = config_candidates.family_name
                name = self.select([first_name_label, family_name_label], 
                                    self.candidates.name,
                                    f"WHERE {self.candidates.primary_key} = '{filename}'")
                name = name[0][0] + " " + name[0][1]
                self.candidates.files_names[filename] = name
        else:
            vectordb = vectorstore_lib.create_vectordb_single(doc)
            self.candidates.fill(filename, vectordb, retriever_type='vectordb',
                                 llm='default', verbose=True)
            for entity in self.entities:
                self.entities[entity].fill(filename, vectordb, 
                                           retriever_type="vectordb", llm='default', verbose=True)

    def outputs_for_each_cv(self, question: str, fields_dict: dict, 
                                        chain='default', llm='default', verbose=False):
        '''Ask a question separately on each CV and return dictionary of outputs
        Input fields_dict specifies wether the fields are part of the candidates's attributes
        (value = True) or involve other tables (False) (None if unknown)
        '''
        outputs = {}
        for name in self.candidates.candidates_names():
            output = self.ask_targeted(question, fields_dict=fields_dict, name=name,
                                       llm=llm, chain=chain, verbose=verbose)
            outputs[name] = output
        return outputs

    def ask_targeted(self, question: str, fields_dict: dict = {}, name: str = '',
                                    llm='default', chain='default', verbose=True):
        '''Return LLM's answer to a question on a targeted CV as a string
        Targeted candidate/CV should appear either in question or as filename optional argument.
        '''
        if llm == 'default':
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        if chain == 'default':
            chain = LLMChain(llm=llm, prompt=pr_single.prompt_from_field)
        if not name:
            # identify filter on names
            name = treat_query.target_name(question, self.candidates.candidates_names(), 
                                           llm=llm, verbose=verbose)
        filename = self.candidates.related_file(name)  # todo: case of homonym candidates
        if fields_dict == {}:
            fields_dict = self.target_fields_as_dict(question, verbose=False)
        # retrieve data
        data = []
        for field in fields_dict:
            if fields_dict[field] == 'attribute':
                select = self.select(field, self.candidates.name, 
                                     "WHERE " + self.candidates.primary_key + f" = '{filename}'")
                data.append("<" + field + ">  " + select[0][0])
            elif fields_dict[field] == 'other':
                entity = self.entities[field]
                piece = "<" + field + "> "
                if entity.has_relation:
                    cols = entity.attributes(include_relation=True)  # no int primary key nor FileName
                    cols = [col for col in cols if col != self.candidates.primary_key]
                    cols_str = ", ".join([col for col in cols])
                    self.execute(f"""SELECT {cols_str} FROM (SELECT * FROM {entity.entity_name}
                                            NATURAL JOIN {entity.relation_name}) AS TEMP
                                            WHERE {self.candidates.primary_key} = '{filename}';""")
                    select = self.cursor.fetchall()
                else:
                    cols = entity.attributes()
                    cols = [col for col in cols if col != self.candidates.primary_key]
                    select = self.select(cols, entity.entity_name,
                                            "WHERE " + self.candidates.primary_key + f" = '{filename}'")
                for output in select:
                    piece += "\n " + " - ".join([cols[i] + ": " + str(output[i]) for i in range(len(cols))]) + " ;\n"
                data.append(piece)
            # todo: else ask unsupervised query (llm based)
        chain = LLMChain(llm=llm, prompt=pr_single.prompt_from_field)
        return chain.predict(topic=list(fields_dict.keys()), data=data, question=question)
    
    def ask_transverse(self, query_multi: str, fields_dict: dict, chain='default',
                                    llm='default', verbose=True):
        operation = treat_query.detect_operation_from_query(query_multi, llm=llm, verbose=verbose)
        if operation == 'Condition' or operation == 'Comparison':  # Comparison is actually useless
            mono_query = treat_query.multi_to_mono(query_multi)
            outputs = self.outputs_for_each_cv(mono_query, fields_dict, chain=chain,
                                               llm=llm, verbose=verbose)
            selected_candidates = [name for name in outputs if outputs[name] == 'Yes']
            if selected_candidates == [] :
                print('No candidates seem to meet the condition.')
            return ", ".join(selected_candidates)
        elif operation == 'All' :
            mono_query = treat_query.multi_to_mono(query_multi)
            outputs = self.outputs_for_each_cv(mono_query, fields_dict, chain=chain,
                                               llm=llm, verbose=verbose)
            global_output = ""
            for name in outputs:
                global_output += name + ' : ' + outputs[name] + '\n'
            return global_output
        else :
            print('Type of tranversal question not supported yet')
            return ''
        
    def target_fields_as_dict(self, query, llm='default', verbose=True):
        candidate_attributes, other_fields = self.all_fields(fusion=False)
        if verbose:
            print("All possible fields : ", *candidate_attributes, *other_fields)
        try:
            fields = treat_query.extract_target_fields(query, 
                                                       candidate_attributes+other_fields,
                                                       llm=llm, verbose=verbose)
        except Exception as err :
            print(*err.args)
            fields = ['unknown']  # todo : plutôt [] mais à gérer dans fonctions appelées
        fields_involved = {}
        for field in fields:
            if field in candidate_attributes:
                fields_involved[field] = 'attribute'
            elif field in other_fields:
                fields_involved[field] = 'other'
            else:
                fields_involved[field] = 'unknown'
                # todo: raise Exception
        return fields_involved
        
    def ask_question(self, query: str, chain='default', llm='default', verbose=True) :
        '''Identify type of query, then call auxiliary depending on type'''
        fields_dict = self.target_fields_as_dict(query, llm=llm, verbose=verbose)
        try:
            mode = treat_query.detect_query_mode(query, llm=llm, verbose=verbose)
        except Exception as err:
            print(*err.args)
            mode = 'unknown'
        if mode == 'transverse':
            return self.ask_transverse(query, fields_dict, chain=chain,
                                       llm=llm, verbose=verbose)
        elif mode == 'single':
            # todo : exceptions
            return self.ask_targeted(query, fields_dict, llm=llm, verbose=verbose)
        else:
            return('Mode transverse/single unclear')