import sys
sys.path.append("..")
from prompts import prompt_candidates as candidates

prompt_experience = """
You will be provided with a Curriculum Vitae, delimited by triple backsticks. 

Your task is to find and provide the professional experiences (work experience, internship, volunteering experience) of the person in this Curriculum Vitae. 
A professional experience includes dates of employment, the company or organisation name and the job or position title. 

Your output should only be the list of all professional experiences of the person, do not give the description of the tasks performed by the person.

If you did not find an experience, do not mention it in the list. If you cannot find any experience, your output should be "Unknown", not a list.
Do not provide an answer out of the Curriculum Vitae. 

After giving a first answer, try scanning again the Curriculum Vitae to see if you can find other pieces of relevant information that you did not include in your first answer. 
Then, only if you found additional relevant pieces of information, provide a more complete answer.

Try to give the list of professional experiences in the following format:

<FORMAT>
- Job or Position title 1 | Company or Organisation name 1 | Start date 1 - End date 1
- Job or Position title 2 | Company or Organisation name 2 | Start date 2 - End date 2
- Job or Position title 3 | Company or Organisation name 3 | Start date 3 - End date 3
</FORMAT>

Here are some examples of outputs:

<EXAMPLE 1>
- Co-Fondateur et Président | Mistral AI | Septembre 2010 - Aujourd'hui
- Directeur Général Adjoint, en charge de la Branche Intérim | Manpower | Janvier 1999 - Juin 2010
- Directeur RH | Manpower | Janvier 1997 - Janvier 1999
</EXAMPLE 1>

<EXAMPLE 2>
- Data Scientist | Total | Juin 2021 - Today
- Software developer intern | Thalès | Mars 2020 - Avril 2021
</EXAMPLE 2>

Curriculum Vitae : ```{context}```
Professional experience of the person:
"""

table_name = 'experience'
sql_type = "varchar(700)"
config_dict = {'EducationSummary': {'prompt': prompt_experience, 'type': sql_type}}

sql_create = "CREATE TABLE IF NOT EXISTS " + table_name
sql_create += " (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, "
sql_create += ', '.join([col+" "+config_dict[col]['type'] for col in config_dict])
sql_create += f", FileName {candidates.primary_type}, "
sql_create += f"""FOREIGN KEY (FileName) REFERENCES 
                        {candidates.table_name}({candidates.primary_key}) );"""
