
import pandas as pd

template_path = "data_template_concise.csv"
template_df = pd.read_csv(template_path)
fields = list(template_df)

# # Prompt asking to fill directly a template
# prompt_global = """ The texts provided to you are the resumes of the candidates.
# Your task is to answer the user question in a structured way as in the following format.

# <Desired format>

# Please extract the first name in the resume
# First name:
# Please extract the last name in the resume
# Last name:
# Please extract the phone number in the resume
# Phone number:
# Please extract the email contact in the resume
# Email adress:
# Please extract the language skills mentioned in the resume
# Languages :
# Please extract the technical skills mentioned in the resume
# Technical skills:
# Please extract the last experience of the candidate
# Last experience:

# </Desired format>

# Take your time to read carrefuly the pieces in the context to answer the question.
# Do not provide answer out of the context pieces.
# If you don't know the answer, you should output "Unknown".

# Keep the answer as concise as possible. 

# Always say "thanks for asking!" at the end of the answer.
# {context}
# """

# ## Prompt for retrieving the last position of the candidate
# prompt_last_position = """ You are an AI assistant who loves to help people!

# The texts provided to you are the resumes of the candidates.

# Your task is to provide the details about the most recent position of the candidate in the given context

# Your answer maybe the job title of the candidate, company/organization name, dates of employment

# Take your time to read carefully the pieces in the context to provide the request field.

# Do not provide answer out of the context pieces.

# If you don't know the answer, you should output "Unknown".

# Always say "thanks for asking!" at the end of the answer.

# {context}

# Question: {query}

# Answer the question in the language of the question

# Helpful Answer:
# """

prompts_concise_v0 = [[""] +              # Avoiding the first field (=filename)
[f"""You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the {field} of the person in this CV.
Your output should be only the {field}, do not make a sentence.
Do not provide answer out of the context pieces. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{{context}}```
{field} of the person :
"""
for field in fields[1:]] # Avoiding the first field (=filename)
]

prompts_concise_v1 = [[""] +              # Avoiding the first field (=filename)
[""" You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to provide the gender identity of the candidate in the given context
You may specify the gender identity of the candidate by relying on the candidate's first name.
Your output should be only the gender identity of the candidate, do not make a sentence.
Do not provide answer out of the context pieces. If you did not find it, you should output "Unknown".
 
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
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate First Name mentioned in the resumes.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate Last Name mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate's email adress mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate Phone Number mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, you should output "Unknown".


Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate's personal webpage URL mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resume of the candidates.
Your task is to retrieve the candidate's Country of Residence. Do not provide a reasoning.
Your output should be only one Country. Do not make a sentence.
Do not provide answer out of the context pieces.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide to extract the City of Residence of the candidate.
Take your time to read carefully the pieces in the context to retrieve the requested field.
Your output should be only one City. Do not make a sentence.
Do not provide answer out of the context pieces.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide first language spoken by the candidate from the given context. 
Your output should be only the language, do not make a sentence.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide proficiency level of the first language spoken by the candidate from the given context.
Your output should be only the proficiency level, do not make a sentence.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, you should output "Unknown".

<EXAMPLES>
Native
Fluent 
Intermediate
Basic
</EXAMPLES>

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide second language spoken by the candidate from the given context.
Your output should be only the language, do not make a sentence.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide proficiency level of the second language spoken by the candidate from the given context.
Your output should be only the proficiency level, do not make a sentence.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, you should output "Unknown".

<EXAMPLES>
Native
Fluent 
Intermediate
Basic
</EXAMPLES>

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide a comprehensive list of the technical skills of the candidate. Do not specify the technologies, frameworks and programming languages used.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, you should output "Unknown".

<EXAMPLES OF OUTPUTS>
- Coding, Data Science, Optimization, Signal Processing.
- Mathematics, programming, teaching.
</EXAMPLES OF OUTPUTS>

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide a comprehensive list of the candidate's programming skills that are in high demand in the software development industry. 
You may include languages, frameworks, libraries, and technologies.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, you should output "Unknown".

<EXAMPLES OF OUTPUTS>
- Python, Java, C++, Matlab
- Julia, Matlab, SQL, MongoDB.
</EXAMPLES OF OUTPUTS>

Curriculum Vitae : ```{context}```
""",
"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the highest degree of the candidate in the given context.
Your output should be only the highest degree title of the candidate, do not make a sentence. Do not mention the institution. 
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, you should output "Unknown".

<EXAMPLES>
PhD
Msc
Master of Engineering
Bachelor
</EXAMPLES>

Curriculum Vitae : ```{context}```
""",
"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the most current work position of the candidate in the given context.
Your answer should include, if you can find it, the job title of the candidate, company or organization name and dates of employment.
Your output should be only the current work position of the candidate, do not make a sentence.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the previous work position of the candidate in the given context.
Your answer should include, if you can find it, the job title of the candidate, company or organization name and dates of employment.
Your output should be only the previous work position of the candidate, do not make a sentence.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, you should output "Unknown".

Curriculum Vitae : ```{context}```
""",
""" You will be provided with a Curriculum Vitae, delimited by triple backsticks. 
This Curriculum Vitae contains professional experiences which might be described by a date, a company or organisation name and a job or position title.
Your task is to find and provide the list of all professional experiences of the person in this Curriculum Vitae.
If you did not find an experience, do not mention it in the list. If you cannot find any experience, your output should be "Unknown", not a list.
Do not provide an answer out of the Curriculum Vitae. 

Curriculum Vitae : ```{context}```
Professional experience of the person:
"""
,
"""
You will be provided with a Curriculum Vitae, delimited by triple backsticks. 
This Curriculum Vitae contains the education of the person, each item of which might be described by a date, a institution name and the title of the program or the degree.
Your task is to find the education of the person in this Curriculum Vitae and provide under a list format.
If you did not find an experience, do not mention it in the list. If you cannot find any experience, your output should be "Unknown", not a list.
Do not provide an answer out of the Curriculum Vitae. 

Curriculum Vitae : ```{context}```
Professional experience of the person:
"""]
]

# """Your task is to help a recruiter get the information they need from the provided CV of a candidate.
# The CV will be delimited by triple backsticks.
# All the information from the CV is about one individual who is the candidate.

# <FORMAT>
# - Job title 1 | Company or Organisation name 1 | Start date 1 - End date 1
# - Job title 2 | Company or Organisation name 2 | Start date 2 - End date 2
# - Job title 3 | Company or Organisation name 3 | Start date 3 - End date 3
# </FORMAT>
# If no end date is specified, remplace the end date by 'today'.

# Do not provide answer out of the context pieces.
# After giving a first answer, try scanning again the document to see if you can find other pieces of relevant information that you did not include in your first answer. 
# Then, only if you found additional relevant pieces of information, provide a more complete answer.
# If you don't know the answer, you should output "Unknown".

# <EXAMPLE 1>
# - Co-Fondateur et Président | Mistral AI | Septembre 2010 - Aujourd'hui
# - Directeur Général Adjoint, en charge de la Branche Intérim | Manpower | Janvier 1999 - Juin 2010
# - Directeur RH | Manpower | Janvier 1997 - Janvier 1999
# </EXAMPLE 1>

# <EXAMPLE 2>
# - Data Scientist | Total | Juin 2021 - Today
# - Software developer | Thalès | Mars 2014 - Avril 2021
# </EXAMPLE 2>

# <CV> : ```{context}```
# """

prompts_df_concise = pd.DataFrame(data=prompts_concise_v1, columns=fields)
prompts_df_concise.to_csv("prompt_templates_concise.csv", index=False)