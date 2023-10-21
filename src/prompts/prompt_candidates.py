
sql_gender = " varchar(20)"
prompt_gender = """You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the gender identity of the person in this Curriculum Vitae.
You may specify the gender identity of the person by relying on the person's first name.
Your output should be only the gender identity of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".
 
 <EXAMPLES>
If the first name is John:
Male
 
If the first name is Mary:
Female
 
 If the first name is Jeanne:
Female
 
 If the first name is Frédéric:
Male
 
 If the first name is Julia:
Female
 </EXAMPLES>

Curriculum Vitae : ```{context}```
"""

sql_first = " varchar(40)"
prompt_first = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the first name of the person in this Curriculum Vitae.
Your output should be only the first name of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

sql_family = " varchar(40)"
prompt_family = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the last name of the person in this Curriculum Vitae.
Your output should be only the last name of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

sql_email = " varchar(40)"
prompt_email = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the email address of the person in this Curriculum Vitae.s
Your output should be only the email address of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

sql_phone = " varchar(25)"
prompt_phone = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the phone number of the person in this Curriculum Vitae.
Your output should be only the phone number of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

sql_linkedin = " varchar(50)"
prompt_linkedin = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the LinkedIn ID of the person in this Curriculum Vitae.
Your output should be only the LinkedIn ID of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

sql_webpage = " varchar(50)"
prompt_webpage = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the personal webpage URL of the person in this Curriculum Vitae.
Your output should be only the personal webpage URL of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

sql_country = " varchar(30)"
prompt_country = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the country of residence of the person in this Curriculum Vitae.
Your output should be only the country, do not make a sentence. Do not provide a reasoning.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

sql_city = " varchar(30)"
prompt_city = """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the city of residence of the person in this Curriculum Vitae.
Your output should be only one city, do not make a sentence. Do not provide a reasoning.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""

dict_candidates = {
        #"FileName": {'prompt': None, 'type': 'varchar(50) primary key'},
        "Gender": {'prompt': prompt_gender, 'type': sql_gender},
        "FirstName": {'prompt': prompt_first, 'type': sql_family},
        "FamilyName": {'prompt': prompt_family, 'type': sql_family},
        "Email": {'prompt': prompt_email, 'type': sql_email},
        "PhoneNumber": {'prompt': prompt_phone, 'type': sql_phone},
        "LinkedIn": {'prompt': prompt_linkedin, 'type': sql_linkedin},
        "Webpage": {'prompt': prompt_webpage, 'type': sql_webpage},
        "Country": {'prompt': prompt_country, 'type': sql_country},
        "City": {'prompt': prompt_city, 'type': sql_city}
        }
primary_key = "FileName"

table_name = "candidates"
sql_query = "CREATE TABLE IF NOT EXISTS " + table_name + " ( "
sql_query += primary_key + " varchar(50) primary key, "
sql_query += ', '.join([field+dict_candidates[field]['type'] for field in dict_candidates])
sql_query += ');'

# sql_query = """
# CREATE TABLE IF NOT EXISTS candidates (
# FileName varchar(50) primary key,
# FirstName varchar(40),
# FamilyName varchar(40),
# Gender varchar(20),
# Email varchar(30),
# PhoneNumber varchar(25),
# LinkedIn varchar(40),
# Webpage varchar(40),
# Country varchar(30),
# City varchar(30)
# );
# """
