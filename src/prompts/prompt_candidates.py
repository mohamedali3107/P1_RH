dict = {"Gender": """You will be provided with a Curriculum Vitae delimited by triple backsticks.
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
""",
"FirstName": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the first name of the person in this Curriculum Vitae.
Your output should be only the first name of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
"FamilyName": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the last name of the person in this Curriculum Vitae.
Your output should be only the last name of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
"Email": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the email address of the person in this Curriculum Vitae.s
Your output should be only the email address of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
"PhoneNumber": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the phone number of the person in this Curriculum Vitae.
Your output should be only the phone number of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".


Curriculum Vitae : ```{context}```
""",
"LinkedIn": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the LinkedIn ID of the person in this Curriculum Vitae.
Your output should be only the LinkedIn ID of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".


Curriculum Vitae : ```{context}```
""",
"Webpage": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the personal webpage URL of the person in this Curriculum Vitae.
Your output should be only the personal webpage URL of the person, do not make a sentence.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
"Country": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the country of residence of the person in this Curriculum Vitae.
Your output should be only the country, do not make a sentence. Do not provide a reasoning.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
"City": """ You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the city of residence of the person in this Curriculum Vitae.
Your output should be only one city, do not make a sentence. Do not provide a reasoning.
Do not provide answer out of the Curriculum Vitae. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
"""
}