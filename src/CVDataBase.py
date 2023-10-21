import time
import getpass
import mysql.connector
import sql_queries as sql
from Candidates import Candidates
import subprocess
import vectorstore_lib
import loading.load_pdf as load

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

    def list_tables(self):
        self.execute("SHOW TABLES")
        return self.cursor.fetchall()

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
                print(table[0])
                self.execute("DESCRIBE " + table[0])
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

    def add_cv(self, doc, force_refill=False, verbose=True):
        # todo : handle force_refill
        filename = doc.metadata['source']
        if verbose:
            print("\nFilling the database with " + filename +" ...\n")
        known_files = self.select(columns=self.candidates.primary_key, table=self.candidates.name)
        known_files = [file[0] for file in known_files]
        if filename in known_files:
            print("CV already parsed.")
        else:
            vectordb = vectorstore_lib.create_vectordb_single(doc)
            self.candidates.fill(filename, vectordb, retriever_type='vectordb', llm='default', verbose=True)