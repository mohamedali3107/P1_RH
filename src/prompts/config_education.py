from prompts import prompt_candidates as candidates

prompt_education = """
You will be provided with a Curriculum Vitae, delimited by triple backsticks. 

Your task is to find and provide the educational programs (for instance:  High School, Bachelor, Masters) attended by the person in this Curriculum Vitae. 
An educational program includes dates of attendance, the institution name and the program or degree title. 

Your output should only be the list of all educational programs attended by the person, do not give the description of the program.

If you did not find an educational program, do not mention it in the list. If you cannot find any education, your output should be "Unknown", not a list.
Do not provide an answer out of the Curriculum Vitae. 

After giving a first answer, try scanning again the Curriculum Vitae to see if you can find other pieces of relevant information that you did not include in your first answer. 
Then, only if you found additional relevant pieces of information, provide a more complete answer.

Try to give the list of the educational programs in the following format:
<FORMAT>
- Program or Degree title 1 | Institution name 1 | Start date 1 - End date 1
- Program or Degree title 2 | Institution name 2 | Start date 2 - End date 2
- Program or Degree title 3 | Institution name 3 | Start date 3 - End date 3
</FORMAT>

Here are some examples of outputs:

<EXAMPLE 1>
- Master of Science | Université Paris 6 | Septembre 2017 - Juin 2019
- Licence de Physique | Université Sorbonne | Septembre 2014 - Juillet 2017
- Baccalauréat S | Lycée Pierre-Gilles de Gênes | Juin 2014
</EXAMPLE 1>

<EXAMPLE 2>
- Engineering degree | MIT | October 2020 - April 2023
- Bachelor of Arts | Superior school of Journalism | August 2017 - September 2020
</EXAMPLE 2>

Curriculum Vitae : ```{context}```
Education of the person:
"""

table_name = 'education'
sql_type = "varchar(1000)"
config_dict = {'Summary': {'prompt': prompt_education, 'type': sql_type}}

sql_create = "CREATE TABLE IF NOT EXISTS " + table_name
sql_create += " (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, "
sql_create += ', '.join([col+" "+config_dict[col]['type'] for col in config_dict])
sql_create += f", FileName {candidates.primary_type}, "
sql_create += f"""FOREIGN KEY (FileName) REFERENCES 
                        {candidates.table_name}({candidates.primary_key}) );"""


