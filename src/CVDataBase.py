import time
import getpass
import subprocess
import mysql.connector
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import sql_queries as sql
from Candidates import Candidates
from prompts.prompt_extract_names import prompt_name_in_query
from prompts.prompt_format_name import prompt_identify_name
import prompts.prompt_single_cv as pr_single
import vectorstore_lib
import treat_query
import prompts.prompt_candidates as pr_candidates
import manage_transversal_query

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

    def list_tables(self, except_candidates=False):
        self.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        if except_candidates:
            return [table[0] for table in tables if table[0] != self.candidates.name]
        else:
            return [table[0] for table in tables]

    def all_fields(self, fusion=True):
        candidates_attributes = self.candidates.attributes()
        other_fields = self.list_tables(except_candidates=True)
        if fusion:
            return candidates_attributes + other_fields
        else:
            return candidates_attributes, other_fields

    def select(self, columns: list, table: str, condition: str = '') :
        '''Input condition: str that specifies optional ending to the select query (ex: "where...")
        Output: list of tuples of strings'''
        cols_str = ", ".join(columns) if type(columns) == list else str(columns)
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
            print("Names : ", self.candidates.candidate_names)

    def add_cv(self, doc, force_refill=False, verbose=True):
        # todo : handle force_refill
        filename = doc.metadata['source']
        if verbose:
            print("\nFilling the database with " + filename +" ...\n")
        ## names of files already in the database (but not yet recorded in the CVDataBase object) :
        known_files = self.select(columns=self.candidates.primary_key, table=self.candidates.name)
        known_files = [file[0] for file in known_files]
        if filename in known_files:
            print("CV already parsed.")
            ## recover the candidate's name
            if filename not in self.candidates.files_names:
                first_name_label, family_name_label = pr_candidates.first_name, pr_candidates.family_name
                name = self.select([first_name_label, family_name_label], 
                                    self.candidates.name,
                                    f"WHERE {self.candidates.primary_key} = '{filename}'")
                name = name[0][0] + " " + name[0][1]
                self.candidates.files_names[filename] = name
        else:
            vectordb = vectorstore_lib.create_vectordb_single(doc)
            self.candidates.fill(filename, vectordb, retriever_type='vectordb', llm='default', verbose=True)

    def outputs_for_each_cv(self, question: str, chain='default', llm='default', verbose=False):
        '''Ask a question separately on each CV and return dictionary of outputs'''
        outputs = {}
        # todo : exception
        for filename in self.candidates.filenames():
            output = self.ask_filtered(question, llm=llm, chain=chain, verbose=verbose)
            outputs[filename] = output
        return outputs

    def ask_filtered(self, question: str, llm='default', chain='default', verbose=True):
        if llm == 'default':
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        if chain == 'default':
            chain = LLMChain(llm=llm, prompt=pr_single.prompt_from_field)
        # identify filter
        name = treat_query.target_name(question, self.candidates.candidates_names(), 
                                       llm=llm, verbose=verbose)
        if verbose: print('Candidate :', name)
        filename = self.candidates.related_file(name)
        # identify field
        candidates_attributes, other_fields = self.all_fields(fusion=False)
        all_fields = candidates_attributes + other_fields
        if verbose: print("All possible fields : ", all_fields)
        fields = treat_query.extract_target_fields(question, all_fields, llm=llm)
        # retrieve data
        data = []
        for field in fields:
            if field in candidates_attributes:
                select = self.select(field, self.candidates.name, 
                                     f"WHERE " + self.candidates.primary_key + " = '{filename}'")
                data.append(select[0][0])
            # todo : else (other_fields, ie. ask other tables)
        chain = LLMChain(llm=llm, prompt=pr_single.prompt_from_field)
        return chain.predict(topic=fields, data=data, question=question)  # lists as inputs
    
    # def ask_question_multi(self, query_multi: str, chain='default', llm='default') :
    #     all_fields = self.all_fields()
    #     try :
    #         fields_involved = treat_query.extract_target_fields(query_multi, all_fields, llm=llm)
    #     except Exception as err :
    #         print(*err.args)
    #         fields_involved = ['unknown']  # todo : plutôt [] mais à gérer dans fonctions appelées
    #     operation = treat_query.detect_operation_from_query(query_multi, llm=llm)
    #     if operation == 'Condition' or operation == 'Comparison' :  # Comparison is actually useless
    #         mono_query = treat_query.multi_to_mono(query_multi)
    #         outputs = manage_transversal_query.outputs_from_dict(dict_db, mono_query, fields_involved, chain=chain, llm=llm)
    #         selected_candidates = []
    #         for meta in outputs :
    #             if outputs[meta] == 'Yes' :
    #                 selected_candidates.append(meta)
    #         if selected_candidates == [] :
    #             print('No candidates seem to meet the condition.')
    #         return ", ".join(selected_candidates)
    #     elif operation == 'All' :
    #         mono_query = treat_query.multi_to_mono(query_multi)
    #         outputs = manage_transversal_query.outputs_from_dict(dict_db, mono_query, fields_involved, chain=chain, llm=llm)
    #         global_output = ""
    #         for meta in outputs :
    #             global_output += meta + ' : ' + outputs[meta] + '\n'
    #         return global_output
    #     else :
    #         print('Type of tranversal question not supported yet')
    #         return ''