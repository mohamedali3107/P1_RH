
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
# If you don't know the answer, just say that you don't know, don't try to make up an answer.

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

# If you don't know the answer, just say that you don't know, don't try to make up an answer.

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
[""" You are an AI assistant who loves to help people! The texts provided to you are the resume of the candidates.
Your task is to provide the gender identity of the candidate  in the given context
You may specify the Gender identity of the candidate by relying on the candidate first name.
For example "John" for male or "Mary" for female.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.


Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate First Name mentioned in the resumes.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate Last Name mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate's email adress mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate Phone Number mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! Your are provided with the resumes of the candidates.
Your task is to retrieve the candidate's personal webpage URL mentioned in the resume.
Take your time to read carefully the pieces in the provided context to get the right answer.
Do not provide answer out of the context pieces. Just provide the answer without making a sentence.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resume of the candidates.
Your task is to retrieve candidate Country of Residence. Do not provide a reasoning.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide to extract the City of Residence of the candidate.
Take your time to read carefully the pieces in the context to retrieve the requested field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide first language spoken by the candidate from the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide proficiency level of the first language spoken by the candidate from the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide second language spoken by the candidate from the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide proficiency level of the second language spoken by the candidate from the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces and do not make a reasoning.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide a comprehensive list of the technical skills of the candidate, along with a brief description for each in the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
""" You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide a comprehensive list of the programming skills of the candidate, along with a brief description for each in the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the highest degree of the candidate in the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the most current work position of the candidate in the given context.
Your answer may be the job title of the candidate, company or organization name, dates of employment.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",

"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the previous work position of the candidate in the given context.
Your answer may be the job title of the candidate, company or organization name, dates of employment.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the details about the professional experience of the candidate in the given context.
Your answer maybe the job title of the candidate, company/organization name, dates of employment.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
""",
"""  You are an AI assistant who loves to help people! The texts provided to you are the resumes of the candidates.
Your task is to provide the details about the education of the candidate in the given context.
Take your time to read carefully the pieces in the context to provide the request field.
Do not provide answer out of the context pieces.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Curriculum Vitae : ```{context}```
"""]
]

prompts_df_concise = pd.DataFrame(data=prompts_concise_v1, columns=fields)
prompts_df_concise.to_csv("prompt_templates_concise.csv", index=False)