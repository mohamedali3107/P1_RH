import sys
sys.path.append("..")
from config_database_mysql import config_candidates as candidates

prompt_skills = """
 You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find the technical skills of the person in the Curriculum Vitae and provide a comprehensive list of those skills. You should not specify any of the technologies, frameworks and programming languages used.
Your output should be only the list of technical skills, do not make a sentence.
Do not provide answer out of the Curriculum Vitae.
If you don't know the answer, you should output "Unknown".

<EXAMPLE 1>
Coding, Data Science, Optimization, Signal Processing.
</EXAMPLE 1>

<EXAMPLE 2>
Mathematics, programming, teaching.
</EXAMPLE 2>

Curriculum Vitae : ```{context}```
"""

table_name = 'skills'
sql_type = "varchar(700)"
config_dict = {'Summary': {'prompt': prompt_skills, 'type': sql_type}}

sql_create = "CREATE TABLE IF NOT EXISTS " + table_name
sql_create += " (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, "
sql_create += ', '.join([col+" "+config_dict[col]['type'] for col in config_dict])
sql_create += f", FileName {candidates.primary_type}, "
sql_create += f"""FOREIGN KEY (FileName) REFERENCES 
                        {candidates.table_name}({candidates.primary_key}) );"""