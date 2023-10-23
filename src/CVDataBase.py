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
import prompts.prompt_single_cv as prompt_single_cv
import vectorstore_lib
import treat_query
import prompts.prompt_candidates as pr_candidates

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
        self.candidates = None
        self.entities = []  # contains CVUnits

    def execute(self, sql_query: str):
        self.cursor.execute(sql_query)

    def list_tables(self, except_candidates=False):
        self.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        if except_candidates:
            return [table[0] for table in tables if table[0] != self.candidates.name]
        else:
            return [table[0] for table in tables]


    def select(self, columns: list, table: str, condition: str = '') :
        '''Input condition: str that specifies optional ending to the select query (ex: "where...")
        Output: list of tuples of strings'''
        cols_str = ", ".join(columns) if type(columns) == list else str(columns)
        query = f"SELECT {cols_str} FROM {table}" + " " + condition
        self.execute(query)
        return self.cursor.fetchall()

    def initialize(self, verbose: bool = True):
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
        # cursor.execute(sql.create_languages)
        # cursor.execute(sql.create_speaks)
        if verbose:
            tables = self.list_tables()
            print("Database tables :")
            for table in tables:
                print(table)
                self.execute("DESCRIBE " + table)
                columns = self.cursor.fetchall()
                for col in columns:
                    print("   ", col)

    def all_fields(self):
        # todo : implement
        fields = []
        for table in self.tables:
            fields.extend(["table.attributs"])

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
        known_files = self.select(columns=self.candidates.primary_key, table=self.candidates.name)
        known_files = [file[0] for file in known_files]
        if filename in known_files:
            print("CV already parsed.")
            ## recover the candidate's name
            first_name_label, family_name_label = pr_candidates.first_name, pr_candidates.family_name
            name = self.select([first_name_label, family_name_label], 
                               self.candidates.name,
                               f"WHERE {self.candidates.primary_key} = '{filename}'")
            name = name[0][0] + " " + name[0][1]
            self.candidates.candidate_names.append(name)
        else:
            vectordb = vectorstore_lib.create_vectordb_single(doc)
            self.candidates.fill(filename, vectordb, retriever_type='vectordb', llm='default', verbose=True)

    def ask_filtered(self, question, llm='default') :
        if llm == 'default' :
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        # identify filter
        chain_extract_name = LLMChain(llm=llm, prompt=prompt_name_in_query)
        name_approx = chain_extract_name.predict(context=question)
        print('name approx : ', name_approx)
        print('all names : ', self.candidates.candidate_names)
        chain_format_name = LLMChain(llm=llm, prompt=prompt_identify_name)
        name = chain_format_name.predict(context=self.candidates.candidate_names, name=name_approx)
        print('Candidate :', name)
        # identify field
        all_fields = [attribute for attribute in self.candidates.dict]
        all_fields += self.list_tables(except_candidates=True)
        print("all fields : ", all_fields)
        fields = treat_query.extract_target_fields(question, all_fields, llm=llm)
        # retrieve data
        data = []
        for field in fields :
            first, fam = name.split(" ")
            select = self.select(field, self.candidates.name, f"WHERE FirstName = '{first}' AND FamilyName = '{fam}'")
            data.append(select[0][0])
        chain = LLMChain(llm=llm, prompt=prompt_single_cv.prompt_from_field)
        return chain.predict(topic=fields, data=data, question=question)  # lists as inputs