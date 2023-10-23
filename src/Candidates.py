from CVUnit import CVUnit
from DBTable import DBTable
from sql_queries import create_candidates
from prompts import prompt_candidates as pr_candidates
import treat_chunks
import vectorstore_lib
import call_to_llm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

class Candidates() :
    
    def __init__(self, database):
        self.dict = pr_candidates.dict_candidates  # could/should be a class attribute (or just a global)
        self.database = database
        self.candidate_names = []
        self.primary_key = pr_candidates.primary_key  # 'FileName'
        self.table = DBTable(database, sql_query=pr_candidates.sql_query, is_entity=True)
        self.name = self.table.name  # 'candidates'

    def fill(self, filename, retriever_obj, retriever_type="vectordb", llm='default', verbose=True):
        if llm == 'default':
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        columns, values = [pr_candidates.primary_key], [filename]
        name = []
        for field in self.dict :
            prompt_template = self.dict[field]['prompt']
            prompt = PromptTemplate(template=prompt_template, input_variables=['context'])
            chain = call_to_llm.create_chain(llm, prompt)   # call_to_llm un peu useless

            ## Retrieving and calling the LLM
            sources = vectorstore_lib.retrieving(retriever_obj, field, retriever_type=retriever_type, with_scores=True)
            context = treat_chunks.create_context_from_chunks(sources)
            answer = chain.predict(context=context)
            if verbose:
                print(f"Filling the {field} information... Here are the retrieved chunks with scores: \n\n")
                treat_chunks.print_chunks(sources)
                print(answer, "\n")
            if field == pr_candidates.first_name :
                name = [answer] + name
            if field == pr_candidates.family_name :
                name = name + [answer]

            columns.append(field)
            values.append(answer)
        name = " ".join(name)
        print("NAME : ", name)
        if name not in self.candidate_names :
            self.candidate_names.append(name)
        self.table.insert(columns, values)

    def attributes(self):
        return self.table.columns()
